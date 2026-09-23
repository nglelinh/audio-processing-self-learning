---
layout: post
title: "05-02 AudioWorklet and audio callbacks"
chapter: "05"
order: 2
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter05
lesson_type: required
draft: false
---

Browser audio is rendered on a real-time thread. **AudioWorklet** is the API that puts your code on that thread: `audioWorklet.addModule`, then an `AudioWorkletNode`, then `process(inputs, outputs, parameters)` once per render quantum. The quantum is often **128 samples**. At 48 kHz that is $$128/48000\approx 2.67$$ ms. Inside `process` you may not allocate, take a lock, or touch the network. `console.log` does all three kinds of harm and is not how you debug a dropout.

![AudioWorklet quantum as a wall-time budget next to RTF]({{ site.imgurl }}/generated/rtf-audioworklet.png)

*Figure. Each callback owns a short block — commonly 128 samples, about 2.67 ms at 48 kHz — and must return before the next one. RTF is measured on whatever block you chose to time (one quantum, or one 10 ms model hop gathered from several quanta). The picture is the deadline, not a license to run a DeepFilterNet forward pass inside a single `process` call.*

## Learning objectives

You will trace the AudioWorklet lifecycle, write a `process` that copies input to output when a bypass flag is set, explain why `console.log` is illegal on that thread, and place a 480-sample DeepFilterNet hop across several 128-sample quanta without assuming the counts divide.

## 60-minute teaching plan

- **0–10 min** — Why the main thread cannot own the microphone callback.
- **10–25 min** — Lifecycle, the 128-sample quantum, `return true`.
- **25–40 min** — Bypass copy, and the ban on allocate / lock / network.
- **40–50 min** — Where a DF3 ONNX graph is allowed to run.
- **50–60 min** — Mini-lab (pseudocode is enough), exercises.

## Core explanation

### Lifecycle

1. On the main thread, `audioContext.audioWorklet.addModule('ns-processor.js')` loads the processor script. This is where compilation belongs. It is not inside `process`.
2. `new AudioWorkletNode(audioContext, 'ns-processor', options)` constructs the node. `options.processorOptions` can pass hop size and channel count once.
3. Connect `source → nsNode → destination`, or into the WebRTC track path (Chapter 07).
4. The browser calls `process` on the **audio rendering thread**, once per quantum, for the life of the node. MDN’s AudioWorklet page is the spec-facing reference: [developer.mozilla.org/en-US/docs/Web/API/AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet).

`registerProcessor('ns-processor', NsProcessor)` runs when the module loads, on the audio thread’s setup, not per buffer. Returning `true` from `process` keeps the node alive. Returning `false` allows the browser to collect it, which sounds like the suppressor vanished mid-call.

### The bypass contract

```js
class NsProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.bypass = true; // model not ready: copy, do not block
    this.port.onmessage = (event) => {
      // Control messages are delivered between callbacks, not during them.
      if (event.data.type === "setBypass") this.bypass = event.data.value;
    };
  }

  process(inputs, outputs) {
    const input = inputs[0] && inputs[0][0];
    const output = outputs[0] && outputs[0][0];
    if (!input || !output) return true;
    if (this.bypass) {
      // output already exists. set() copies bytes; it does not allocate the buffer.
      output.set(input);
      return true;
    }
    // Enhancement would use only preallocated scratch and a ready model.
    output.set(input);
    return true;
  }
}
registerProcessor("ns-processor", NsProcessor);
```

When `bypass` is set, the listener hears the microphone, delayed by the graph, with no suppressor. That is the correct behavior while WASM is compiling or while the previous hop missed its deadline (lesson 05-03). `output.set(input)` requires equal lengths. A quantum of 128 into a leftover buffer of a different size throws, and an exception inside `process` kills the node. Check `input.length` before the copy.

`deepfilternet3-noise-filter` uses the same shape: ONNX/WASM in an AudioWorklet, `DeepFilterNoiseFilterProcessor`, `DeepFilterNet3Core`, suppression 0–100 via `setSuppressionLevel`. It is not bit-exact with the `deepFilter` CLI, and the bypass above is teaching code, not that package.

### Why `console.log` is illegal in `process`

The rendering thread has a hard deadline of about 2.67 ms for a 128-sample quantum at 48 kHz. Three rules follow, and `console.log` breaks them:

- **No allocation.** Formatting a log line builds a string. A string is a heap allocation. Allocation can trigger garbage collection, and a GC pause of a few milliseconds is already larger than the quantum.
- **No lock.** Delivering the line to the console or to DevTools crosses to another thread and can wait on a mutex. `Atomics.wait` and any synchronous IPC are the same class of bug.
- **No network.** A log sink that posts to a remote debugger or a telemetry endpoint waits on I/O. The audio device does not.

