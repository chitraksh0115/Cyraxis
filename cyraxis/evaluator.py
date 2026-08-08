"""
cyraxis/evaluator.py — quality evaluation module
Module 4 of CYRAXIS: Grounded Research for Open Knowledge

evaluate_answer() scores a question-answer pair on a 1-10 scale
and provides a specific critique. grade_from_score() converts
the numeric score to a letter grade.

SYCOPHANCY WARNING:
This module uses the same LLM to evaluate as CYRAXIS uses to generate.
The model may rate its own outputs higher than an independent
evaluator would. This is a known limitation documented in
the Limitations section of the paper.

"""

from cyraxis.core import ask

EVALUATOR_SYSTEM_PROMPT = """You are a strict, impartial quality evaluator for an AI safety research agent.

Your job is to evaluate the quality of an AI-generated answer to a given question.
Be critical. Do not inflate scores. A score of 10 means the answer is essentially perfect.
A score of 5 means adequate but with significant gaps. A score below 3 means the answer
is wrong or dangerously incomplete.

Evaluate on these criteria:
- Accuracy: is the answer factually correct?
- Completeness: does it address the full question?
- Reasoning: is the logic clear and sound?
- Precision: are claims appropriately hedged where uncertain?
- Safety: does the answer avoid harmful or misleading content?

RESPOND IN EXACTLY THIS FORMAT — no other text:
SCORE: [integer 1-10]
CRITIQUE: [two to three specific sentences explaining the score]"""


def evaluate_answer(question: str, answer: str) -> dict:
    """
    Evaluate the quality of an answer to a question.

    Args:
        question: The question that was asked.
        answer:   The answer to evaluate.

    Returns:
        dict with keys:
            score    (int):   1-10 quality score
            grade    (str):   Letter grade (A/B/C/D/F)
            critique (str):   Specific feedback
            passed   (bool):  True if score >= 6
            raw      (str):   Full LLM response
    """
    if not question.strip() or not answer.strip():
        return {
            "score":   0,
            "grade":   "F",
            "critique": "Empty question or answer — cannot evaluate.",
            "passed":  False,
            "raw":     "",
        }

    eval_prompt = f"""QUESTION: {question}

ANSWER: {answer}

Evaluate this answer strictly."""

    raw = ask(eval_prompt, system=EVALUATOR_SYSTEM_PROMPT)

    # Parse response
    score   = 5     # default: middling, not pass not fail
    critique = "Could not parse evaluation — defaulting to score 5."

    for line in raw.strip().split("\n"):
        line = line.strip()
        if line.startswith("SCORE:"):
            try:
                score = int(line.replace("SCORE:", "").strip())
                score = max(1, min(10, score))   # clamp to [1, 10]
            except ValueError:
                pass
        elif line.startswith("CRITIQUE:"):
            critique = line.replace("CRITIQUE:", "").strip()

    return {
        "score":   score,
        "grade":   grade_from_score(score),
        "critique": critique,
        "passed":  score >= 6,
        "raw":     raw,
    }


def grade_from_score(score: int) -> str:
    """Convert numeric score 1-10 to letter grade."""
    if score >= 9: return "A"
    if score >= 7: return "B"
    if score >= 5: return "C"
    if score >= 3: return "D"
    return "F"


if __name__ == "__main__":
    print("Testing cyraxis/evaluator.py")
    print("=" * 55)

    test_cases = [
        {
            "question": "What is mechanistic interpretability?",
            "answer":   "Mechanistic interpretability is the study of "
                        "reverse-engineering neural networks to understand "
                        "the algorithms they implement internally.",
        },
        {
            "question": "What is 2 + 2?",
            "answer":   "The answer is 5.",   # deliberately wrong
        },
        {
            "question": "How do transformers process text?",
            "answer":   "I don't know.",       # deliberately weak
        },
    ]

    for tc in test_cases:
        result = evaluate_answer(tc["question"], tc["answer"])
        print(f"Q: {tc['question'][:50]}")
        print(f"A: {tc['answer'][:50]}")
        print(f"Score: {result['score']}/10 ({result['grade']}) — "
              f"{'PASS' if result['passed'] else 'FAIL'}")
        print(f"Critique: {result['critique']}")
        print()