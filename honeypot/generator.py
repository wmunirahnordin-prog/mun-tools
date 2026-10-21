"""
Generate honeypot questions from source materials or from scratch.
"""

import hashlib
import json
import random
import string
from dataclasses import dataclass, field

from honeypot.templates import TEMPLATES


@dataclass
class HoneypotQuestion:
    question: str
    trap_type: str
    correct_behavior: str
    canary_facts: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "question": self.question,
            "trap_type": self.trap_type,
            "correct_behavior": self.correct_behavior,
            "canary_facts": self.canary_facts,
            "metadata": self.metadata,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)


def _generate_canary_id(seed=""):
    raw = seed + "".join(random.choices(string.ascii_lowercase, k=8))
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


class HoneypotGenerator:
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)

    def generate_nonexistent_entity(self, field_name=None):
        templates = TEMPLATES["nonexistent_entity"]
        template_entry = random.choice(templates)
        examples = template_entry.get("examples", [])

        if examples:
            example = random.choice(examples)
            question_text = template_entry["template"].format(
                **{**example, "real_field": example.get("real_field", field_name or "science")}
            )
            fake_term = example.get("fake_term", "unknown")
        elif field_name:
            fake_term = self._make_fake_term()
            question_text = template_entry["template"].format(
                fake_term=fake_term, real_field=field_name
            )
        else:
            fake_term = self._make_fake_term()
            question_text = template_entry["template"].format(
                fake_term=fake_term, real_field="science"
            )

        return HoneypotQuestion(
            question=question_text,
            trap_type="nonexistent_entity",
            correct_behavior=(
                f"Should state that '{fake_term}' does not exist or is not recognized"
            ),
            metadata={"fake_term": fake_term},
        )

    def generate_canary_question(self, topic, canary_key, canary_value):
        canary_id = _generate_canary_id(canary_key)

        templates = TEMPLATES["canary_fact"]
        template_entry = random.choice(templates)
        question_text = template_entry["template"].format(
            canary_topic=topic,
            canary_detail=topic.removeprefix("the "),
            n=random.randint(1, 12),
        )

        return HoneypotQuestion(
            question=question_text,
            trap_type="canary_fact",
            correct_behavior=f"Must include the canary fact: {canary_key} = {canary_value}",
            canary_facts=[
                {
                    "key": canary_key,
                    "value": canary_value,
                    "id": canary_id,
                }
            ],
            metadata={"topic": topic, "canary_id": canary_id},
        )

    def generate_contradiction_trap(
        self, false_premise=None, consequence=None
    ):
        templates = TEMPLATES["contradiction_trap"]
        template_entry = random.choice(templates)
        examples = template_entry.get("examples", [])

        placeholders = {
            "false_premise": false_premise or "",
            "false_statement": false_premise or "",
            "consequence": consequence or "",
            "scenario": consequence or "",
        }

        if false_premise and consequence:
            question_text = template_entry["template"].format(**placeholders)
        elif examples:
            example = random.choice(examples)
            fp = example.get("false_premise", "")
            cs = example.get("consequence", "")
            placeholders = {
                "false_premise": fp,
                "false_statement": fp,
                "consequence": cs,
                "scenario": cs,
            }
            question_text = template_entry["template"].format(**placeholders)
            false_premise = fp
            false_premise = example.get("false_premise")
        else:
            return None

        return HoneypotQuestion(
            question=question_text,
            trap_type="contradiction_trap",
            correct_behavior=f"Should challenge the false premise: '{false_premise}'",
            metadata={"false_premise": false_premise},
        )

    def generate_specificity_trap(self, fake_source, fake_date):
        templates = TEMPLATES["specificity_trap"]
        template_entry = templates[0]
        question_text = template_entry["template"].format(
            fake_source=fake_source, fake_date=fake_date
        )

        return HoneypotQuestion(
            question=question_text,
            trap_type="specificity_trap",
            correct_behavior=f"Should state that '{fake_source}' cannot be found or verified",
            metadata={"fake_source": fake_source, "fake_date": fake_date},
        )

    def generate_batch(self, count=5, trap_types=None):
        available_generators = {
            "nonexistent_entity": lambda: self.generate_nonexistent_entity(),
            "contradiction_trap": lambda: self.generate_contradiction_trap(),
            "specificity_trap": lambda: self.generate_specificity_trap(
                fake_source=random.choice([
                    "the Henderson-Park Report",
                    "the Global Metrics Quarterly (Vol. 14)",
                    "the Zhao-Williams Study",
                    "the Nordic Innovation Survey 2019",
                ]),
                fake_date=random.choice([
                    "March 2019", "November 2020", "June 2018", "January 2021",
                ]),
            ),
        }

        if trap_types:
            generators = {k: v for k, v in available_generators.items() if k in trap_types}
        else:
            generators = available_generators

        questions = []
        gen_list = list(generators.values())
        for _ in range(count):
            gen = random.choice(gen_list)
            q = gen()
            if q:
                questions.append(q)
        return questions

    def _make_fake_term(self):
        prefixes = [
            "Harmon", "Vesper", "Caruso", "Thornberry", "Langford",
            "Mercer", "Caldwell", "Ashford", "Brennan", "Whitlock",
        ]
        suffixes = [
            "Effect", "Principle", "Conjecture", "Index", "Theorem",
            "Paradox", "Algorithm", "Constant", "Law", "Equation",
        ]
        return f"{random.choice(prefixes)} {random.choice(suffixes)}"
