# mun-tools

Personal toolkit by Munirah Nordin — educator, finance academic, and builder.

## What's here

- **honeypot/** — Question generator and AI answer scorer. Create questions where AI-generated answers are instantly flagged.
- **profile.json** — Structured profile data (experience, skills, education) for use in apps, CVs, and automation.

## Install

```bash
pip install -e .
```

## Quick start

```python
from honeypot import HoneypotGenerator, AnswerScorer

# Generate honeypot questions
gen = HoneypotGenerator()
questions = gen.generate_batch(count=5)

for q in questions:
    print(f"[{q.trap_type}] {q.question}")

# Score an answer
scorer = AnswerScorer()
result = scorer.score(
    "The Thornberry Effect is a crucial concept...",
    question_type="nonexistent_entity"
)
print(result)
# Score: 83/100 — LIKELY AI
```

## CLI

```bash
# Generate questions
python -m honeypot generate --count 5
python -m honeypot generate --type nonexistent_entity --output questions.json

# Score an answer
python -m honeypot score --answer response.txt --type nonexistent_entity
echo "some answer" | python -m honeypot score --answer - --type contradiction_trap

# List trap types
python -m honeypot list-types
```

## Trap types

| Type | How it works | What flags AI |
|---|---|---|
| `nonexistent_entity` | Ask about a fake term/concept | AI fabricates an explanation instead of saying "this doesn't exist" |
| `canary_fact` | Plant unique fake details in your materials | AI omits the canary or fabricates different details |
| `contradiction_trap` | Give a false premise, ask to build on it | AI accepts and builds on it; humans push back |
| `specificity_trap` | Reference a non-existent source with specific details | AI fabricates methodology instead of saying it can't find the source |
| `personal_experience` | Ask about personal/lived experience | AI gives generic answers lacking sensory/emotional specifics |

## Scoring

The scorer checks answers for:

- **Hedging phrases** — "it's important to note", "let me explain", "hope this helps"
- **Structural patterns** — numbered lists, bullet points, markdown headers
- **Filler language** — "plays a crucial role", "in today's world", "delve into"
- **Verbosity** — AI answers tend to be much longer
- **Canary fact presence** — whether planted details appear in the answer
- **Fabrication detection** — explains non-existent things without doubt
- **False premise acceptance** — builds on wrong premises without pushback

Score ranges: 75+ LIKELY AI, 55-74 SUSPICIOUS, 40-54 UNCERTAIN, <40 LIKELY HUMAN.
