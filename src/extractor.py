"""Key facts extraction using spaCy NLP."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import spacy
from spacy.language import Language


@dataclass
class ExtractedFacts:
    """Extracted facts from text."""

    entities: dict[str, list[str]]  # label -> list of entity texts
    key_phrases: list[str]
    statistics: list[str]  # numbers, percentages, dates mentioned
    claims: list[str]  # sentences that look like factual claims


def _load_spacy_model() -> Language:
    """Load spaCy model, downloading if needed."""
    model_name = "en_core_web_sm"
    try:
        return spacy.load(model_name)
    except OSError:
        from spacy.cli import download
        download(model_name)
        return spacy.load(model_name)


@dataclass
class FactExtractor:
    """Extract structured facts from text using spaCy."""

    max_text_length: int = 100_000
    _nlp: Language | None = field(default=None, init=False, repr=False)

    @property
    def nlp(self) -> Language:
        if self._nlp is None:
            self._nlp = _load_spacy_model()
        return self._nlp

    def _extract_entities(self, doc: spacy.tokens.Doc) -> dict[str, list[str]]:
        entities: dict[str, list[str]] = {}
        seen: set[str] = set()
        for ent in doc.ents:
            text = ent.text.strip()
            key = f"{ent.label_}:{text.lower()}"
            if key in seen or len(text) < 2:
                continue
            seen.add(key)
            label = ent.label_
            if label not in entities:
                entities[label] = []
            entities[label].append(text)
        return entities

    def _extract_key_phrases(self, doc: spacy.tokens.Doc) -> list[str]:
        """Extract noun chunks as key phrases."""
        phrases: list[str] = []
        seen: set[str] = set()
        for chunk in doc.noun_chunks:
            text = chunk.text.strip().lower()
            if len(text) > 3 and text not in seen and len(text.split()) <= 5:
                seen.add(text)
                phrases.append(chunk.text.strip())
        # Sort by frequency/importance (longer phrases first)
        phrases.sort(key=len, reverse=True)
        return phrases[:30]

    def _extract_statistics(self, text: str) -> list[str]:
        """Extract sentences containing numbers, percentages, or dates."""
        patterns = [
            r"[^.]*\d+\.?\d*\s*%[^.]*\.",
            r"[^.]*\$\d+[^.]*\.",
            r"[^.]*\d{4}[^.]*\.",
            r"[^.]*\d+\s*(million|billion|trillion|thousand)[^.]*\.",
        ]
        stats: list[str] = []
        seen: set[str] = set()
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                s = match.group(0).strip()
                if s not in seen and 20 < len(s) < 300:
                    seen.add(s)
                    stats.append(s)
        return stats[:20]

    def _extract_claims(self, doc: spacy.tokens.Doc) -> list[str]:
        """Extract sentences that appear to be factual claims."""
        claim_indicators = {
            "according", "research", "study", "found", "showed",
            "reported", "demonstrated", "revealed", "concluded",
            "evidence", "data", "results", "analysis", "survey",
            "published", "discovered", "confirmed", "estimated",
        }
        claims: list[str] = []
        for sent in doc.sents:
            text = sent.text.strip()
            words = {t.lower_ for t in sent}
            if words & claim_indicators and 30 < len(text) < 400:
                claims.append(text)
        return claims[:15]

    def extract(self, text: str) -> ExtractedFacts:
        """Extract all facts from text."""
        truncated = text[: self.max_text_length]
        doc = self.nlp(truncated)

        return ExtractedFacts(
            entities=self._extract_entities(doc),
            key_phrases=self._extract_key_phrases(doc),
            statistics=self._extract_statistics(truncated),
            claims=self._extract_claims(doc),
        )
