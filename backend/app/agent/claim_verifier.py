from dataclasses import dataclass

from app.agent.claim_extractor import Claim


@dataclass
class ClaimVerification:
    claim_id: str
    claim: str
    citation_id: str
    supported: bool
    overlap_score: int
    reason: str


class ClaimVerifier:
    """
    Verifies whether a generated claim is sufficiently supported
    by its cited evidence.

    Initial implementation uses deterministic lexical overlap.
    """

    STOPWORDS = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "to",
        "of",
        "for",
        "in",
        "on",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "this",
        "that",
        "their",
        "they",
        "them",
        "with",
        "may",
        "must",
        "can",
        "who",
        "what",
        "how",
        "from",
        "as",
        "by",
        "it",
        "its",
        "have",
        "has",
        "had",
        "required",
        "provided",
    }

    def verify(
        self,
        claim: Claim,
        citation_id: str,
        citations: list[dict],
        minimum_overlap: int = 3,
    ) -> ClaimVerification:

        citation = next(
            (
                item
                for item in citations
                if item["citation_id"] == citation_id
            ),
            None,
        )

        if citation is None:
            return ClaimVerification(
                claim_id=claim.claim_id,
                claim=claim.text,
                citation_id=citation_id,
                supported=False,
                overlap_score=0,
                reason="Citation does not exist in the evidence.",
            )

        claim_tokens = self._tokenize(claim.text)

        evidence_text = " ".join(
            [
                str(citation.get("section", "")),
                str(citation.get("content", "")),
            ]
        )

        evidence_tokens = self._tokenize(evidence_text)

        overlap = claim_tokens.intersection(
            evidence_tokens,
        )

        overlap_score = len(overlap)

        if overlap_score >= minimum_overlap:
            return ClaimVerification(
                claim_id=claim.claim_id,
                claim=claim.text,
                citation_id=citation_id,
                supported=True,
                overlap_score=overlap_score,
                reason=(
                    "Claim contains sufficient lexical overlap "
                    "with the cited evidence."
                ),
            )

        return ClaimVerification(
            claim_id=claim.claim_id,
            claim=claim.text,
            citation_id=citation_id,
            supported=False,
            overlap_score=overlap_score,
            reason=(
                "Claim does not contain sufficient lexical overlap "
                "with the cited evidence."
            ),
        )

    def _tokenize(self, text: str) -> set[str]:
        import re

        words = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower(),
        )

        return {
            word
            for word in words
            if word not in self.STOPWORDS
        }