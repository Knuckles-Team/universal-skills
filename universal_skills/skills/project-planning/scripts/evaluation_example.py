"""
Advanced Evaluation Example

This script demonstrates the core evaluation patterns from the advanced-evaluation skill.
It uses pseudocode that works across Python environments without specific dependencies.
"""

# =============================================================================
# DIRECT SCORING EXAMPLE
# =============================================================================


def direct_scoring_example():
    """
    Direct scoring: Rate a single response against defined criteria.
    Best for objective criteria like accuracy, completeness, instruction following.
    """

    # Removed unused input variables

    criteria = [
        {"name": "Accuracy", "description": "Scientific correctness", "weight": 0.4},
        {
            "name": "Clarity",
            "description": "Understandable for audience",
            "weight": 0.3,
        },
        {
            "name": "Engagement",
            "description": "Interesting and memorable",
            "weight": 0.3,
        },
    ]

    # system_prompt = ... removed because unused in this example
    # user_prompt = ... removed because unused in this example
    pass  # Keep some content in the function body if it becomes empty (it won't here)

    # Expected output structure
    expected_output = {
        "scores": [
            {
                "criterion": "Accuracy",
                "score": 4,
                "evidence": [
                    "Correctly uses analogy",
                    "Mentions spooky action at a distance",
                ],
                "justification": "Core concept is correct, analogy is appropriate",
                "improvement": "Could mention it's a quantum mechanical phenomenon",
            },
            {
                "criterion": "Clarity",
                "score": 5,
                "evidence": ["Simple coin analogy", "No jargon"],
                "justification": "Appropriate for high school level",
                "improvement": "None needed",
            },
            {
                "criterion": "Engagement",
                "score": 4,
                "evidence": ["Magical coins", "Spooky action quote"],
                "justification": "Memorable imagery and Einstein quote",
                "improvement": "Could add a real-world application",
            },
        ],
        "summary": {
            "assessment": "Good explanation suitable for the target audience",
            "strengths": ["Clear analogy", "Age-appropriate language"],
            "weaknesses": ["Could be more comprehensive"],
        },
    }

    # Calculate weighted score
    total_weight = sum(c["weight"] for c in criteria)
    weighted_score = (
        sum(
            s["score"]
            * next(c["weight"] for c in criteria if c["name"] == s["criterion"])
            for s in expected_output["scores"]
        )
        / total_weight
    )

    print(f"Weighted Score: {weighted_score:.2f}/5")
    return expected_output


# =============================================================================
# PAIRWISE COMPARISON WITH POSITION BIAS MITIGATION
# =============================================================================


def pairwise_comparison_example():
    """
    Pairwise comparison: Compare two responses and select the better one.
    Includes position swapping to mitigate position bias.
    Best for subjective preferences like tone, style, persuasiveness.
    """

    prompt = "Explain machine learning to a beginner"

    # response_a = ... removed because unused
    # response_b = ... removed because unused
    pass

    criteria = ["clarity", "accessibility", "accuracy"]

    # system_prompt = ... removed because unused
    pass

    # First pass: A first, B second
    def evaluate_pass(first_response, second_response, first_label, second_label):
        user_prompt = f"""## Original Prompt
{prompt}

## Response {first_label}
{first_response}

## Response {second_label}
{second_response}

## Comparison Criteria
{', '.join(criteria)}

## Output Format
{{
  "comparison": [
    {{"criterion": "clarity", "winner": "A|B|TIE", "reasoning": "..."}}
  ],
  "result": {{
    "winner": "A|B|TIE",
    "confidence": 0.0-1.0,
    "reasoning": "overall reasoning"
  }}
}}"""
        return user_prompt

    # Position bias mitigation protocol
    print("Pass 1: A in first position")
    pass1_result = {"winner": "B", "confidence": 0.8}

    print("Pass 2: B in first position (swapped)")
    pass2_result = {"winner": "A", "confidence": 0.75}  # A because B was first

    # Map pass2 result back (swap labels)
    def map_winner(winner):
        return {"A": "B", "B": "A", "TIE": "TIE"}[winner]

    pass2_mapped = map_winner(pass2_result["winner"])
    print(f"Pass 2 mapped winner: {pass2_mapped}")

    # Check consistency
    consistent = pass1_result["winner"] == pass2_mapped

    if consistent:
        final_result = {
            "winner": pass1_result["winner"],
            "confidence": (pass1_result["confidence"] + pass2_result["confidence"]) / 2,
            "position_consistent": True,
        }
    else:
        final_result = {
            "winner": "TIE",
            "confidence": 0.5,
            "position_consistent": False,
            "bias_detected": True,
        }

    print(f"\nFinal Result: {final_result}")
    return final_result


# =============================================================================
# RUBRIC GENERATION
# =============================================================================


def rubric_generation_example():
    """
    Generate a domain-specific scoring rubric.
    Rubrics reduce evaluation variance by 40-60%.
    """

    criterion_name = "Code Readability"
    # Removed unused metadata variables

    # system_prompt = ... removed because unused
    pass

    # user_prompt = ... removed because unused
    pass

    # Expected rubric structure
    rubric = {
        "criterion": criterion_name,
        "scale": {"min": 1, "max": 5},
        "levels": [
            {
                "score": 1,
                "label": "Poor",
                "description": "Code is difficult to understand without significant effort",
                "characteristics": [
                    "No meaningful variable or function names",
                    "No comments or documentation",
                    "Deeply nested or convoluted logic",
                ],
                "example": "def f(x): return x[0]*x[1]+x[2]",
            },
            {
                "score": 3,
                "label": "Adequate",
                "description": "Code is understandable with some effort",
                "characteristics": [
                    "Most variables have meaningful names",
                    "Basic comments for complex sections",
                    "Logic is followable but could be cleaner",
                ],
                "example": "def calc_total(items): # calculate sum\n    total = 0\n    for i in items: total += i\n    return total",
            },
            {
                "score": 5,
                "label": "Excellent",
                "description": "Code is immediately clear and maintainable",
                "characteristics": [
                    "All names are descriptive and consistent",
                    "Comprehensive documentation",
                    "Clean, modular structure",
                ],
                "example": "def calculate_total_price(items: List[Item]) -> Decimal:\n    '''Calculate the total price of all items.'''\n    return sum(item.price for item in items)",
            },
        ],
        "scoring_guidelines": [
            "Focus on readability, not cleverness",
            "Consider the intended audience (team skill level)",
            "Consistency matters more than style preference",
        ],
        "edge_cases": [
            {
                "situation": "Code uses domain-specific abbreviations",
                "guidance": "Score based on readability for domain experts, not general audience",
            },
            {
                "situation": "Code is auto-generated",
                "guidance": "Apply same standards but note in evaluation",
            },
        ],
    }

    print("Generated Rubric:")
    for level in rubric["levels"]:
        print(f"  {level['score']}: {level['label']} - {level['description']}")

    return rubric


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("DIRECT SCORING EXAMPLE")
    print("=" * 60)
    direct_scoring_example()

    print("\n" + "=" * 60)
    print("PAIRWISE COMPARISON EXAMPLE")
    print("=" * 60)
    pairwise_comparison_example()

    print("\n" + "=" * 60)
    print("RUBRIC GENERATION EXAMPLE")
    print("=" * 60)
    rubric_generation_example()
