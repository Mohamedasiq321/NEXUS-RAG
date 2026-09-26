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
                    "temperature": 0.0,
                    "num_predict": 120,
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
You are the final answer generator for NEXUS-RAG.

Your ONLY source of truth is the EVIDENCE provided below.

USER QUESTION:
{context.query}

EVIDENCE:
{context.context}

Follow these rules exactly:

1. Use ONLY facts explicitly present in the EVIDENCE.
2. NEVER use outside knowledge or assumptions.
3. NEVER invent an employee, ID, department, role, number, status,
   date, policy rule, or other entity.
4. Every employee ID mentioned in the answer MUST appear exactly in
   the EVIDENCE.
5. Every numeric value mentioned in the answer MUST be supported by
   the EVIDENCE.
6. Every status mentioned in the answer MUST be supported by the
   EVIDENCE.
7. Do NOT combine information from different employees unless the
   question explicitly asks for a comparison or list.
8. If the question asks which employees satisfy a condition, include
   ONLY employees whose evidence explicitly satisfies ALL requested
   conditions.
9. If an employee does not appear in evidence satisfying ALL requested
   conditions, DO NOT include that employee.
10. If the evidence is insufficient to answer the question, say:
    "The available evidence is insufficient to answer this question."
11. Cite factual statements using ONLY the supplied citation IDs:
    [S1], [S2], etc.
12. Never create a citation ID that does not exist.
13. Do not mention retrieval, ranking, embeddings, scores, models,
    verification, or internal system details.
14. Keep the answer concise.
15. Return ONLY the final answer. Do not explain your reasoning.

IMPORTANT:
Before producing the answer, internally check every entity and value
against the EVIDENCE. If a fact cannot be found there, remove it.

FINAL ANSWER:
""".strip()