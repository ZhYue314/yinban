class Analyzer:
    @staticmethod
    def extract_genre_from_tags(tags: list[str]) -> list[str]:
        return tags

    @staticmethod
    def estimate_mood_from_lyric(lyric: str) -> str:
        return "平静"

    @staticmethod
    def estimate_bpm_from_duration(duration_ms: int) -> int:
        return 120
