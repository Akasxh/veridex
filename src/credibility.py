"""Source credibility scoring."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

# Well-known high-credibility domains
_TRUSTED_DOMAINS: dict[str, float] = {
    "nature.com": 0.95, "science.org": 0.95, "sciencedirect.com": 0.90,
    "pubmed.ncbi.nlm.nih.gov": 0.95, "scholar.google.com": 0.85,
    "arxiv.org": 0.85, "ieee.org": 0.90, "acm.org": 0.90,
    "gov": 0.85, "edu": 0.80,
    "reuters.com": 0.85, "apnews.com": 0.85, "bbc.com": 0.80, "bbc.co.uk": 0.80,
    "nytimes.com": 0.80, "washingtonpost.com": 0.78, "theguardian.com": 0.78,
    "wikipedia.org": 0.70, "britannica.com": 0.80,
    "who.int": 0.90, "cdc.gov": 0.90, "nih.gov": 0.90,
    "stackoverflow.com": 0.70, "github.com": 0.65,
}

# Low-credibility indicators
_LOW_CREDIBILITY_PATTERNS = [
    "blogspot", "wordpress.com", "medium.com", "quora.com",
    "reddit.com", "tumblr.com", "pinterest.com",
]


@dataclass
class CredibilityScore:
    """Credibility assessment for a source."""

    url: str
    domain: str
    score: float  # 0.0 - 1.0
    is_https: bool
    is_known_source: bool
    tld_trust: float
    reasons: list[str]

    @property
    def rating(self) -> str:
        if self.score >= 0.8:
            return "High"
        if self.score >= 0.5:
            return "Medium"
        return "Low"


@dataclass
class CredibilityScorer:
    """Score source credibility based on domain heuristics."""

    def score(self, url: str, word_count: int = 0, has_citations: bool = False) -> CredibilityScore:
        """Score a URL's credibility."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower().removeprefix("www.")
        tld = domain.split(".")[-1] if "." in domain else ""
        is_https = parsed.scheme == "https"

        reasons: list[str] = []
        points: float = 0.5  # Base score

        # HTTPS check
        if is_https:
            points += 0.05
            reasons.append("Uses HTTPS")
        else:
            points -= 0.1
            reasons.append("No HTTPS (insecure)")

        # Known trusted domain
        is_known = False
        for trusted, trust_score in _TRUSTED_DOMAINS.items():
            if domain.endswith(trusted) or domain == trusted:
                points = max(points, trust_score)
                is_known = True
                reasons.append(f"Known trusted source: {trusted}")
                break

        # TLD trust
        tld_trust = 0.5
        if tld in ("gov", "edu", "mil"):
            tld_trust = 0.85
            points += 0.15
            reasons.append(f"Trusted TLD: .{tld}")
        elif tld in ("org",):
            tld_trust = 0.65
            points += 0.05
            reasons.append("Organization TLD (.org)")
        elif tld in ("com", "net"):
            tld_trust = 0.5

        # Low credibility patterns
        for pattern in _LOW_CREDIBILITY_PATTERNS:
            if pattern in domain:
                points -= 0.15
                reasons.append(f"User-generated content platform: {pattern}")
                break

        # Content quality signals
        if word_count > 500:
            points += 0.05
            reasons.append("Substantial content (500+ words)")
        elif word_count > 0 and word_count < 100:
            points -= 0.05
            reasons.append("Very short content")

        if has_citations:
            points += 0.05
            reasons.append("Contains citations/references")

        score = max(0.0, min(1.0, points))

        return CredibilityScore(
            url=url,
            domain=domain,
            score=round(score, 2),
            is_https=is_https,
            is_known_source=is_known,
            tld_trust=tld_trust,
            reasons=reasons,
        )
