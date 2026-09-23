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
    Generates grounded answers using a local Ollama model.

    The model receives only the controlled AnswerContext,
    keeping generation grounded in retrieved evidence.
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
                    "temperature": 0.1,
                    "num_predict": 150,
                },
            },
            timeout=300,
        )

        response.raise_for_status()

        data = response.json()

        answer = data["response"].strip()

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
You are the answer-generation component of NEXUS-RAG.

Answer the user's question using ONLY the evidence provided below.

STRICT RULES:
1. Do not use outside knowledge.
2. Do not invent or assume facts.
3. If the evidence does not support a claim, do not make that claim.
4. Answer directly and concisely.
5. Cite factual claims using the supplied citation IDs such as [S1].
6. Only use citation IDs that actually appear in the evidence.
7. Do not mention retrieval scores or internal implementation details.
8. Do not explain your reasoning.
9. Keep the answer to 2-4 concise sentences.
10. If the evidence is insufficient, clearly state that the available
    evidence is insufficient.

USER QUESTION:
{context.query}

EVIDENCE:
{context.context}

Now provide ONLY the final grounded answer.
""".strip()