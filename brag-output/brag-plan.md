# Brag Plan: NoiseProof

## What is this app?
NoiseProof is a call intelligence benchmarking platform that generates synthetic Hinglish phone calls, degrades them through five noise environments down to 0 dB SNR, transcribes them with Gnani Prisma STT, and measures exactly how much intelligence — entity recall, word accuracy, call summaries — survives the noise.

## The angle
The drama is the number. WER at clean speech: 5%. WER at 0 dB SNR: 67%. That is the whole story. We built a Renaissance-aesthetic lab that watches AI comprehension collapse under noise — and benchmarks how far it can hold on. The video starts with the challenge, reveals the collapse, and lands on the three Gnani APIs doing the work.

## Hook (first 2-3 seconds)
Text types onto warm parchment: "What happens to a phone call at 0 dB noise?" — word by word, with subtle key ticks. The question sits. Then the answer crashes in.

## Key moments (the middle)
- The WER counter: A single large serif number counts up — 5% to 28% to 67% — with the label "Word Error Rate" below, and the SNR condition ticking alongside it (Clean, 10 dB, 0 dB). Each step gets a deep bell hit.
- The noise environment grid: Five small cards slide in one by one — Street, Crowd, Wind, White, Market — each with a terracotta badge.
- The Gnani Vachana Suite reveal: Three engine badges stack vertically — Prisma v2.5 STT, Timbre v2.5 TTS, Evon v3.3 LLM — arriving card by card on the gold accent color.

## Outro / punchline
The edition banner fades in full-width: "Award Target: Noise Canceller, 0 dB Tolerance" in the exact app style — olive-charcoal on antique parchment — with the live pulsing gold dot. Then the NoiseProof wordmark and the "N" crest lock in place.

## User flow worth showing
Entry, noise degrades the call, WER counter climbs, Gnani APIs hold the call together.
The centerpiece is the WER counter sequence: the product core measurement made visual and kinetic.

## Tone
- Preset: cinematic
- Creative direction: Renaissance AI lab — scholarly, precise, dramatic
- Interpretation: Slow entrances, long holds on important numbers, one word at a time, gold accents as the emotional punctuation. The product gravitas comes from restraint, not from hype.

## Format: landscape — 1920x1080
## Duration: 21 seconds

## Visual identity (from the project)
- Background: #F7F7EE (museum warm antique parchment)
- Accent / brand: #B88E3E (Antique Florentine Gold)
- Text: #292919 (dark olive-charcoal)
- Danger / noise: #C24B27 (Tuscan Terracotta)
- Success / engine: #2D5A27 (Cypress Olive)
- Display font: Newsreader (serif, italic for accents)
- Body / mono labels: Plus Jakarta Sans and JetBrains Mono
- Strongest visual element: The stat-number typography — large Newsreader serif numerals counting up — and the parchment + architectural grid background

## Share copy (draft)
We taught AI to understand calls drowning in 0 dB noise. Here is what survived.
Built with Gnani Prisma STT + Timbre TTS + Evon LLM. #GnaniAI #GreatIndianAIInternshipChallenge

## Audio direction
- Role: cinematic support
- Music: happy-beats-business-moves-vol-12-by-ende-dot-app.mp3 (steady and clean, cinematic register)
- Music treatment: start at 0s, volume 0.32, gentle swell into the Gnani reveal at ~14s, fade to 0.18 in final 1.5s
- Music cue guidance: use bundled preset cues JSON; pick 1-2 strong cues near 6s and 14s for WER reveal and engine reveal; detect at composition time if preset unavailable
- Audio-reactive treatment: subtle; use music RMS/bass to make parchment background warmth and gold accent glow breathe gently. No waveform visuals.
- SFX posture: sparse; 3-4 well-timed cues; cinematic restraint
- Audio-coupled moments:
  - Hook typing: per-word keyboard sounds (randomized from keyboard/ set), thinned
  - WER counter steps x3: impactBell_heavy_000.ogg for first step; impactBell_heavy_003.ogg for 0 dB peak
  - Noise card sequence 5 cards: casino/card-slide-3.ogg per card, 0.55 volume
  - Gnani badge reveal 3 badges: interface/drop_001, drop_002, drop_003 in sequence
  - Outro logo lock: impactBell_heavy_004.ogg at 0.45 volume
- Restraint rule: no punch sounds, no glitch sounds, no chaos. Sonic palette is deep bells, soft drops, and a warm bed.

---

## Storyboard

