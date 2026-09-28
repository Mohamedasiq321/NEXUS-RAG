
from dataclasses import dataclass

import requests

from app.agent.answer_context import AnswerContext


@dataclass
class LocalGeneratedAnswer:
    answer: str
    citations: list[dict]
    grounded: bool


class OllamaAnswerGenerator:
    """
    Generates concise answers from the controlled evidence context.

    Evidence sufficiency is decided by the NEXUS-RAG agent before
    generation. The local LLM is responsible only for converting
    the supplied evidence into a concise natural-language answer.
    """

    def __init__(
        self,
        model: str = "qwen2.5:1.5b",
        base_url: str = "http://localhost:11434",
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(
        self,
        context: AnswerContext,
    ) -> LocalGeneratedAnswer:

        if not context.grounded:
            return LocalGeneratedAnswer(
                answer=(
                    "I don't have sufficient evidence in the "
                    "available knowledge base to answer this question."
                ),
                citations=[],
                grounded=False,
            )

        prompt = self._build_prompt(context)

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "think": False,
                "options": {
                    "temperature": 0.0,
                    "num_predict": 120,
                },
            },
            timeout=300,
        )

        response.raise_for_status()

        data = response.json()

        answer = data.get("response", "").strip()

        if not answer:
            answer = (
                "The available evidence does not contain "
                "a usable answer."
            )

        return LocalGeneratedAnswer(
            answer=answer,
            citations=context.citations,
            grounded=True,
        )

    @staticmethod
    def _build_prompt(
        context: AnswerContext,
    ) -> str:

        return f"""
You are NEXUS-RAG's answer generator.

Answer the USER QUESTION using ONLY the information in the EVIDENCE.

USER QUESTION:
{context.query}

EVIDENCE:
{context.context}

Instructions:

- Answer the user's question directly.
- Use only facts explicitly stated in the evidence.
- Do not add outside knowledge.
- Do not guess or invent information.
- Keep the answer concise and natural.
- If the question asks "who", identify the relevant people or employees
  only when they are explicitly present in the evidence.
- If the question asks "what", explain the relevant rule or information
  stated in the evidence.
- If the question asks "how many", use only numbers explicitly stated
  in the evidence.
- Preserve important conditions and limitations stated in the evidence.
- Do not discuss retrieval, embeddings, models, verification, or
  internal system processes.
- Do not explain your reasoning.
- Return ONLY the final answer.

Citation rules:
- Use the citation IDs provided in the evidence.
- A citation ID looks like [S1], [S2], or [S3].
- Place the relevant citation ID after the factual statement.
- Never invent a citation ID.

FINAL ANSWER:
""".strip()
