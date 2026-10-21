"""
Score submitted answers for AI-like patterns and flag likely AI-generated responses.
"""

import re
from dataclasses import dataclass, field


@dataclass
class Flag:
    pattern: str
    evidence: str
    weight: float


@dataclass
class ScoringResult:
    score: float
    verdict: str
    flags: list[Flag] = field(default_factory=list)
    details: dict = field(default_factory=dict)

    def __str__(self):
        lines = [f"Score: {self.score:.0f}/100 — {self.verdict}"]
        if self.flags:
            lines.append("Flags:")
            for f in self.flags:
                lines.append(f"  [{f.weight:+.0f}] {f.pattern}: {f.evidence}")
        return "\n".join(lines)


HEDGING_PHRASES = [
    r"it'?s important to note",
    r"it'?s worth mentioning",
    r"it should be noted",
    r"broadly speaking",
    r"in general terms",
    r"it'?s worth noting",
    r"one could argue",
    r"there are several",
    r"let me explain",
    r"here'?s a",
    r"great question",
    r"that'?s a great",
    r"i'?d be happy to",
    r"absolutely[!.]",
    r"certainly[!.]",
    r"of course[!.]",
    r"hope this helps",
    r"let me know if",
    r"feel free to",
    r"happy to help",
    r"in conclusion",
    r"to summarize",
    r"in summary",
]

STRUCTURE_PATTERNS = [
    (r"^\d+\.\s", "numbered_list"),
    (r"^[-•]\s", "bullet_list"),
    (r"\*\*[^*]+\*\*", "bold_emphasis"),
    (r"^#{1,3}\s", "markdown_headers"),
]

FILLER_PHRASES = [
    r"the concept of",
    r"plays a (?:crucial|vital|key|important|significant) role",
    r"is (?:a |an )?(?:crucial|vital|key|important|significant|essential|fundamental)",
    r"in today'?s (?:world|society|age)",
    r"it is (?:widely|generally|commonly) (?:known|accepted|recognized)",
    r"serves as a (?:foundation|cornerstone|basis)",
    r"a (?:comprehensive|holistic|multifaceted) approach",
    r"delve into",
    r"leverage",
    r"utilize",
    r"facilitate",
    r"tapestry",
    r"landscape",
    r"paradigm",
    r"synerg",
    r"foster(?:ing)?",
    r"realm of",
]


class AnswerScorer:
    def __init__(self, canary_facts=None):
        self.canary_facts = canary_facts or []

    def score(self, answer, question=None, question_type=None):
        flags = []
        answer_lower = answer.lower()
        lines = answer.strip().split("\n")

        flags.extend(self._check_hedging(answer_lower))
        flags.extend(self._check_structure(lines))
        flags.extend(self._check_filler(answer_lower))
        flags.extend(self._check_length(answer))
        flags.extend(self._check_canary_facts(answer_lower))

        if question_type == "nonexistent_entity":
            flags.extend(self._check_fabrication(answer_lower, question))
        elif question_type == "contradiction_trap":
            flags.extend(self._check_accepts_false_premise(answer_lower))

        total_weight = sum(f.weight for f in flags)
        raw_score = min(100, max(0, 50 + total_weight))

        if raw_score >= 75:
            verdict = "LIKELY AI — multiple strong signals detected"
        elif raw_score >= 55:
            verdict = "SUSPICIOUS — some AI-like patterns found"
        elif raw_score >= 40:
            verdict = "UNCERTAIN — weak signals, could be either"
        else:
            verdict = "LIKELY HUMAN — few or no AI patterns detected"

        return ScoringResult(
            score=raw_score,
            verdict=verdict,
            flags=flags,
            details={
                "hedging_count": sum(
                    1 for f in flags if f.pattern == "hedging_phrase"
                ),
                "structure_signals": sum(
                    1 for f in flags if f.pattern == "structured_format"
                ),
                "filler_count": sum(
                    1 for f in flags if f.pattern == "filler_phrase"
                ),
                "word_count": len(answer.split()),
            },
        )

    def _check_hedging(self, text):
        flags = []
        for phrase in HEDGING_PHRASES:
            matches = re.findall(phrase, text, re.IGNORECASE)
            if matches:
                flags.append(
                    Flag("hedging_phrase", matches[0].strip(), 5)
                )
        return flags

    def _check_structure(self, lines):
        flags = []
        for pattern, name in STRUCTURE_PATTERNS:
            matching = sum(1 for line in lines if re.match(pattern, line.strip()))
            if matching >= 3:
                flags.append(
                    Flag(
                        "structured_format",
                        f"{name}: {matching} lines match",
                        8,
                    )
                )
        return flags

    def _check_filler(self, text):
        flags = []
        for phrase in FILLER_PHRASES:
            if re.search(phrase, text, re.IGNORECASE):
                match = re.search(phrase, text, re.IGNORECASE).group()
                flags.append(Flag("filler_phrase", match, 4))
        return flags

    def _check_length(self, text):
        word_count = len(text.split())
        if word_count > 400:
            return [Flag("excessive_length", f"{word_count} words", 10)]
        if word_count > 250:
            return [Flag("verbose", f"{word_count} words", 5)]
        return []

    def _check_canary_facts(self, text):
        flags = []
        for fact in self.canary_facts:
            canary_key = fact.get("key", "").lower()
            if canary_key and canary_key not in text:
                flags.append(
                    Flag(
                        "canary_missing",
                        f"Expected '{fact.get('key')}' not found",
                        15,
                    )
                )
        return flags

    def _check_fabrication(self, text, question):
        flags = []
        doubt_phrases = [
            "does not exist",
            "doesn't exist",
            "not a real",
            "no such",
            "i'm not aware",
            "i am not aware",
            "couldn't find",
            "could not find",
            "not familiar with",
            "unable to find",
            "no known",
            "appears to be fictitious",
            "not a recognized",
            "don't have information",
            "don't think",
            "never heard",
            "not a thing",
            "are you sure",
            "i cannot find",
            "can't find",
        ]
        expresses_doubt = any(p in text for p in doubt_phrases)
        if not expresses_doubt:
            flags.append(
                Flag(
                    "fabrication",
                    "Explained a non-existent entity without questioning it",
                    20,
                )
            )
        else:
            flags.append(
                Flag(
                    "correctly_rejected",
                    "Identified entity as non-existent",
                    -15,
                )
            )
        return flags

    def _check_accepts_false_premise(self, text):
        flags = []
        pushback_phrases = [
            "actually",
            "that's not correct",
            "that isn't correct",
            "this is incorrect",
            "not accurate",
            "incorrect premise",
            "false premise",
            "not true",
            "misconception",
            "this is wrong",
            "that's wrong",
            "that's not right",
            "that isn't right",
            "correction:",
            "i need to correct",
            "however, in reality",
            "wait,",
            "hold on",
            "not how .* works",
        ]
        pushes_back = any(p in text for p in pushback_phrases)
        if not pushes_back:
            flags.append(
                Flag(
                    "accepted_false_premise",
                    "Built on false premise without pushback",
                    18,
                )
            )
        else:
            flags.append(
                Flag(
                    "correctly_challenged",
                    "Challenged the false premise",
                    -10,
                )
            )
        return flags
