"""Data Lab: Data preparation, deduplication, multilingual profiling, and evaluation dataset tools."""

from __future__ import annotations
import hashlib
from typing import Any, Dict, List


class DataLab:
    """Utilities for cleaning, analyzing, and formatting evaluation & test datasets."""

    def __init__(self, data: list[dict[str, Any]] | None = None):
        self.data: list[dict[str, Any]] = data or []

    def load_samples(self, samples: list[dict[str, Any]]) -> None:
        """Load dataset samples."""
        self.data = list(samples)

    def deduplicate(self, key_field: str = "question") -> tuple[int, int]:
        """Deduplicate records based on text hash of key field.

        Returns (original_count, remaining_count).
        """
        seen_hashes = set()
        unique_records = []
        original_count = len(self.data)

        for item in self.data:
            val = str(item.get(key_field, "")).strip().lower()
            h = hashlib.sha256(val.encode("utf-8")).hexdigest()
            if h not in seen_hashes:
                seen_hashes.add(h)
                unique_records.append(item)

        self.data = unique_records
        return original_count, len(self.data)

    def profile_languages(self, lang_field: str = "language") -> dict[str, int]:
        """Compute distribution across languages."""
        dist: dict[str, int] = {}
        for item in self.data:
            lang = item.get(lang_field, "unknown")
            dist[lang] = dist.get(lang, 0) + 1
        return dist

    def profile_intents(self, intent_field: str = "expected_intent") -> dict[str, int]:
        """Compute distribution across intents."""
        dist: dict[str, int] = {}
        for item in self.data:
            intent = item.get(intent_field, "unknown")
            dist[intent] = dist.get(intent, 0) + 1
        return dist

    def get_summary(self) -> dict[str, Any]:
        """Generate a complete statistical profile of the dataset."""
        return {
            "total_records": len(self.data),
            "languages": self.profile_languages(),
            "intents": self.profile_intents(),
        }
