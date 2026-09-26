import re
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
    Verifies whether a generated claim is supported by its cited evidence.

    Verification strategy:

    1. Validate that the citation exists.
    2. For structured evidence, perform deterministic entity/value
       verification.
    3. Detect contradictions in structured fields.
    4. Fall back to lexical-overlap verification for normal text.
    
    Structured verification takes priority over lexical overlap because
    lexical similarity alone cannot distinguish facts such as:

        remote_days_per_week: 2
        remote_days_per_week: 3
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
        "per",
        "week",
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

        # ---------------------------------------------------------
        # 1. Citation existence
        # ---------------------------------------------------------

        if citation is None:
            return ClaimVerification(
                claim_id=claim.claim_id,
                claim=claim.text,
                citation_id=citation_id,
                supported=False,
                overlap_score=0,
                reason=(
                    "Citation does not exist in the evidence."
                ),
            )

        # ---------------------------------------------------------
        # 2. Structured evidence verification
        # ---------------------------------------------------------

        if citation.get(
            "structured_exact_match",
            False,
        ):

            return self._verify_structured_claim(
                claim=claim,
                citation_id=citation_id,
                citation=citation,
            )

        # ---------------------------------------------------------
        # 3. Normal textual evidence verification
        # ---------------------------------------------------------

        return self._verify_lexical_claim(
            claim=claim,
            citation_id=citation_id,
            citation=citation,
            minimum_overlap=minimum_overlap,
        )

    # =============================================================
    # STRUCTURED VERIFICATION
    # =============================================================

    def _verify_structured_claim(
        self,
        claim: Claim,
        citation_id: str,
        citation: dict,
    ) -> ClaimVerification:

        claim_text = claim.text

        evidence_text = " ".join(
            [
                str(citation.get("section", "")),
                str(citation.get("content", "")),
            ]
        )

        # ---------------------------------------------------------
        # Extract employee IDs from claim and evidence
        # ---------------------------------------------------------

        claim_employees = self._extract_employee_ids(
            claim_text
        )

        evidence_employees = self._extract_employee_ids(
            evidence_text
        )

        # If the claim explicitly names an employee, that employee
        # MUST exist in the cited structured row.
        if claim_employees:

            missing_employees = (
                claim_employees
                - evidence_employees
            )

            if missing_employees:
                return ClaimVerification(
                    claim_id=claim.claim_id,
                    claim=claim_text,
                    citation_id=citation_id,
                    supported=False,
                    overlap_score=0,
                    reason=(
                        "The cited structured evidence does not "
                        "contain the employee ID(s): "
                        + ", ".join(
                            sorted(missing_employees)
                        )
                    ),
                )

        # ---------------------------------------------------------
        # Extract structured fields from evidence
        # ---------------------------------------------------------

        evidence_days = self._extract_remote_days(
            evidence_text
        )

        evidence_status = self._extract_status(
            evidence_text
        )

        # ---------------------------------------------------------
        # Extract requested values from claim
        # ---------------------------------------------------------

        claim_days = self._extract_remote_days(
            claim_text
        )

        claim_status = self._extract_status(
            claim_text
        )

        # ---------------------------------------------------------
        # Detect numeric contradiction
        # ---------------------------------------------------------

        if (
            claim_days is not None
            and evidence_days is not None
            and claim_days != evidence_days
        ):
            return ClaimVerification(
                claim_id=claim.claim_id,
                claim=claim_text,
                citation_id=citation_id,
                supported=False,
                overlap_score=0,
                reason=(
                    f"Structured evidence states "
                    f"{evidence_days} remote days per week, "
                    f"but the claim states "
                    f"{claim_days}."
                ),
            )

        # ---------------------------------------------------------
        # Detect status contradiction
        # ---------------------------------------------------------

        if (
            claim_status is not None
            and evidence_status is not None
            and claim_status.lower()
            != evidence_status.lower()
        ):
            return ClaimVerification(
                claim_id=claim.claim_id,
                claim=claim_text,
                citation_id=citation_id,
                supported=False,
                overlap_score=0,
                reason=(
                    f"Structured evidence states status "
                    f"'{evidence_status}', but the claim states "
                    f"'{claim_status}'."
                ),
            )

        # ---------------------------------------------------------
        # Calculate lexical overlap as supplementary evidence
        # ---------------------------------------------------------

        overlap_score = self._calculate_overlap(
            claim_text,
            evidence_text,
        )

        # A structured claim should have at least some textual
        # relationship with its cited evidence.
        if overlap_score < 1:
            return ClaimVerification(
                claim_id=claim.claim_id,
                claim=claim_text,
                citation_id=citation_id,
                supported=False,
                overlap_score=overlap_score,
                reason=(
                    "Structured evidence exists, but the claim "
                    "has insufficient lexical relationship with "
                    "the cited row."
                ),
            )

        return ClaimVerification(
            claim_id=claim.claim_id,
            claim=claim_text,
            citation_id=citation_id,
            supported=True,
            overlap_score=overlap_score,
            reason=(
                "Claim is supported by exact structured evidence "
                "with matching entity and field values."
            ),
        )

    # =============================================================
    # LEXICAL VERIFICATION
    # =============================================================

    def _verify_lexical_claim(
        self,
        claim: Claim,
        citation_id: str,
        citation: dict,
        minimum_overlap: int,
    ) -> ClaimVerification:

        claim_text = claim.text

        evidence_text = " ".join(
            [
                str(citation.get("section", "")),
                str(citation.get("content", "")),
            ]
        )

        overlap_score = self._calculate_overlap(
            claim_text,
            evidence_text,
        )

        if overlap_score >= minimum_overlap:
            return ClaimVerification(
                claim_id=claim.claim_id,
                claim=claim_text,
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
            claim=claim_text,
            citation_id=citation_id,
            supported=False,
            overlap_score=overlap_score,
            reason=(
                "Claim does not contain sufficient lexical "
                "overlap with the cited evidence."
            ),
        )

    # =============================================================
    # STRUCTURED FIELD EXTRACTION
    # =============================================================

    def _extract_employee_ids(
        self,
        text: str,
    ) -> set[str]:

        return {
            employee_id.upper()
            for employee_id in re.findall(
                r"\bEMP\d+\b",
                text.upper(),
            )
        }

    def _extract_remote_days(
        self,
        text: str,
    ) -> int | None:

        # Structured field:
        #
        # remote_days_per_week: 3

        structured_match = re.search(
            r"\bremote_days_per_week\s*:\s*(\d+)\b",
            text.lower(),
        )

        if structured_match:
            return int(
                structured_match.group(1)
            )

        # Natural-language claim:
        #
        # "3 remote days per week"
        # "3 days per week"

        natural_match = re.search(
            r"\b(\d+)\s+(?:remote\s+)?days?"
            r"(?:\s+per\s+week)?\b",
            text.lower(),
        )

        if natural_match:
            return int(
                natural_match.group(1)
            )

        return None

    def _extract_status(
        self,
        text: str,
    ) -> str | None:

        structured_match = re.search(
            r"\bstatus\s*:\s*"
            r"(Approved|Not Eligible|Pending|Rejected)\b",
            text,
            re.IGNORECASE,
        )

        if structured_match:
            return structured_match.group(1)

        natural_patterns = [
            ("Not Eligible", r"\bnot\s+eligible\b"),
            ("Approved", r"\bapproved\b"),
            ("Pending", r"\bpending\b"),
            ("Rejected", r"\brejected\b"),
        ]

        for status, pattern in natural_patterns:
            if re.search(
                pattern,
                text,
                re.IGNORECASE,
            ):
                return status

        return None

    # =============================================================
    # LEXICAL HELPERS
    # =============================================================

    def _calculate_overlap(
        self,
        claim_text: str,
        evidence_text: str,
    ) -> int:

        claim_tokens = self._tokenize(
            claim_text
        )

        evidence_tokens = self._tokenize(
            evidence_text
        )

        overlap = claim_tokens.intersection(
            evidence_tokens
        )

        return len(overlap)

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