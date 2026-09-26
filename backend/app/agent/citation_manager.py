import re
from dataclasses import dataclass


@dataclass
class CitationAttachment:
    answer: str
    citations: list[dict]


class CitationManager:
    """
    Attaches citations to generated answer sentences.

    Citation strategy:
    1. Detect explicit structured entities such as employee IDs.
    2. Attach the exact structured evidence containing each entity.
    3. Fall back to deterministic lexical-overlap matching.
    4. Preserve provenance without relying on the LLM for citation selection.

    The LLM generates the answer.
    NEXUS-RAG determines the provenance.
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
    }

    def attach(
        self,
        answer: str,
        citations: list[dict],
    ) -> CitationAttachment:

        if not answer.strip() or not citations:
            return CitationAttachment(
                answer=answer.strip(),
                citations=[],
            )

        sentences = self._split_sentences(answer)

        attached_sentences = []
        used_citations = []

        for sentence in sentences:
            if not sentence.strip():
                continue

            citation_matches = self._find_best_citations(
                sentence,
                citations,
            )

            if citation_matches:
                citation_ids = [
                    citation["citation_id"]
                    for citation in citation_matches
                ]

                citation_suffix = "".join(
                    f"[{citation_id}]"
                    for citation_id in citation_ids
                )

                attached_sentences.append(
                    f"{sentence.strip()} {citation_suffix}"
                )

                for citation in citation_matches:
                    if citation not in used_citations:
                        used_citations.append(citation)

            else:
                attached_sentences.append(sentence.strip())

        return CitationAttachment(
            answer=" ".join(attached_sentences),
            citations=used_citations,
        )

    def _find_best_citations(
        self,
        sentence: str,
        citations: list[dict],
        minimum_score: int = 2,
    ) -> list[dict]:

        # ---------------------------------------------------------
        # 1. Structured entity matching
        # ---------------------------------------------------------
        #
        # Example:
        #
        # "The employees approved are EMP005 and EMP001."
        #
        # If EMP005 and EMP001 appear in the sentence, locate the
        # exact structured rows containing those employee IDs.
        #
        structured_entity_matches = self._find_structured_entity_matches(
            sentence,
            citations,
        )

        if structured_entity_matches:
            return structured_entity_matches

        # ---------------------------------------------------------
        # 2. Standard lexical-overlap matching
        # ---------------------------------------------------------

        sentence_tokens = self._tokenize(sentence)

        scored = []

        for citation in citations:
            evidence_text = " ".join(
                [
                    str(citation.get("section", "")),
                    str(citation.get("content", "")),
                ]
            )

            evidence_tokens = self._tokenize(
                evidence_text
            )

            overlap = sentence_tokens.intersection(
                evidence_tokens,
            )

            score = len(overlap)

            if score >= minimum_score:
                scored.append(
                    (score, citation)
                )

        if not scored:
            return []

        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        best_score = scored[0][0]

        return [
            citation
            for score, citation in scored
            if score == best_score
        ][:2]

    def _find_structured_entity_matches(
        self,
        sentence: str,
        citations: list[dict],
    ) -> list[dict]:
        """
        Finds exact structured evidence for entities explicitly
        mentioned in the generated answer.

        Currently supports employee IDs such as:
        EMP001
        EMP005
        EMP123
        """

        entity_pattern = r"\bEMP\d+\b"

        entities = re.findall(
            entity_pattern,
            sentence.upper(),
        )

        if not entities:
            return []

        matches = []

        for entity in dict.fromkeys(entities):
            for citation in citations:

                if not citation.get(
                    "structured_match",
                    False,
                ):
                    continue

                evidence_text = " ".join(
                    [
                        str(
                            citation.get(
                                "section",
                                "",
                            )
                        ),
                        str(
                            citation.get(
                                "content",
                                "",
                            )
                        ),
                    ]
                ).upper()

                if entity in evidence_text:
                    if citation not in matches:
                        matches.append(citation)

                    break

        return matches

    def _tokenize(
        self,
        text: str,
    ) -> set[str]:

        words = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower(),
        )

        return {
            word
            for word in words
            if word not in self.STOPWORDS
        }

    @staticmethod
    def _split_sentences(
        text: str,
    ) -> list[str]:

        return re.split(
            r"(?<=[.!?])\s+",
            text.strip(),
        )