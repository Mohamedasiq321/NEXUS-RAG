from openai import OpenAI

from app.agent.answer_context import AnswerContext
from app.generation.config import GENERATION_CONFIG
from app.generation.generator import GeneratedAnswer


class OpenAIAnswerGenerator:
    """
    Generates grounded answers using the OpenAI Responses API.

    The model receives only the user query and the controlled
    evidence context produced by NEXUS-RAG.
    """

    SYSTEM_INSTRUCTIONS = """
You are the answer-generation component of NEXUS-RAG.

Your job is to answer the user's question using ONLY the supplied
evidence.

Rules:
1. Do not use outside knowledge.
2. Do not invent facts.
3. If the evidence does not support an answer, say that the
   available evidence is insufficient.
4. Keep the answer concise and directly address the question.
5. Cite factual claims using the supplied citation IDs such as [S1].
6. Do not create citation IDs that are not present in the evidence.
7. Do not mention internal retrieval scores, embeddings, reranking,
   or implementation details unless the user asks about them.
"""

    def __init__(self):
        api_key = GENERATION_CONFIG["api_key"]

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI(api_key=api_key)

        self.model = GENERATION_CONFIG["model"]

    def generate(
        self,
        context: AnswerContext,
    ) -> GeneratedAnswer:

        if not context.grounded:
            return GeneratedAnswer(
                answer=(
                    "I don't have sufficient evidence in the "
                    "available knowledge base to answer this question."
                ),
                citations=[],
                grounded=False,
            )

        user_input = (
            f"User question:\n"
            f"{context.query}\n\n"
            f"Evidence:\n"
            f"{context.context}\n\n"
            "Answer the user's question using only this evidence."
        )

        response = self.client.responses.create(
            model=self.model,
            instructions=self.SYSTEM_INSTRUCTIONS,
            input=user_input,
        )

        answer = response.output_text.strip()

        return GeneratedAnswer(
            answer=answer,
            citations=context.citations,
            grounded=True,
        )