The same ban covers `fetch`, `JSON.parse` of a weight file, `new Float32Array` every callback, compiling WASM, and blocking on a mutex held by the main thread. Control changes (bypass, suppression, a “model ready” bit) arrive as small messages on `MessagePort`, applied between quanta. Weights load on the main thread or a worker before the node leaves bypass.

A Node.js script that imports `wrtc` or a WASM build is optional practice. It is not required to pass this lab. The pass condition is the pseudocode and the explanation above.

### Quantum versus hop

The published hop is 10 ms, **480 samples** at 48 kHz (04-02, 04-03). $$480/128=3.75$$. Three callbacks hold 384 samples, four hold 512. Append into a ring (05-03) until 480 are present, run one hop, and slice the overlap-add output back into 128-sample quanta. Assuming `input.length === 480` drops or repeats audio.

`sampleRate` is in scope in the worklet. Read it. At 44.1 kHz the same 128 samples last $$128/44100\approx 2.90$$ ms, and a 480-sample hop is the wrong length for a 48 kHz model. CoreAudio, WASAPI, and AAudio use the same rule under other names: finish before the next period, and bypass when the model is late.

## Pitfalls

- Debugging dropouts with `console.log` and making them worse.
- `new Float32Array(128)` inside `process`.
- Hard-coding 48000 instead of reading `sampleRate`.
- Structured-cloning a full PCM buffer to the main thread every quantum. Use a SharedArrayBuffer ring if you must leave the thread, and measure the copies.
- Running ScriptProcessorNode, which pulls audio back onto the main thread.

## Mini-lab

**Goal.** Implement the bypass copy as plain pseudocode in Python so the lab has no browser and no Node dependency. The AudioWorklet version is the block in the lesson; a Node harness is optional and is not required to pass.

```bash
python3 - << 'PY'
def process(frame, bypass, output):
    """Copy input to the caller-provided output when bypass is set.
    console.log is illegal: it allocates a string, can lock against
    the console thread, and may touch the network. Do none of that here.
    """
    if bypass:
        for i, sample in enumerate(frame):
            output[i] = sample
        return True
    for i, sample in enumerate(frame):
        output[i] = sample  # enhancement would write here, still no allocation
    return True

frame = [0.1, -0.2, 0.3, -0.4]
out = [0.0] * 4
alive = process(frame, bypass=True, output=out)
print(alive, out)
PY
```

**Expected**. `True [0.1, -0.2, 0.3, -0.4]`. The output buffer object is the one the caller allocated. Nothing in `process` constructs a list, prints, or waits.

**Failure modes**. Allocating `out = frame.copy()` inside the function and calling it real-time safe. Inserting a print “just for the lab” and leaving it in the worklet. Requiring `npm install` or a running browser for a pass. Treating a successful copy as evidence that the DF3 graph meets the 2.67 ms budget — the copy is a few loads and stores, the graph is not.

## Exercises

1. **Deadline.** 256-sample quantum, 48 kHz. How many milliseconds do you have? At 44.1 kHz?
2. **Gather.** You need 480 samples and each `process` gives 128. After how many callbacks do you first hold a full hop, and how many samples are left over?
3. **Suppression message.** Draft the `postMessage` payload that sets suppression to 40 on a processor that exposes `setSuppressionLevel` in the range 0–100. What happens if you apply it halfway through `output.set`?
4. **Failure.** `process` occasionally takes 15 ms while the quantum is 2.67 ms. What does the user hear, and what should the next callback do?

### Answer hints

1. $$256/48000\approx 5.33$$ ms. $$256/44100\approx 5.80$$ ms. Both are still too small for a cold ONNX session, and 5.33 ms is half of a 10 ms hop, so one quantum is still not a hop.
2. Four callbacks hold $$4\times 128=512$$ samples. The hop consumes 480 and **32** remain in the input ring. Three callbacks hold only 384.
3. `{type: "setSuppressionLevel", value: 40}` handled in `onmessage`, stored in a field, applied on the next hop boundary. Applying it mid-copy makes the two halves of one quantum use different gains and clicks.
4. The device underruns: a click, a repeat, or a short silence, depending on the browser. The recovery callback should take the bypass path (copy) or play the samples already in the output ring, not block until inference catches up.

## Further reading

- MDN, [AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet) and the `AudioWorkletProcessor.process` reference.
- Lesson 05-01 for RTF and the 10 ms hop budget; lesson 05-03 for the ring that absorbs the 3.75 quanta.
- [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) for `DeepFilterNoiseFilterProcessor` and `setSuppressionLevel` as a product surface, not as this lesson’s code.
