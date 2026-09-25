import re
from dataclasses import dataclass


@dataclass
class Claim:
    claim_id: str
    text: str


class ClaimExtractor:
    """
    Extracts factual claim-like sentences from a generated answer.

    Initial implementation is deterministic and model-agnostic.
    """

    def extract(self, answer: str) -> list[Claim]:
        cleaned_answer = " ".join(answer.strip().split())

        if not cleaned_answer:
            return []

        sentences = re.split(
            r"(?<=[.!?])\s+",
            cleaned_answer,
        )

        claims = []

        for index, sentence in enumerate(
            sentences,
            start=1,
        ):
            sentence = sentence.strip()

            if not sentence:
                continue

            # Remove citation markers before evaluating the claim text.
            sentence = re.sub(
    r"\s*\[S\d+\]",
    "",
    sentence,
).strip()
            sentence = re.sub(r"\s+([.!?,])", r"\1", sentence)

            if not sentence:
                continue

            claims.append(
                Claim(
                    claim_id=f"C{index}",
                    text=sentence,
                )
            )

        return claims   