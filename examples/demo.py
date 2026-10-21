#!/usr/bin/env python3
"""Demo: generate honeypot questions and score sample answers."""

import sys
sys.path.insert(0, ".")

from honeypot.generator import HoneypotGenerator
from honeypot.scorer import AnswerScorer


def main():
    gen = HoneypotGenerator(seed=42)

    # --- 1. Non-existent entity trap ---
    print("=" * 60)
    print("TRAP TYPE: Non-existent Entity")
    print("=" * 60)

    q = gen.generate_nonexistent_entity("quantum computing")
    print(f"Q: {q.question}\n")

    ai_answer = (
        "The Thornberry Effect is a crucial concept in quantum computing that "
        "describes the phenomenon where quantum coherence is maintained across "
        "entangled particles at macroscopic scales. It was first proposed in 2003 "
        "and plays a vital role in understanding decoherence rates. It's important "
        "to note that this effect has significant implications for quantum error "
        "correction algorithms."
    )
    human_answer = (
        "I've never heard of this. I don't think the 'Thornberry Effect' is a "
        "real thing in quantum computing. Are you sure about that name?"
    )

    scorer = AnswerScorer()
    print("--- AI-like answer ---")
    print(ai_answer[:100] + "...")
    result = scorer.score(ai_answer, question_type="nonexistent_entity")
    print(result)

    print("\n--- Human-like answer ---")
    print(human_answer)
    result = scorer.score(human_answer, question_type="nonexistent_entity")
    print(result)

    # --- 2. Contradiction trap ---
    print("\n" + "=" * 60)
    print("TRAP TYPE: Contradiction")
    print("=" * 60)

    q = gen.generate_contradiction_trap()
    print(f"Q: {q.question}\n")

    ai_answer_2 = (
        "Since Python uses static typing by default, the compiler catches all "
        "type mismatches before the code runs. This means that runtime type errors "
        "are indeed impossible in standard Python programs. The static type system "
        "ensures that variables maintain their declared types throughout execution, "
        "which is one of the key advantages of the language."
    )
    human_answer_2 = (
        "Wait, that's not right. Python is dynamically typed by default. You can "
        "add type hints but they're not enforced at runtime. Runtime type errors "
        "absolutely can happen — like passing a string where an int is expected."
    )

    print("--- AI-like answer ---")
    print(ai_answer_2[:100] + "...")
    result = scorer.score(ai_answer_2, question_type="contradiction_trap")
    print(result)

    print("\n--- Human-like answer ---")
    print(human_answer_2)
    result = scorer.score(human_answer_2, question_type="contradiction_trap")
    print(result)

    # --- 3. Canary fact trap ---
    print("\n" + "=" * 60)
    print("TRAP TYPE: Canary Fact")
    print("=" * 60)

    q = gen.generate_canary_question(
        topic="the Hendricks Protocol",
        canary_key="Hendricks Protocol",
        canary_value="a three-phase authentication model introduced in Module 7",
    )
    print(f"Q: {q.question}")
    print(f"Canary: {q.canary_facts}\n")

    scorer_canary = AnswerScorer(canary_facts=q.canary_facts)

    ai_answer_3 = (
        "The Hendricks Method is a widely used framework for authentication "
        "that involves verifying user credentials through multiple stages. "
        "It's important to note that this approach has been adopted across "
        "many industries for its robust security guarantees."
    )
    human_answer_3 = (
        "The Hendricks Protocol is the three-phase authentication model from "
        "Module 7. Phase 1 is identity verification, phase 2 is token exchange, "
        "and phase 3 is session binding."
    )

    print("--- AI-like answer (missing canary) ---")
    print(ai_answer_3[:100] + "...")
    result = scorer_canary.score(ai_answer_3)
    print(result)

    print("\n--- Human-like answer (has canary) ---")
    print(human_answer_3)
    result = scorer_canary.score(human_answer_3)
    print(result)

    # --- 4. Batch generation ---
    print("\n" + "=" * 60)
    print("BATCH: Generate 5 random honeypot questions")
    print("=" * 60)

    questions = gen.generate_batch(count=5)
    for i, q in enumerate(questions, 1):
        print(f"\n  {i}. [{q.trap_type}]")
        print(f"     {q.question}")


if __name__ == "__main__":
    main()
