from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.agent.answer_context import AnswerContextBuilder
from app.agent.controller import AgentController
from app.generation.generator import AnswerGenerator


controller = AgentController()
builder = AnswerContextBuilder()
generator = AnswerGenerator()


supported_query = (
    "Who is eligible for remote work "
    "and what approval is required for exceptions?"
)

supported_state = controller.run(supported_query)
supported_context = builder.build(supported_state)
supported_answer = generator.generate(supported_context)

print("SUPPORTED QUERY")
print("=" * 90)
print(f"Grounded : {supported_answer.grounded}")
print(f"Citations: {len(supported_answer.citations)}")
print("Answer:")
print(supported_answer.answer)


print("\n" + "=" * 90)

unsupported_query = (
    "What is the company's annual bonus policy?"
)

unsupported_state = controller.run(unsupported_query)
unsupported_context = builder.build(unsupported_state)
unsupported_answer = generator.generate(unsupported_context)

print("UNSUPPORTED QUERY")
print("=" * 90)
print(f"Grounded : {unsupported_answer.grounded}")
print(f"Citations: {len(unsupported_answer.citations)}")
print("Answer:")
print(unsupported_answer.answer)


print("\n" + "=" * 90)
print("Generation service test completed!")