"""Optional AssemblyAI realtime voice intake for ShiftBridge.

Captures a spoken handover from a microphone, prints finalized turns, and can
persist the transcript for later conversion into a ShiftBridge incident packet.
This is intentionally separate from CALL-E: AssemblyAI handles inbound speech;
CALL-E remains the outbound handover/ownership call.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture a live spoken handover with AssemblyAI")
    parser.add_argument("--output", type=Path, default=Path("handover_transcript.json"))
    parser.add_argument("--sample-rate", type=int, default=16000)
    args = parser.parse_args()

    api_key = os.environ.get("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise RuntimeError("ASSEMBLYAI_API_KEY is not set")

    try:
        import pyaudio
        from assemblyai.streaming.v3 import (
            RealTimeEvents,
            RealTimeParameters,
            RealTimeTranscriber,
            RealTimeTranscriberOptions,
            TurnEvent,
        )
    except ImportError as exc:
        raise RuntimeError(
            "Voice intake extras are missing. Install: pip install assemblyai pyaudio"
        ) from exc

    finalized: list[str] = []

    def on_turn(_: object, event: TurnEvent) -> None:
        text = (event.transcript or "").strip()
        if not text:
            return
        prefix = "FINAL" if event.end_of_turn else "partial"
        print(f"{prefix}: {text}")
        if event.end_of_turn:
            finalized.append(text)

    def on_error(_: object, error: object) -> None:
        print(f"AssemblyAI error: {error}")

    client = RealTimeTranscriber(
        RealTimeTranscriberOptions(),
        api_key=api_key,
    )
    client.on(RealTimeEvents.Turn, on_turn)
    client.on(RealTimeEvents.Error, on_error)
    client.connect(
        RealTimeParameters(
            speech_model="universal-3-5-pro",
            sample_rate=args.sample_rate,
        )
    )

    audio = pyaudio.PyAudio()
    frames_per_buffer = 1600  # 100 ms at 16 kHz
    mic = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=args.sample_rate,
        input=True,
        frames_per_buffer=frames_per_buffer,
    )

    print("Listening. Press Ctrl+C to finish and save finalized turns.")
    try:
        while True:
            client.stream(mic.read(frames_per_buffer, exception_on_overflow=False))
    except KeyboardInterrupt:
        pass
    finally:
        mic.stop_stream()
        mic.close()
        audio.terminate()
        client.disconnect(terminate=True)

    payload = {
        "source": "assemblyai_realtime",
        "speech_model": "universal-3-5-pro",
        "sample_rate": args.sample_rate,
        "turns": finalized,
        "transcript": " ".join(finalized),
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
