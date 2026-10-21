#!/usr/bin/env python3
"""
CLI for generating honeypot questions and scoring answers.

Usage:
    python -m honeypot.cli generate [--count N] [--type TYPE] [--output FILE]
    python -m honeypot.cli score --answer FILE [--type TYPE] [--canary FILE]
    python -m honeypot.cli list-types
"""

import argparse
import json
import sys

from honeypot.generator import HoneypotGenerator
from honeypot.scorer import AnswerScorer
from honeypot.templates import list_trap_types


def cmd_generate(args):
    gen = HoneypotGenerator(seed=args.seed)
    trap_types = [args.type] if args.type else None
    questions = gen.generate_batch(count=args.count, trap_types=trap_types)

    output = [q.to_dict() for q in questions]

    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"Generated {len(questions)} questions → {args.output}")
    else:
        for i, q in enumerate(questions, 1):
            print(f"\n{'='*60}")
            print(f"Question {i} [{q.trap_type}]")
            print(f"{'='*60}")
            print(f"  Q: {q.question}")
            print(f"  Correct behavior: {q.correct_behavior}")
            if q.canary_facts:
                print(f"  Canary facts: {q.canary_facts}")


def cmd_score(args):
    if args.answer == "-":
        answer_text = sys.stdin.read()
    else:
        with open(args.answer) as f:
            answer_text = f.read()

    canary_facts = []
    if args.canary:
        with open(args.canary) as f:
            canary_facts = json.load(f)

    scorer = AnswerScorer(canary_facts=canary_facts)
    result = scorer.score(
        answer_text,
        question_type=args.type,
    )

    print(result)


def cmd_list_types(args):
    for trap_type in list_trap_types():
        print(f"  {trap_type}")


def main():
    parser = argparse.ArgumentParser(
        description="Honeypot question generator and AI answer scorer"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("generate", help="Generate honeypot questions")
    gen_parser.add_argument("--count", "-n", type=int, default=5)
    gen_parser.add_argument("--type", "-t", choices=list_trap_types())
    gen_parser.add_argument("--output", "-o", help="Output JSON file")
    gen_parser.add_argument("--seed", "-s", type=int, help="Random seed")
    gen_parser.set_defaults(func=cmd_generate)

    score_parser = subparsers.add_parser("score", help="Score an answer")
    score_parser.add_argument("--answer", "-a", required=True, help="Answer file or - for stdin")
    score_parser.add_argument("--type", "-t", choices=list_trap_types())
    score_parser.add_argument("--canary", "-c", help="Canary facts JSON file")
    score_parser.set_defaults(func=cmd_score)

    list_parser = subparsers.add_parser("list-types", help="List trap types")
    list_parser.set_defaults(func=cmd_list_types)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
