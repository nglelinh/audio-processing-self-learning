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

Browser real-time audio runs inside **AudioWorklet** (or legacy ScriptProcessorNode—avoid for production). Native stacks use similarly strict **audio callbacks**. This lesson teaches the callback contract: no blocking, bounded CPU, explicit communication with the main thread, and how a DeepFilterNet-class processor fits into `process(inputs, outputs, parameters)`.

## Learning objectives

You will describe the AudioWorklet lifecycle (`addModule`, `AudioWorkletNode`, `process`), list operations that are forbidden on the audio thread, design a message-port protocol for control (enable NS, load state), and sketch where ring buffers sit relative to the callback (05-03).

## 60-minute teaching plan

- **0–10 min** — Why main-thread audio fails; history → Worklet.
- **10–25 min** — Lifecycle and `process` signature; render quantum.
- **25–40 min** — Do’s/don’ts; transferring PCM via `MessagePort` / SharedArrayBuffer patterns at high level.
- **40–50 min** — Placing neural NS: in-worklet vs worker+SAB.
- **50–60 min** — Pitfalls, exercises, Mezon web implications.

## Core explanation

### Lifecycle (browser)

1. Main thread: `audioContext.audioWorklet.addModule('ns-processor.js')`.
2. Construct `AudioWorkletNode(audioContext, 'ns-processor', options)`.
3. Connect `mic → nsNode → destination` (or into WebRTC track plumbing—Ch. 07).
4. Browser calls `process(inputList, outputList, parameters)` repeatedly on the **audio rendering thread**.

### The `process` contract

```js
class NsProcessor extends AudioWorkletProcessor {
  process(inputs, outputs) {
    const input = inputs[0][0];   // Float32Array channel
    const output = outputs[0][0];
    // bounded work only
    this.ns.process(input, output);
    return true; // keep alive
  }
}
registerProcessor('ns-processor', NsProcessor);
```

**Return `true`** to keep the processor alive when the graph might otherwise tear it down—know your browser quirks.

### Hard rules on the audio thread

**Do not:** `fetch`, `JSON.parse` large blobs, allocate huge arrays each callback, take locks waiting on main, run GC-heavy JS, synchronously compile WASM, or block on `Atomics.wait` without a clear real-time design.

**Do:** preallocate buffers, reuse scratch memory, keep control messages tiny, measure worst-case CPU, fail soft (bypass NS) if behind.

### Render quantum vs model hop

Browsers often deliver **128-sample** blocks (at the context sample rate). DeepFilterNet hops may be **larger** (e.g. 480 samples at 48 kHz for 10 ms—verify your model). You must **accumulate** quanta into hops and **emit** OLA outputs via a ring buffer (next lesson). Never assume `input.length === hopSize`.

### Control plane

Use `node.port.postMessage` for:

- enable/disable NS,
- set suppression strength,
- report RTF stats (throttled),
- signal model ready / failed.

Load weights on the main thread or a worker; transfer a ready WASM module / ORT session into the worklet only with patterns your runtime supports (some products keep ORT in a worker and exchange PCM via SharedArrayBuffer—architecture choice for Ch. 07/09).

### Native callbacks (parallel mental model)

CoreAudio / WASAPI / Android AudioTrack callbacks share the philosophy: **finish before the next period**. The same ring-buffer and state rules apply; only the API names change.

## Pitfalls

- Using ScriptProcessorNode (main-thread, high latency, deprecated mindset).
- Creating `new Float32Array` every `process` call.
- Assuming sampleRate is always 48000—read `sampleRate` in the worklet scope.
- Posting large PCM arrays by structured clone every quantum (prefer SAB / transferable rings).

## Exercises

1. **Toy worklet.** Build a pass-through AudioWorklet that gains by 0.5; verify with a tone.
2. **Quantum log.** Count samples per `process` call across Chrome/Firefox; record results.
3. **Protocol.** Specify message types `{type:'setEnabled', value:boolean}` and a state machine diagram.
4. **Failure mode.** Describe user-visible behavior if `process` occasionally takes 15 ms when the quantum is ~3 ms.

## Further reading

- MDN AudioWorklet and AudioWorkletProcessor documentation.
- Web Audio API spec — rendering thread notes.
- WebRTC insertion points (preview of Ch. 07).
- ORT Web / WASM integration guides (high level).
