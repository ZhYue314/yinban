from pathlib import Path

import edge_tts

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "output"


class TTSEngine:
    def __init__(self, voice: str = "zh-CN-XiaoxiaoNeural"):
        self.voice = voice

    async def speak(self, text: str, filename: str = "podcast.mp3") -> Path:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / filename

        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(str(output_path))

        return output_path

    async def speak_stream(self, text: str):
        communicate = edge_tts.Communicate(text, self.voice)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
