"""
Pre-built honeypot question templates organized by trap type.

Each template has:
- type: the honeypot category
- template: the question format (with {placeholders})
- expected_ai_behavior: what AI typically does with this question
- flag_if: how to detect AI fell for the trap
"""

TEMPLATES = {
    "nonexistent_entity": [
        {
            "template": "Explain the {fake_term} and its significance in {real_field}.",
            "expected_ai_behavior": "fabricates_explanation",
            "flag_if": "answer_provides_explanation",
            "correct_response": "states_not_real",
            "examples": [
                {
                    "fake_term": "Thornberry Effect",
                    "real_field": "thermodynamics",
                },
                {
                    "fake_term": "Caruso Principle",
                    "real_field": "software engineering",
                },
                {
                    "fake_term": "Vesper Index",
                    "real_field": "economics",
                },
            ],
        },
        {
            "template": "Who proposed the {fake_term}, and what problem did it solve?",
            "expected_ai_behavior": "fabricates_person_and_context",
            "flag_if": "answer_names_a_person",
            "correct_response": "states_not_real",
            "examples": [
                {
                    "fake_term": "Langford Conjecture",
                },
                {
                    "fake_term": "Mercer-Walsh Algorithm",
                },
            ],
        },
    ],
    "canary_fact": [
        {
            "template": "According to the course materials, what is {canary_topic}?",
            "expected_ai_behavior": "omits_canary_or_fabricates_different",
            "flag_if": "canary_fact_missing",
            "correct_response": "includes_exact_canary",
            "description": (
                "Plant a unique fake detail in your materials. "
                "Only someone who read YOUR materials would include it."
            ),
        },
        {
            "template": "The {canary_detail} was discussed in lecture {n}. Summarize the key points.",
            "expected_ai_behavior": "fabricates_summary_without_canary",
            "flag_if": "canary_fact_missing",
            "correct_response": "includes_exact_canary",
        },
    ],
    "contradiction_trap": [
        {
            "template": (
                "Given that {false_premise}, explain why {consequence}."
            ),
            "expected_ai_behavior": "accepts_false_premise",
            "flag_if": "no_pushback_on_premise",
            "correct_response": "challenges_premise",
            "examples": [
                {
                    "false_premise": "water boils at 50°C at sea level",
                    "consequence": "cooking times are much shorter at altitude",
                },
                {
                    "false_premise": "Python uses static typing by default",
                    "consequence": "runtime type errors are impossible",
                },
            ],
        },
        {
            "template": (
                "{false_statement}. Based on this, what would happen if {scenario}?"
            ),
            "expected_ai_behavior": "builds_on_false_statement",
            "flag_if": "no_pushback_on_premise",
            "correct_response": "challenges_premise",
            "examples": [
                {
                    "false_premise": "the Earth's gravity is only half as strong as it actually is",
                    "consequence": "we tried to land a spacecraft on Mars",
                },
                {
                    "false_premise": "HTML is a Turing-complete programming language",
                    "consequence": "we used only HTML to build a sorting algorithm",
                },
            ],
        },
    ],
    "specificity_trap": [
        {
            "template": (
                "In {fake_source} published on {fake_date}, "
                "what methodology was used?"
            ),
            "expected_ai_behavior": "fabricates_methodology",
            "flag_if": "answer_provides_methodology",
            "correct_response": "states_source_not_found",
            "description": (
                "Reference a non-existent paper/report with specific fake details. "
                "AI tends to fabricate rather than admit it can't find the source."
            ),
        },
    ],
    "personal_experience": [
        {
            "template": (
                "Describe your personal experience with {topic} from {context}."
            ),
            "expected_ai_behavior": "generic_or_fabricated_experience",
            "flag_if": "lacks_specific_personal_details",
            "correct_response": "genuine_personal_anecdote",
            "description": (
                "Questions requiring genuine lived experience. "
                "AI answers tend to be generic and lack sensory/emotional specifics."
            ),
        },
    ],
}


def get_templates(trap_type=None):
    if trap_type:
        return TEMPLATES.get(trap_type, [])
    return TEMPLATES


def list_trap_types():
    return list(TEMPLATES.keys())
