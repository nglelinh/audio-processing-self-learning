#!/usr/bin/env python3
"""Generate labeled teaching diagrams for the noise-suppression course.

Outputs PNG files under img/generated/. Re-run after editing this script:

    python3 scripts/generate_course_figures.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "img" / "generated"

INK = "#1a2332"
MUTED = "#526071"
BLUE = "#1f6feb"
GREEN = "#1a7f4b"
ORANGE = "#d97706"
RED = "#c2410c"
TEAL = "#0f766e"
PURPLE = "#6d28d9"
PANEL = "#f4f7fb"
LINE = "#d0d7e2"


def _new(w=11.2, h=6.2):
    fig, ax = plt.subplots(figsize=(w, h), dpi=140)
    fig.patch.set_facecolor("white")
    return fig, ax


def _save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(path)


def _box(ax, xy, w, h, text, fc, ec=INK, fs=9, weight="medium"):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor=fc,
        edgecolor=ec,
        linewidth=1.3,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fs,
        color=INK,
        fontweight=weight,
        wrap=True,
    )


def _arrow(ax, start, end, color=INK):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.4,
            color=color,
            shrinkA=2,
            shrinkB=2,
        )
    )


def fourier_intuition():
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.4), dpi=140)
    fig.patch.set_facecolor("white")
    t = np.linspace(0, 0.02, 1200)
    tones = [(200, 1.0), (600, 0.55), (1000, 0.28)]
    x = sum(a * np.sin(2 * np.pi * f * t) for f, a in tones)
    ax = axes[0]
    ax.plot(t * 1000, x, color=BLUE, lw=1.6)
    ax.set_title("Time: sum of three sinusoids", color=INK, fontsize=12, pad=8)
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("amplitude")
    ax.set_xlim(0, 20)
    ax.axhline(0, color=LINE, lw=0.8)
    ax.text(1, 1.55, r"$x(t)=\sum_k a_k\sin(2\pi f_k t)$", color=MUTED, fontsize=10)
    ax.set_ylim(-1.9, 1.9)
    ax.grid(True, color=LINE, lw=0.6)

    ax = axes[1]
    freqs = [f for f, _ in tones]
    amps = [a for _, a in tones]
    markerline, stemlines, baseline = ax.stem(freqs, amps, basefmt=" ")
    plt.setp(stemlines, color=GREEN, linewidth=2)
    plt.setp(markerline, color=GREEN, markersize=7)
    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 1.25)
    ax.set_title("Frequency: one line per tone", color=INK, fontsize=12, pad=8)
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel(r"$|X(f)|$")
    for f, a in tones:
        ax.annotate(f"{f} Hz", (f, a), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, color=INK)
    ax.grid(True, axis="y", color=LINE, lw=0.6)
    fig.suptitle("Fourier intuition — a periodic mixture becomes spectral lines", fontsize=13, color=INK, y=1.02)
    for a in axes:
        a.tick_params(colors=MUTED)
        for sp in a.spines.values():
            sp.set_color(LINE)
    _save(fig, "fourier-intuition.png")


def sampling_nyquist():
    fig, axes = plt.subplots(2, 1, figsize=(11.2, 6.6), dpi=140, sharex=True)
    fig.patch.set_facecolor("white")
    fs = 8000
    t = np.linspace(0, 0.004, 2000)
    n = np.arange(0, 0.004, 1 / fs)

    cases = [
        (1000, "Below Nyquist: 1 kHz sampled at 8 kHz is uniquely represented", BLUE, GREEN),
        (7000, "Alias: 7 kHz sampled at 8 kHz lands on the same samples as 1 kHz", RED, ORANGE),
    ]
    for ax, (f0, title, c_cont, c_samp) in zip(axes, cases):
        cont = np.sin(2 * np.pi * f0 * t)
        samp = np.sin(2 * np.pi * f0 * n)
        ax.plot(t * 1000, cont, color=c_cont, lw=1.5, label=f"continuous {f0/1000:.0f} kHz")
        ax.plot(n * 1000, samp, "o", color=c_samp, ms=7, label="samples @ 8 kHz")
        if f0 == 7000:
            alias = np.sin(2 * np.pi * 1000 * t)
            ax.plot(t * 1000, alias, color=BLUE, lw=1.2, ls="--", label="alias at 1 kHz = fs − 7 kHz")
        ax.set_title(title, color=INK, fontsize=11, loc="left")
        ax.set_ylabel("amplitude")
        ax.set_ylim(-1.35, 1.45)
        ax.legend(loc="upper right", fontsize=8, frameon=False)
        ax.grid(True, color=LINE, lw=0.5)
        ax.axhline(0, color=LINE, lw=0.7)
        for sp in ax.spines.values():
            sp.set_color(LINE)
    axes[1].set_xlabel("time (ms)")
    fig.suptitle("Sampling and Nyquist — fs/2 = 4 kHz is the folding frequency", fontsize=13, color=INK)
    fig.tight_layout()
    _save(fig, "sampling-nyquist.png")


def stft_ola():
    fig, axes = plt.subplots(3, 1, figsize=(11.2, 7.2), dpi=140, sharex=True)
    fig.patch.set_facecolor("white")
    L, R, nframes = 64, 32, 4
    n = np.arange(0, R * (nframes - 1) + L)
    wave = 0.7 * np.sin(2 * np.pi * n / 28)
    ax = axes[0]
    ax.plot(n, wave, color=INK, lw=1.2)
    ax.set_ylabel("x[n]")
    ax.set_ylim(-1.15, 1.35)
    ax.set_title("Analysis frames: length L, hop R (here L = 64, R = 32, 50% overlap)", loc="left", color=INK, fontsize=11)
    colors = [BLUE, GREEN, ORANGE, PURPLE]
    hann = np.hanning(L)
    for m, c in enumerate(colors):
        start = m * R
        ax.axvspan(start, start + L, color=c, alpha=0.08)
        ax.text(start + 4, 1.12, f"frame {m}", fontsize=8, color=c, ha="left")

    ax = axes[1]
    for m, c in enumerate(colors):
        start = m * R
        ax.plot(np.arange(start, start + L), hann, color=c, lw=1.8)
    ax.annotate(
        "",
        xy=(0, 1.08),
        xytext=(L, 1.08),
        arrowprops=dict(arrowstyle="<->", color=INK, lw=1.1),
    )
    ax.text(L / 2, 1.18, "frame length L", ha="center", va="bottom", color=INK, fontsize=8)
    ax.annotate(
        "",
        xy=(L, 0.55),
        xytext=(L + R, 0.55),
        arrowprops=dict(arrowstyle="<->", color=ORANGE, lw=1.2),
    )
    ax.text(L + R / 2, 0.62, "hop R", ha="center", va="bottom", color=ORANGE, fontsize=8)
    ax.set_ylabel("window")
    ax.set_ylim(-0.05, 1.45)
    ax.set_title("Hann windows slide by R. Each frame is FFT'd, modified, then IFFT'd.", loc="left", color=INK, fontsize=11)

    ax = axes[2]
    acc = np.zeros(n.size + L)
    for m in range(nframes):
        acc[m * R : m * R + L] += hann ** 2
    ax.plot(acc[: n.size], color=TEAL, lw=2)
    ax.axhline(acc[L // 2 : L // 2 + R * (nframes - 1)].mean(), color=MUTED, ls="--", lw=0.8)
    ax.set_ylabel("COLA sum")
    ax.set_xlabel("sample index")
    ax.set_title(r"COLA: $\sum_m w^2[n-mR]$ is flat in the steady region — OLA can rebuild x[n]", loc="left", color=INK, fontsize=11)
    for a in axes:
        a.grid(True, color=LINE, lw=0.5)
        for sp in a.spines.values():
            sp.set_color(LINE)
        a.set_xlim(0, n[-1])
    fig.tight_layout()
    _save(fig, "stft-ola.png")


def spectral_subtraction_wiener():
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.6), dpi=140)
    fig.patch.set_facecolor("white")
    bins = np.arange(1, 13)
    speech = np.array([0.2, 0.4, 1.6, 2.4, 1.1, 0.5, 1.8, 2.1, 0.7, 0.3, 0.25, 0.2])
    noise = np.full_like(speech, 0.45)
    y2 = speech + noise
    alpha, beta = 1.0, 0.1
    sub = np.maximum(y2 - alpha * noise, beta * noise)

    ax = axes[0]
    ax.bar(bins - 0.18, y2, width=0.36, color="#93c5fd", label=r"$|Y|^2$ noisy power")
    ax.bar(bins + 0.18, sub, width=0.36, color=GREEN, label=r"$\max(|Y|^2-\alpha|\hat N|^2,\ \beta|\hat N|^2)$")
    ax.plot(bins, noise, color=ORANGE, marker="o", lw=1.4, label=r"noise floor $|\hat N|^2$")
    ax.set_xlabel("frequency bin k")
    ax.set_ylabel("power")
    ax.set_title("Spectral subtraction (power)", color=INK, fontsize=12)
    ax.legend(fontsize=8, frameon=False, loc="upper right")
    ax.set_xticks(bins)

    ax = axes[1]
    xi = np.logspace(-1.2, 1.4, 300)
    gain = xi / (1 + xi)
    ax.semilogx(xi, gain, color=BLUE, lw=2.2, label=r"Wiener $H=\xi/(1+\xi)$")
    ax.axhline(0.5, color=LINE, ls="--", lw=0.8)
    ax.annotate("equal speech & noise\n→ gain 0.5 (−6 dB)", xy=(1, 0.5), xytext=(2.2, 0.28),
                fontsize=8, color=MUTED, arrowprops=dict(arrowstyle="->", color=MUTED))
    ax.set_xlabel(r"a priori SNR $\xi = P_s / P_n$")
    ax.set_ylabel("gain H(k)")
    ax.set_ylim(0, 1.05)
    ax.set_title("Wiener gain is a soft SNR gate", color=INK, fontsize=12)
    ax.legend(fontsize=8, frameon=False)
    ax.grid(True, which="both", color=LINE, lw=0.5)
    for a in axes:
        for sp in a.spines.values():
            sp.set_color(LINE)
    fig.suptitle("Classical NS — subtract a floor, or apply an SNR-dependent gain", fontsize=13, color=INK)
    fig.tight_layout()
    _save(fig, "spectral-subtraction-wiener.png")


def deepfilternet_erb():
    fig, ax = _new(12.2, 6.4)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    ax.set_title("DeepFilterNet block — ERB path plus multi-frame deep filter", loc="left", color=INK, fontsize=13, pad=8)

    _box(ax, (0.25, 2.6), 1.5, 1.1, "PCM\n48 kHz", "#e0f2fe")
    _box(ax, (2.15, 2.6), 1.6, 1.1, "STFT\nHann, hop", "#e0f2fe")
    _box(ax, (4.2, 4.35), 2.3, 1.25, "ERB features\n(coarse bands)", "#dcfce7")
    _box(ax, (6.85, 4.35), 2.5, 1.25, "ERB encoder\n→ band gains", "#bbf7d0")
    _box(ax, (4.2, 0.7), 2.3, 1.25, "Complex STFT\nY(k, ℓ)", "#ffedd5")
    _box(ax, (6.85, 0.7), 2.5, 1.25, "Deep filter\n" + r"$\sum_\tau H_\tau Y_{\ell-\tau}$", "#fed7aa")
    _box(ax, (9.7, 2.6), 1.9, 1.1, "ISTFT\n+ OLA", "#ede9fe")

    _arrow(ax, (1.75, 3.15), (2.15, 3.15))
    _arrow(ax, (3.75, 3.4), (4.2, 4.9))
    _arrow(ax, (3.75, 2.9), (4.2, 1.35))
    _arrow(ax, (6.5, 4.95), (6.85, 4.95))
    _arrow(ax, (6.5, 1.3), (6.85, 1.3))
    _arrow(ax, (9.35, 4.7), (10.2, 3.7))
    _arrow(ax, (9.35, 1.5), (10.2, 2.6))
    ax.text(6.0, 3.15, "causal\nstate", ha="center", va="center", fontsize=8, color=PURPLE)
    ax.annotate(
        "",
        xy=(7.4, 1.95),
        xytext=(7.4, 4.35),
        arrowprops=dict(arrowstyle="<->", color=PURPLE, lw=1.2),
    )
    ax.text(0.25, 0.25, "ERB stage suppresses noise cheaply. Deep filter restores harmonics the coarse bands smear.\nLook-ahead, if any, is part of algorithmic latency — not free.", fontsize=9, color=MUTED)
    _save(fig, "deepfilternet-erb.png")


def rtf_audioworklet():
    fig, ax = _new(11.4, 5.8)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 10.5)
    ax.axis("off")
    ax.set_title("RTF and the AudioWorklet deadline", loc="left", color=INK, fontsize=13)

    # timeline
    ax.plot([8, 98], [8.15, 8.15], color=INK, lw=1.2)
    for i, x in enumerate(range(8, 99, 18)):
        ax.plot([x, x], [7.95, 8.35], color=INK, lw=1.2)
        ax.text(x + 9, 8.85, f"q{i+1}", ha="center", fontsize=8, color=MUTED)
    ax.text(8, 9.45, "Each tick is one render quantum (~128 samples ≈ 2.7 ms at 48 kHz). Bars below are process() time.", fontsize=8.5, color=MUTED)

    # processing bars: 4 ok, 1 overrun
    durations = [8, 7, 10, 16, 6]
    colors = [GREEN, GREEN, GREEN, RED, GREEN]
    labels = ["ok", "ok", "ok", "overrun", "ok"]
    for i, (d, c, lab) in enumerate(zip(durations, colors, labels)):
        x0 = 8 + i * 18
        ax.add_patch(FancyBboxPatch((x0, 4.6), d, 1.3, boxstyle="round,pad=0.02,rounding_size=0.15",
                                    facecolor=c, edgecolor="none", alpha=0.85))
        ax.text(x0 + d / 2, 5.25, lab, ha="center", va="center", color="white", fontsize=8, fontweight="bold")
    ax.text(4, 5.25, "process()", ha="right", va="center", color=INK, fontsize=9)

    ax.text(8, 3.3, r"RTF $= T_{wall}(D) / D$.  RTF < 1 is necessary, not sufficient.", fontsize=11, color=INK)
    ax.text(8, 2.45, "A mean RTF of 0.4 can still click if p99 exceeds the hop. Log p95/p99, not only the average.", fontsize=10, color=MUTED)
    ax.text(8, 1.55, "Audio thread: STFT + model + OLA must finish before the next quantum is due.", fontsize=10, color=MUTED)
    ax.text(8, 0.7, "Main thread: download WASM/ONNX and compile — cold start, not steady-state RTF.", fontsize=10, color=MUTED)
    _save(fig, "rtf-audioworklet.png")


def livekit_trackprocessor():
    fig, ax = _new(12.0, 6.2)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    ax.set_title("LiveKit publish path with DeepFilterNoiseFilterProcessor", loc="left", color=INK, fontsize=13)

    boxes = [
        (0.3, 2.5, 1.7, 1.2, "Mic\nMediaStream", "#e0f2fe"),
        (2.4, 2.5, 2.1, 1.2, "LocalAudioTrack\nsetProcessor()", "#dbeafe"),
        (4.9, 2.5, 2.6, 1.2, "DeepFilterNoise\nFilterProcessor", "#dcfce7"),
        (7.9, 2.5, 1.8, 1.2, "Encoded\naudio", "#ffedd5"),
        (10.0, 2.5, 1.6, 1.2, "LiveKit\nSFU", "#ede9fe"),
    ]
    for b in boxes:
        _box(ax, (b[0], b[1]), b[2], b[3], b[4], b[5], fs=8.5)
    for x1, x2 in ((2.0, 2.4), (4.5, 4.9), (7.5, 7.9), (9.7, 10.0)):
        _arrow(ax, (x1, 3.1), (x2, 3.1))

    _box(ax, (4.9, 4.5), 2.6, 1.15, "CDN assets\nWASM + ONNX model\n(v2/ on ≥ 1.2.0)", "#fef9c3", fs=8)
    _arrow(ax, (6.2, 4.5), (6.2, 3.7), color=ORANGE)
    _box(ax, (4.9, 0.45), 2.6, 1.25, "setSuppressionLevel(0–100)\nsetEnabled(false) → bypass", "#f1f5f9", fs=8)
    _arrow(ax, (6.2, 1.7), (6.2, 2.5), color=TEAL)
    ax.text(0.3, 0.15, "Processor owns the audio graph. The Room still owns signaling. On asset failure, publish unprocessed audio.", fontsize=9, color=MUTED)
    _save(fig, "livekit-trackprocessor.png")


def eval_metric_map():
    fig, ax = _new(11.6, 6.2)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    ax.set_title("Evaluation map — three questions, three metric families", loc="left", color=INK, fontsize=13)

    _box(ax, (0.35, 4.3), 3.4, 1.5, "Intrusive\nSI-SDR, STOI\nneeds aligned clean reference", "#dbeafe", fs=9)
    _box(ax, (4.3, 4.3), 3.4, 1.5, "Non-intrusive\nDNSMOS / P.835\nno clean reference", "#dcfce7", fs=9)
    _box(ax, (8.25, 4.3), 3.4, 1.5, "Human\nlistening test\ngold standard, slow", "#ffedd5", fs=9)
    _box(ax, (3.3, 1.5), 5.4, 1.45, "Ship decision for Mezon NS\nquality  ·  artifacts  ·  RTF  ·  failure policy", "#ede9fe", fs=10)
    for x in (2.05, 6.0, 9.95):
        _arrow(ax, (x, 4.3), (6.0, 2.95))
    ax.text(0.4, 0.45, "High SI-SDR can still sound metallic. DNSMOS can miss your noise domain. Listening tests catch both — if the clips are fair.", fontsize=9, color=MUTED)
    _save(fig, "eval-metric-map.png")


def window_leakage():
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.2), dpi=140)
    fig.patch.set_facecolor("white")
    n = np.arange(256)
    tone = np.sin(2 * np.pi * 10.5 * n / 256)
    for ax, w, title, color in (
        (axes[0], np.ones(256), "Rectangular window — sinc leakage", ORANGE),
        (axes[1], np.hanning(256), "Hann window — lower sidelobes, wider main lobe", BLUE),
    ):
        spec = np.abs(np.fft.rfft(tone * w))
        spec_db = 20 * np.log10(spec / spec.max() + 1e-12)
        ax.plot(spec_db, color=color, lw=1.6)
        ax.set_ylim(-80, 3)
        ax.set_xlim(0, 80)
        ax.set_title(title, color=INK, fontsize=11)
        ax.set_xlabel("FFT bin")
        ax.set_ylabel("magnitude (dB, peak-normalized)")
        ax.axhline(-40, color=LINE, ls="--", lw=0.7)
        ax.grid(True, color=LINE, lw=0.5)
        for sp in ax.spines.values():
            sp.set_color(LINE)
    fig.suptitle("Spectral leakage — the window, not the FFT length alone, sets the sidelobes", fontsize=12, color=INK)
    fig.tight_layout()
    _save(fig, "window-leakage.png")


def ring_buffer():
    fig, ax = _new(11.2, 4.8)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.set_title("Single-producer ring buffer between mic callback and NS worker", loc="left", color=INK, fontsize=13)
    for i in range(10):
        color = "#bbf7d0" if i < 6 else "#f1f5f9"
        if i == 6:
            color = "#fecaca"
        _box(ax, (0.4 + i * 1.15, 2.3), 1.05, 1.1, str(i), color, fs=10)
    ax.annotate("read", xy=(0.9, 2.3), xytext=(0.9, 1.3), arrowprops=dict(arrowstyle="->", color=GREEN), ha="center", color=GREEN, fontsize=9)
    ax.annotate("write", xy=(0.4 + 6 * 1.15 + 0.5, 3.4), xytext=(0.4 + 6 * 1.15 + 0.5, 4.3),
                arrowprops=dict(arrowstyle="->", color=RED), ha="center", color=RED, fontsize=9)
    ax.text(0.4, 0.6, "Filled slots (green) are ready to process. If write catches read, you overrun: drop or bypass, do not grow without bound.", fontsize=9, color=MUTED)
    _save(fig, "ring-buffer.png")


def noise_mixture():
    fig, axes = plt.subplots(3, 1, figsize=(11.0, 6.4), dpi=140, sharex=True)
    fig.patch.set_facecolor("white")
    n = np.arange(800)
    rng = np.random.default_rng(0)
    speech = np.zeros_like(n, dtype=float)
    speech[120:520] = np.sin(2 * np.pi * n[120:520] / 18) * np.hanning(400)
    noise = 0.25 * rng.standard_normal(n.size)
    mix = speech + noise
    for ax, y, title, c in (
        (axes[0], speech, "Clean speech s[n]  (what SI-SDR wants as the reference)", GREEN),
        (axes[1], noise, "Additive noise n[n]  (stationary in this cartoon)", ORANGE),
        (axes[2], mix, r"Mixture y[n] = s[n] + n[n]   — the only signal the mic gives you", BLUE),
    ):
        ax.plot(y, color=c, lw=1.0)
        ax.set_title(title, loc="left", color=INK, fontsize=11)
        ax.set_ylabel("amp")
        ax.set_ylim(-1.4, 1.4)
        ax.grid(True, color=LINE, lw=0.4)
        for sp in ax.spines.values():
            sp.set_color(LINE)
    axes[2].set_xlabel("sample")
    fig.tight_layout()
    _save(fig, "noise-mixture.png")


def realtime_vs_offline():
    fig, ax = _new(11.2, 5.4)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("Offline enhancement may see the future. A call may not.", loc="left", color=INK, fontsize=13)
    _box(ax, (0.4, 3.4), 5.2, 1.8, "Offline file\nwhole utterance in memory\nbidirectional net, any RTF\nmetric = best quality", "#dbeafe", fs=9)
    _box(ax, (6.4, 3.4), 5.2, 1.8, "Live call\ncausal hop + small look-ahead\nRTF p95 < budget\nmetric = quality at a deadline", "#dcfce7", fs=9)
    ax.text(0.5, 2.3, "Algorithmic latency ≈ frame centering + look-ahead + hop, even when RTF ≪ 1.", fontsize=10, color=INK)
    ax.text(0.5, 1.5, "A model that scores well offline can still be unsippable if it reads future frames or misses the callback.", fontsize=10, color=MUTED)
    ax.text(0.5, 0.7, "Mezon NS ships the live column: on-device, causal, with an explicit bypass when the deadline is missed.", fontsize=10, color=MUTED)
    _save(fig, "realtime-vs-offline.png")


def onnx_wasm_path():
    fig, ax = _new(12.0, 5.2)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5.2)
    ax.axis("off")
    ax.set_title("On-device path used by deepfilternet3-noise-filter ≥ 1.2", loc="left", color=INK, fontsize=13)
    labels = [
        (0.25, "PyTorch\nDF3 graph", "#e0f2fe"),
        (2.55, "ONNX\nexport", "#dbeafe"),
        (4.85, "WASM\nSIMD build", "#dcfce7"),
        (7.15, "Package or CDN\n1.3.0 uses v3/", "#fef9c3"),
        (9.45, "AudioWorklet\ninference", "#ede9fe"),
    ]
    for x, text, fc in labels:
        _box(ax, (x, 2.2), 2.1, 1.3, text, fc, fs=9)
    for x in (2.35, 4.65, 6.95, 9.25):
        _arrow(ax, (x, 2.85), (x + 0.2, 2.85))
    ax.text(0.3, 1.2, "Installed 1.3.0 getAssetUrls() requests v3/pkg/df_bg.wasm and v3/models/DeepFilterNet3_onnx.tar.gz.", fontsize=9, color=INK)
    ax.text(0.3, 0.55, "The README still says v2/ for every release ≥ 1.2.0. The package adds the prefix. Do not put v2 or v3 in cdnUrl.", fontsize=9, color=MUTED)
    _save(fig, "onnx-wasm-path.png")


def spectrogram_reading():
    fig, ax = _new(11.0, 5.2)
    rng = np.random.default_rng(1)
    t = np.linspace(0, 1.2, 180)
    f = np.linspace(0, 8000, 120)
    spec = 0.15 * rng.random((f.size, t.size))
    # harmonics during speech
    for h in range(1, 8):
        band = int(h * 180 * 8 / 80)
        if band < f.size:
            spec[band - 1 : band + 2, 30:120] += 0.8 / h
    # noise burst
    spec[:, 130:155] += 0.55
    ax.imshow(spec, origin="lower", aspect="auto", cmap="magma",
              extent=[0, 1.2, 0, 8])
    ax.set_xlabel("time (s)")
    ax.set_ylabel("frequency (kHz)")
    ax.set_title("How to read a speech spectrogram", color=INK, fontsize=13)
    ax.annotate("voiced harmonics\n(vertical stack)", xy=(0.45, 1.4), xytext=(0.15, 5.5),
                color="white", fontsize=9, arrowprops=dict(arrowstyle="->", color="white"))
    ax.annotate("noise burst\n(fills all bands)", xy=(1.05, 4), xytext=(0.72, 6.6),
                color="white", fontsize=9, arrowprops=dict(arrowstyle="->", color="white"))
    _save(fig, "spectrogram-reading.png")


def dft_basis():
    fig, axes = plt.subplots(2, 4, figsize=(11.2, 5.0), dpi=140)
    fig.patch.set_facecolor("white")
    N = 32
    n = np.arange(N)
    ks = [0, 1, 2, 4]
    for col, k in enumerate(ks):
        real = np.cos(2 * np.pi * k * n / N)
        imag = -np.sin(2 * np.pi * k * n / N)
        axes[0, col].stem(n, real, linefmt="C0-", markerfmt="C0o", basefmt=" ")
        axes[1, col].stem(n, imag, linefmt="C1-", markerfmt="C1o", basefmt=" ")
        axes[0, col].set_title(f"k = {k}", color=INK, fontsize=10)
        axes[0, col].set_ylim(-1.2, 1.2)
        axes[1, col].set_ylim(-1.2, 1.2)
        for a in (axes[0, col], axes[1, col]):
            a.set_xticks([])
            a.grid(True, color=LINE, lw=0.4)
            for sp in a.spines.values():
                sp.set_color(LINE)
    axes[0, 0].set_ylabel("real")
    axes[1, 0].set_ylabel("imag")
    fig.suptitle(r"DFT basis vectors for N = 32  —  columns of the DFT matrix, $e^{-j2\pi kn/N}$", fontsize=12, color=INK)
    fig.tight_layout()
    _save(fig, "dft-basis.png")


def main():
    fourier_intuition()
    sampling_nyquist()
    stft_ola()
    spectral_subtraction_wiener()
    deepfilternet_erb()
    rtf_audioworklet()
    livekit_trackprocessor()
    eval_metric_map()
    window_leakage()
    ring_buffer()
    noise_mixture()
    realtime_vs_offline()
    onnx_wasm_path()
    spectrogram_reading()
    dft_basis()


if __name__ == "__main__":
    main()
