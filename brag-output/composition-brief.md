# Hyperframes Composition Brief: NoiseProof

## Objective
Create a short cinematic launch brag video for NoiseProof — a call intelligence benchmarking platform built for the Gnani AI Great Indian AI Internship Challenge.

## Output
- Composition directory: brag-output/composition/
- Rendered video: brag-output/brag.mp4
- Format: landscape — 1920x1080
- Duration: 21 seconds

## Source Material
- Project root: d:/PROJECTS/NoiseProof/
- Primary files read: frontend/src/index.css, frontend/src/App.jsx, frontend/src/pages/Overview.jsx, README.md
- Product name: NoiseProof
- Tagline / strongest claim: "Award Target: Noise Canceller — 0 dB Tolerance"
- Key UI or visual moment to recreate: The WER stat-number counter (Newsreader serif, huge, terracotta on worst case) and the Gnani engine badge stack from the sidebar
- Copy that must appear verbatim:
  - "What happens to a phone call at 0 dB noise?"
  - "Award Target: Noise Canceller (0 dB Tolerance)"
  - "NoiseProof"
  - "THE RENAISSANCE EDITION, WINTER 26"
  - "Prisma v2.5 · STT Audio Engine"
  - "Timbre v2.5 · Multi-Voice TTS"
  - "Evon v3.3 · Reasoning & Eval"

## Creative Direction
- Tone preset: cinematic
- Creative direction: Renaissance AI lab — scholarly, precise, dramatic
- Interpretation: Long holds on important numbers, one element at a time, gold accents as emotional punctuation. Restraint over hype. Parchment warmth over harsh contrast.
- Angle: The video dramatizes the collapse of speech comprehension under noise, showing the WER counter rise from 5% (clean speech) to 67% (0 dB SNR), then reveals the three Gnani AI engines behind the benchmark.
- Hook: "What happens to a phone call at 0 dB noise?" typed word by word on warm parchment, then a hard cut to the WER number slamming in.
- Outro / punchline: The edition banner with the pulsing gold dot, the NoiseProof wordmark, and the challenge hashtags — closing with a deep bell.
- Avoid:
  - Generic SaaS language ("streamline", "empower", etc.)
  - Abstract filler visuals (color washes, particles, floating shapes)
  - Dark mode — the app is warm parchment light mode; match that exactly

## Visual Identity
- Background: #F7F7EE (museum warm antique parchment)
- Text: #292919 (dark olive-charcoal)
- Accent / gold: #B88E3E (Antique Florentine Gold)
- Noise / danger: #C24B27 (Tuscan Terracotta)
- Engine / success: #2D5A27 (Cypress Olive)
- Display font: Newsreader (Google Font, serif — use for all large numbers and the wordmark); fallback: Georgia
- Body font: Plus Jakarta Sans (Google Font, sans-serif); fallback: system-ui
- Mono font: JetBrains Mono; fallback: monospace
- Visual references from the project:
  - Architectural grid background: 80px grid, hairline rgba(41,41,25,0.03) lines on the parchment
  - .stat-number class: Newsreader serif, clamp(38px, 4.5vw, 58px), font-weight 600, letter-spacing -0.03em, font-feature-settings "tnum"
  - .gnani-badge: white bg, 1px solid rgba(41,41,25,0.12) border, JetBrains Mono 11px, border-radius 6px, strong tags in #292919
  - .edition-tag: white bg, 100px border-radius pill, ink text, 11px mono, live-dot in gold with 2.2s pulseDot animation
  - .brand-crest: 36px square, #292919 bg, #F7F7EE Newsreader italic "N", border-radius 8px
  - Card style: white surface, rgba(41,41,25,0.12) hairline border, border-radius 14px

## Storyboard
Use the storyboard in brag-output/brag-plan.md as the creative contract.

Scene summary:
1. Hook — 3s — "What happens to a phone call at 0 dB noise?" types word by word on parchment
2. WER Collapse — 7s — Giant serif number counts 5% → 28% → 67%, color shifts to terracotta, bell hits on each
3. Noise Environments — 4s — 5 cards slide in one by one: Street, Crowd, Wind, White, Markets
4. Gnani Vachana Suite — 4s — 3 engine badges stack vertically: Prisma, Timbre, Evon
5. Outro — 3s — Edition banner + NoiseProof wordmark + hashtags + pulsing gold dot

## Audio
- Audio role: cinematic support
- Audio arc: quiet suspense → verdict (bell hits on WER) → methodical (card slides) → warm authority (badge drops) → deep resonance (outro bell, music fades)
- Music: assets/music/happy-beats-business-moves-vol-12-by-ende-dot-app.mp3
- Music treatment: volume 0.32, start at 0s, slight swell ~14s into Scene 4, fade to 0.18 in final 1.5s
- Music cue guidance: use bundled preset JSON for vol-12; target strong cues near 6s (WER reveal) and 14s (Gnani reveal); or detect at composition time via hyperframes beats; use 1-2 beat locks maximum
- Audio-reactive treatment: subtle; use music RMS/bass to gently modulate background warmth and the gold accent glow on the badge cards. No waveform visualizers. No heavy pulsing.
- Audio-coupled moments:
  - Scene 1 — per-word keyboard sounds (randomized from keyboard/ set, 1 per word)
  - Scene 2 beat 1 — impact/impactBell_heavy_000.ogg at WER number arrival (5%)
  - Scene 2 beat 2 — impact/impactBell_heavy_003.ogg at 28% arrival
  - Scene 2 beat 3 — impact/impactBell_heavy_003.ogg at 67% arrival (loudest)
  - Scene 3 — casino/card-slide-3.ogg per card, 0.55 volume, 5 times
  - Scene 4 — interface/drop_001, drop_002, drop_003 per badge, ~0.65 volume
  - Scene 5 — impact/impactBell_heavy_004.ogg on wordmark lock, 0.45 volume
- SFX selection guidance: all from the brag skill assets. For the bell hits, use the heavy_000, heavy_003, and heavy_004 variants of impactBell. For card slides, casino/card-slide-3.ogg is the most neutral. Drop sounds for badge arrivals. Keyboard/ randomized per word in Scene 1.
- SFX analysis guidance: read sfx-analysis.md from skill assets if available
- Exact SFX choice: Hyperframes should finalize filenames, timestamps, and volumes based on the actual implemented animation timing
- Audio files: copy chosen music and SFX into brag-output/composition/assets/

## Hyperframes Instructions
Load the composition-building Hyperframes domain skills (hyperframes-core, hyperframes-animation, hyperframes-creative, hyperframes-keyframes, hyperframes-cli). Do NOT enter the hyperframes entry-point intent interview. Do NOT route into the generic promo or launch-video workflow. This is the /brag workflow — use the brag-plan.md and this brief as the creative contract.

Requirements:
- Show at least one real UI element from the source project (the stat-number typography, the gnani-badge, and the edition-tag are all recreated from exact CSS values above)
- Keep all text readable — every line of copy must hit its reading-time floor
- Keep the video within 21 seconds
- Include the music and SFX layer as specified
- Treat music cue metadata as optional timing hints — readability and pacing come first
- The parchment background with the architectural grid MUST appear throughout (this is the most distinctive visual element)
- The WER counter must be the hero moment — giant serif number, hard cuts between states, bell hit on each
- Run npx hyperframes check before render — zero errors required
