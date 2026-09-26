from __future__ import annotations

from ...domain import Category, Priority, TriageResult


class RuleBasedTriage:
    name = 'rules'

    CATEGORY_TERMS: dict[Category, tuple[str, ...]] = {
        Category.WATER: ('water', 'pipe', 'sewer water', 'leak', 'burst', 'pani'),
        Category.ELECTRICITY: ('electric', 'bijli', 'transformer', 'wire', 'power', 'voltage'),
        Category.SANITATION: ('garbage', 'trash', 'waste', 'kachra', 'drain', 'sewerage', 'smell'),
        Category.ROADS: ('road', 'pothole', 'gadda', 'street broken', 'asphalt', 'footpath'),
        Category.STREETLIGHTS: ('streetlight', 'street light', 'lamp', 'light pole'),
    }
    HIGH_TERMS = (
        'flood', 'fire', 'sparking', 'electrocution', 'collapsed', 'accident', 'danger',
        'entering house', 'entering ground floor', 'main burst', 'live wire', 'overflowing badly',
    )
    LOW_TERMS = ('dim', 'minor', 'small crack', 'one light', 'request', 'routine')

    def triage(self, text: str, location: str) -> TriageResult:
        haystack = f'{text} {location}'.lower()
        scores = {
            category: sum(1 for term in terms if term in haystack)
            for category, terms in self.CATEGORY_TERMS.items()
        }
        category = max(scores, key=scores.get) if max(scores.values(), default=0) else Category.OTHER
        if any(term in haystack for term in self.HIGH_TERMS):
            priority = Priority.HIGH
        elif any(term in haystack for term in self.LOW_TERMS):
            priority = Priority.LOW
        else:
            priority = Priority.NORMAL
        summary = ' '.join(text.strip().split())
        if len(summary) > 140:
            summary = summary[:137].rstrip() + '...'
        confidence = 0.92 if category != Category.OTHER else 0.55
        return TriageResult(category=category, priority=priority, summary=summary, confidence=confidence)
