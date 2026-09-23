# Real-Time Audio Noise Suppression: From DSP to DeepFilterNet

**VI:** Khử nhiễu âm thanh thời gian thực: Từ DSP đến DeepFilterNet

Bilingual (EN + VI) self-learning course for Vietnamese software engineers. Assumes coding comfort; teaches **Fourier transforms and the audio pipeline in depth** (not a light DSP mention), then classical NS, DeepFilterNet, realtime/on-device deployment, and product integration.

Capstone aligns with [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) (npm [`deepfilternet3-noise-filter`](https://www.npmjs.com/package/deepfilternet3-noise-filter)) — the course teaches **techniques**, not only the wrapper.

- **Author:** Nguyen Le Linh (`nglelinh@gmail.com`)
- **Site (intended):** https://nglelinh.github.io/audio-processing-self-learning/
- **Repo:** https://github.com/nglelinh/audio-processing-self-learning
- **Advisor outline:** [COURSE_OUTLINE.md](COURSE_OUTLINE.md)

## Chapters (00–10)

| # | EN | VI |
|---|----|----|
| 00 | Introduction & problem framing | Giới thiệu & định khung bài toán |
| 01 | **Fourier & discrete transforms (deep)** | **Fourier & biến đổi rời rạc (sâu)** |
| 02 | **Audio processing pipeline** | **Pipeline xử lý âm thanh** |
| 03 | Classical NS / AEC / beamforming | NS / AEC / beamforming cổ điển |
| 04 | Neural SE & DeepFilterNet family | SE neural & họ DeepFilterNet |
| 05 | Real-time constraints | Ràng buộc thời gian thực |
| 06 | On-device inference | Suy luận trên thiết bị |
| 07 | Product integration | Tích hợp sản phẩm |
| 08 | Evaluation | Đánh giá |
| 09 | Capstone: Mezon NS | Capstone: Mezon NS |
| 10 | References & further paths | Tài liệu & hướng đi tiếp |

Lessons are full bilingual articles (53 EN + 53 VI), not stubs. Chapters **01** (Fourier) and **02** (audio pipeline) are first-class modules: continuous FT, sampling/Nyquist, DTFT/DFS/DFT, FFT, realtime framing, then PCM, frames/OLA, windowing, STFT/ISTFT, filtering, spectrograms, and latency budgets.

## Figures

Teaching diagrams live in [`img/generated/`](img/generated/) (Fourier intuition, sampling/Nyquist, STFT/OLA, spectral subtraction/Wiener, DeepFilterNet ERB + deep filter, RTF/AudioWorklet, LiveKit TrackProcessor, evaluation map, and related pipeline figures). Lessons embed them with `{{ site.imgurl }}/generated/...`.

`imgurl` in `_config.yml` is site-relative (`/audio-processing-self-learning/img`) so the same path works for local `jekyll serve` and GitHub Pages. Regenerate PNGs with `python3 scripts/generate_course_figures.py`.

## Run locally (Jekyll)

```bash
bundle install
bundle exec jekyll serve
# http://127.0.0.1:4000/audio-processing-self-learning/
```

Docker: `docker-compose up` (if present). Restart Jekyll after `_config.yml` changes.

## Product context (do not modify from this course)

- GitHub: `mezonai/mezon-noise-suppression`
- npm: `deepfilternet3-noise-filter` **1.3.0** (`DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`, `setSuppressionLevel`, optional `assetConfig.cdnUrl`)
- Local Mac (instructor): `/Users/nguyenlelinh/ncc/mezon-noise-suppression`

## License

See [LICENSE.md](LICENSE.md).