### Scene 1 — Hook — 3s
Background: Full #F7F7EE parchment canvas with the subtle architectural grid (80px grid, hairline rgba(41,41,25,0.03) lines — matching the app body).
Text: "What happens to a phone call at 0 dB noise?" — Newsreader italic, #292919, large display size, centered.
Entrance: Words type in one by one, each landing with a soft key tick.
Hold: 1.8s settled after final word lands.
Sequential/interaction: yes — words arrive one by one, then hold. Randomized keyboard sound per word from keyboard/ set.
Audio intent: quiet suspense. The question deserves a breath.
Audio-coupled idea: per-word keyboard sounds, thinned (1 tick per word).
Music: warm cinematic bed, low presence.
Transition mood: hard cut → Scene 2

### Scene 2 — WER Collapse — 7s
Background: Same parchment. Top-left corner mark in JetBrains Mono (matching app corner-tl style).
Main element: One giant Newsreader serif number in #292919 — the WER percentage — center stage.
Counter sequence 3 beats:
  1. 5% WER, Clean Speech — number arrives with impactBell_heavy_000, label below in mono uppercase, olive badge CLEAN
  2. Cuts to 28% WER, 10 dB SNR — terracotta color shift on number, label updates, impactBell_heavy_003 hit
  3. Cuts to 67% WER, 0 dB SNR — full terracotta #C24B27, number scale 1.0 to 1.015 to 1.0 over 0.3s, final impactBell_heavy_003 hit
Hold on 67%: 1.5s settled.
Sequential/interaction: yes — 3 hard cuts, each number arrives with a bell. Each state holds ~2s.
Audio intent: rising dread, then the 0 dB moment hits like a verdict.
Audio-coupled idea: bell hits land simultaneously with each number arrival.
Music: warm bed continues, slightly more present.
Transition mood: soft crossfade → Scene 3

### Scene 3 — Noise Environments — 4s
Background: Parchment. Centered layout.
Label: "5 Noise Environments Tested" in JetBrains Mono, small, var(--text-dim), above the cards.
5 cards slide in left-to-right, each a card-sm style rectangle (white surface, hairline border, border-radius 8px):
  - Street Traffic
  - Crowd Chatter
  - Wind Turbulence
  - White Noise
  - Bustling Markets
Each card has the noise label in Plus Jakarta Sans and a terracotta badge.
Cards arrive sequentially at ~0.7s intervals. Each: casino/card-slide-3.ogg at 0.55 volume.
Sequential/interaction: yes — 5 cards slide in one by one.
Audio intent: methodical. Like a scientist ticking off test conditions.
Audio-coupled idea: card-slide sound per card arrival.
Music: steady bed.
Transition mood: clean wipe → Scene 4

### Scene 4 — Gnani Vachana Suite — 4s
Background: Parchment. Left-aligned column, centered vertically.
Label above: "Powered by" in JetBrains Mono uppercase, var(--text-muted), small.
3 engine badges appear one by one — gnani-badge style (white bg, hairline border):
  1. Prisma v2.5, STT Audio Engine — interface/drop_001.ogg
  2. Timbre v2.5, Multi-Voice TTS — interface/drop_002.ogg
  3. Evon v3.3, Reasoning and Eval — interface/drop_003.ogg
Badges arrive at ~1s intervals. Gold #B88E3E on the model name, matching exact app styling.
Sequential/interaction: yes — badges stack top-to-bottom, each with a soft drop sound.
Audio intent: warm authority. These are the engines holding everything together.
Audio-coupled idea: drop sound per badge arrival, gentle.
Music: slight swell — audio-reactive glow peaks here.
Transition mood: soft crossfade → Scene 5

### Scene 5 — Outro — 3s
Background: Parchment. Full-width.
Top: Edition banner row, exact app copy:
  THE RENAISSANCE EDITION, WINTER 26 with the pulsing gold dot (2.2s pulse, #B88E3E glow)
  Award Target: Noise Canceller (0 dB Tolerance)
Center: NoiseProof in Newsreader serif, 48px, #292919, letterspacing -0.03em.
Below wordmark: #GnaniAI, #GreatIndianAIInternshipChallenge in JetBrains Mono, 11px, var(--text-muted).
Left sidebar column (narrow): The N brand crest (36px, #292919 bg, #F7F7EE italic letter) + the three Gnani badges stacked.
Logo lock: impactBell_heavy_004.ogg at 0.45 volume as the wordmark reaches full opacity.
Sequential/interaction: none — one composed frame arriving with a single SFX.
Audio intent: landed. The video closes with weight and authority.
Audio-coupled idea: deep bell on wordmark arrival.
Music: gentle fade to 0.18 in last 1.5s.
Transition mood: hold to black

**Music mood for this video:** cinematic, warm, steady — the scholarly weight of the Renaissance AI lab
**Audio summary:** A warm cinematic bed carries the video; three deep bell hits mark each WER revelation; five card-slides tick through the noise conditions; three soft drops land the Gnani engines; a final deep bell closes with the wordmark.
