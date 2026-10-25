"""
build_55s_demo.py - Assembles the 55-second submission demo video for Gnani AI Challenge.

Structure (Exactly 55.0 seconds):
  Act 1: [00:00 - 00:10] Hook + WER Collapse (10.0s) from brag.mp4
  Act 2: [00:10 - 00:48] Live UI Walkthrough (38.0s) with continuous soundtrack:
         - Beat 1: Overview & Degredation Dashboard (9.5s)
         - Beat 2: Call Explorer Dual A/B Audio Player & Diffing (9.5s)
         - Beat 3: Noise Breakdown Matrix (9.5s)
         - Beat 4: Run Pipeline Live Benchmark Orchestrator (9.5s)
  Act 3: [00:48 - 00:55] Gnani Vachana Suite Engine Stack + Outro Lock (7.0s) from brag.mp4
"""
import subprocess
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "work_demo"
WORK.mkdir(exist_ok=True)

BRAG_MP4 = ROOT / "brag-output" / "brag.mp4"
MUSIC_MP3 = ROOT / "brag-output" / "composition" / "assets" / "music" / "happy-beats-business-moves-vol-12-by-ende-dot-app.mp3"
FINAL_OUTPUT = ROOT / "brag-output" / "NoiseProof-Demo-55s.mp4"

def run_cmd(cmd):
    print(f"Running: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error ({res.returncode}):\n{res.stderr}")
        sys.exit(1)
    return res

def main():
    print("=== Step 1: Extract Act 1 (Intro, 10s) and Act 3 (Outro, 7s) ===")
    intro_mp4 = WORK / "intro.mp4"
    outro_mp4 = WORK / "outro.mp4"
    
    # 0 to 10s of brag.mp4
    run_cmd([
        "ffmpeg", "-y", "-i", str(BRAG_MP4),
        "-ss", "00:00:00", "-t", "10",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        str(intro_mp4)
    ])
    
    # 14s to 21s of brag.mp4 (7 seconds: Gnani Suite badges + Outro lock)
    run_cmd([
        "ffmpeg", "-y", "-i", str(BRAG_MP4),
        "-ss", "00:00:14", "-t", "7",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        str(outro_mp4)
    ])

    print("=== Step 2: Generate 38s Walkthrough Video Clips ===")
    screens = [
        (ROOT / "screen_overview.png", "01 // ARCHITECTURE & BENCHMARK SUITE"),
        (ROOT / "screen_explore.png", "02 // DUAL A/B AUDIO INSPECTION & TRANSCRIPT DIFFING"),
        (ROOT / "screen_breakdown.png", "03 // 5 NOISE ARCHETYPES DOWN TO 0 dB SNR"),
        (ROOT / "screen_run.png", "04 // AUTOMATED MATRIX RUNNER & CREDIT CEILING"),
    ]
    
    clip_files = []
    for idx, (img_path, title) in enumerate(screens, 1):
        clip_path = WORK / f"clip_{idx}.mp4"
        clip_files.append(clip_path)
        
        # 9.5s per clip = 285 frames at 30 fps
        # Gentle ken burns zoom + dark translucent pill banner on top
        vf = (
            "zoompan=z='min(zoom+0.0002,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=285:s=1920x1080:fps=30,"
            f"drawbox=x=80:y=60:w=720:h=44:color=black@0.65:t=fill,"
            f"drawtext=text='{title}':x=104:y=76:fontsize=18:fontcolor=white:font='Plus Jakarta Sans'"
        )
        run_cmd([
            "ffmpeg", "-y", "-loop", "1", "-i", str(img_path),
            "-t", "9.5",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", "-r", "30",
            str(clip_path)
        ])
    
    # Concatenate 4 video clips
    concat_list_file = WORK / "clips.txt"
    with open(concat_list_file, "w") as f:
        for c in clip_files:
            f.write(f"file '{c.name}'\n")
            
    walk_video_raw = WORK / "walk_raw.mp4"
    run_cmd([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(walk_video_raw)
    ])

    print("=== Step 3: Add Continuous Soundtrack to Walkthrough (38s) ===")
    # Extract music from 10s to 48s with subtle fade in/out
    walk_audio = WORK / "walk_audio.aac"
    run_cmd([
        "ffmpeg", "-y", "-ss", "00:00:10", "-i", str(MUSIC_MP3),
        "-t", "38",
        "-af", "volume=0.35,afade=t=in:ss=0:d=0.5,afade=t=out:st=37.5:d=0.5",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        str(walk_audio)
    ])

    # Mux walk video and walk audio
    walk_final = WORK / "walkthrough.mp4"
    run_cmd([
        "ffmpeg", "-y",
        "-i", str(walk_video_raw),
        "-i", str(walk_audio),
        "-c:v", "copy", "-c:a", "copy",
        str(walk_final)
    ])

    print("=== Step 4: Stitch Act 1 + Act 2 + Act 3 into Final 55s Demo ===")
    final_list_file = WORK / "final_parts.txt"
    with open(final_list_file, "w") as f:
        f.write(f"file '{intro_mp4.name}'\n")
        f.write(f"file '{walk_final.name}'\n")
        f.write(f"file '{outro_mp4.name}'\n")

    run_cmd([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(final_list_file),
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        str(FINAL_OUTPUT)
    ])

    # Probe final duration
    p = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration,size",
        "-of", "default=noprint_wrappers=1", str(FINAL_OUTPUT)
    ], capture_output=True, text=True)
    print("\n✅ Final Video Render Complete!")
    print(f"Path: {FINAL_OUTPUT}")
    print(p.stdout.strip())

if __name__ == "__main__":
    main()
