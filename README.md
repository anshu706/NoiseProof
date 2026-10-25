# NoiseProof: Call Intelligence Under Noisy Conditions
> **Target Award:** *Noise Canceller* — Best performance on messy, noisy Indian telephonic audio  
> **Built for:** The Great Indian AI Internship Challenge (Gnani AI)  
> **UI Aesthetic:** Shopify Editions Winter 2026 Edition

---

## 🌟 Overview

**NoiseProof** is an end-to-end benchmarking and call intelligence platform powered by **Gnani AI's Vachana Suite**:
- **Gnani Prisma v2.5**: Code-mixed Hinglish Speech-to-Text (STT) handling heavy noise and telephone degradation.
- **Gnani Timbre v2.5**: Multi-voice Text-to-Speech (TTS) generating realistic synthetic dialogue turns (`Poorvi` Hinglish female agent, `Vikrant` Hindi male customer).
- **Gnani Evon v3.3**: Reasoning LLM for script generation, entity fact extraction, and call summarisation.

NoiseProof evaluates call summarisation accuracy as signal-to-noise ratio drops from clean speech down to **0 dB SNR** across **5 noise environments** (street traffic, crowd chatter, wind turbulence, white noise, and bustling markets) and simulated **ITU G.711 telephone degradation** (8 kHz bandpass, soft clipping, and packet dropouts).

---

## 🎨 Design System: Shopify Editions Winter 2026 ("The RenAIssance Edition")

The web interface is engineered around the **Shopify Editions Winter 2026** editorial design language:
- **Museum Warm Parchment Canvas**: Architectural grid backdrop (`#F7F7EE`) with deep olive-charcoal museum ink (`#292919`).
- **Italian Fresco Palette**: Tuscan Terracotta (`#C24B27`), Antique Florentine Gold (`#B88E3E`), and Cypress Olive (`#2D5A27`).
- **Editorial Typography**: Newsreader classical serif display typography paired with geometric Plus Jakarta Sans and JetBrains Mono badges.
- **Dual Audio Inspection Lab**: Synchronized clean vs. degraded waveform listening with live transcript diffing and turn-level inspection.
- **Award Status Bar**: Edition header bar with live pulsing gold dot tracking target award status (*Noise Canceller: 0 dB Tolerance*).

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+ (tested on Python 3.12 / 3.14)
- Node.js 18+ & npm

### 2. Environment Configuration
Copy `.env.example` to `.env` and verify your Gnani API key:
```bash
cp .env.example .env
```
Ensure your key is set:
```env
GNANI_API_KEY=your_gnani_api_key_here
DRY_RUN=false
MAX_API_CALLS=200
```

### 3. Running Backend
```bash
python -m uvicorn backend.app.main:app --port 8000 --reload
```
API Documentation will be available at: `http://localhost:8000/docs`

### 4. Running Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 📊 CLI Benchmark Runner

To run the full multi-condition stress test from the terminal:

```bash
# Run 2 synthetic calls across all 5 noise types & 5 SNR levels (50 total variants)
python scripts/run_benchmark.py --calls 2 --noise street crowd wind white market --snr clean 20 10 5 0

# Dry-run mode (emulates API calls to test without consuming credits)
python scripts/run_benchmark.py --calls 1 --noise street --snr clean 20 --dry-run
```

---

## 🧪 Test Suite

Run the full pytest suite (metrics, SNR mixing accuracy, telephone filter, audio byte roundtrips):
```bash
python -m pytest backend/tests -v
```
All **34 unit tests** pass with 100% pass rate.

---

## 📁 Repository Structure

```
NoiseProof/
├── backend/
│   ├── app/
│   │   ├── cache.py           # SHA-256 disk-backed cache protecting API credits
│   │   ├── call_generator.py  # Hinglish dialogue scripts + Timbre TTS voice synthesis
│   │   ├── config.py          # Centralised Pydantic settings & safety caps
│   │   ├── gnani_client.py    # Unified gateway for Prisma STT, Timbre TTS & Evon
│   │   ├── main.py            # FastAPI REST endpoints + static audio streaming
│   │   ├── metrics.py         # WER, CER, Key-Fact Recall, and Action-Item F1
│   │   ├── models.py          # Pydantic data schemas
│   │   ├── noise_engine.py    # Procedural noise generation + RMS SNR mixing + phone sim
│   │   ├── pipeline.py        # End-to-end benchmark orchestration
│   │   ├── summarize.py       # Summarisation & key-fact extraction with heuristic fallback
│   │   └── transcribe.py      # Multi-variant STT execution & disk caching
│   └── tests/
│       ├── test_metrics.py    # Word Error Rate, recall, and normalisation tests
│       └── test_noise_engine.py # SNR precision, telephone filter, and audio I/O tests
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Overview.jsx       # Benchmark hero, bento stat cards, degradation charts
│   │   │   ├── CallExplorer.jsx   # Dual audio players, transcript diffs, dialogue turns
│   │   │   ├── NoiseBreakdown.jsx # Comparative noise archetype charts & tables
│   │   │   ├── RunPipeline.jsx    # Live benchmark runner & credit estimator
│   │   │   └── UploadCall.jsx     # On-demand custom recording inference lab
│   │   ├── App.jsx            # Shopify Editions header banner, sidebar, and routing
│   │   ├── index.css          # Shopify Editions Winter 2026 design system
│   │   └── api.js             # API helper
│   ├── index.html
│   └── vite.config.js
├── data/
│   ├── calls/                 # Generated WAVs & reference transcripts
│   ├── noise/                 # Procedural and custom noise profiles
│   ├── results/               # Run metrics & aggregated JSON benchmarks
│   └── cache/                 # Diskcache storage
├── scripts/
│   └── run_benchmark.py       # Command-line benchmark orchestrator
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🏆 Key Features for The Challenge

1. **Deterministic SNR Mixing & Telephony Filter**: Mathematical RMS power scaling down to 0 dB, ITU-T G.711 300–3400 Hz bandpass, soft saturation clipping, and random packet-loss dropouts.
2. **Entity Recall Metric**: Tracks whether critical customer numbers (loan amounts, order IDs, account numbers, dates) survived noise distortion.
3. **Credit Conservation**: Strict SHA-256 diskcache prevents duplicate billings; configurable hard cap `MAX_API_CALLS` stops runaway loops.
4. **Resilient Fallbacks**: If Evon reasoning endpoints encounter scope restrictions on API keys, the engine automatically activates high-fidelity extractive parsing and realistic scenario templates while preserving live Gnani Timbre TTS audio generation and Prisma STT transcription.
