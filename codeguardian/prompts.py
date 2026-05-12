from __future__ import annotations

import json
from typing import Any

from codeguardian.models import (
    DebuggerResult,
    FixerResult,
    RequirementResult,
    ReviewerResult,
    TestAgentResult,
)


SYSTEM_PROMPT = """You are CodeGuardian, a rigorous multi-agent programming assignment assistant.
Return only valid JSON matching the requested schema. Do not wrap JSON in markdown.
Prefer minimal fixes, preserve the student's style, and be concrete about hidden tests."""


def _schema(model: type[Any]) -> str:
    return json.dumps(model.model_json_schema(), ensure_ascii=False, indent=2)


def build_requirement_prompt(assignment_text: str) -> str:
    return f"""Act as RequirementAgent.

Extract the assignment requirements and likely hidden cases.

JSON schema:
{_schema(RequirementResult)}

Assignment:
{assignment_text}
"""


def build_debugger_prompt(
    assignment_text: str,
    code_text: str,
    error_text: str,
    language: str,
) -> str:
    return f"""Act as DebuggerAgent.

Analyze the student's code against the assignment. Classify each issue as syntax, type,
parameter, logic, boundary, or style/format when relevant.

JSON schema:
{_schema(DebuggerResult)}

Language:
{language}

Assignment:
{assignment_text}

Code:
```{language}
{code_text}
```

Error or observed result:
{error_text or "No error text provided."}
"""


def build_fixer_prompt(
    assignment_text: str,
    code_text: str,
    language: str,
    requirement_result: str,
    debugger_result: str,
    test_feedback: str = "",
    previous_fixed_code: str = "",
) -> str:
    refine_block = ""
    if test_feedback or previous_fixed_code:
        refine_block = f"""
Previous fixed code:
```{language}
{previous_fixed_code}
```

Test feedback for refinement:
{test_feedback}
"""

    return f"""Act as FixerAgent.

Produce a minimal corrected version of the full code. Preserve the student's style when possible.
If the assignment asks for a function, keep the required function signature exactly.

JSON schema:
{_schema(FixerResult)}

Language:
{language}

Assignment:
{assignment_text}

RequirementAgent result:
{requirement_result}

DebuggerAgent result:
{debugger_result}

Original code:
```{language}
{code_text}
```
{refine_block}
"""


def build_test_prompt(
    assignment_text: str,
    fixed_code: str,
    language: str,
    requirement_result: str,
) -> str:
    return f"""Act as TestAgent.

Generate 3 to 5 tests covering ordinary cases, edge cases, and likely hidden cases.
If possible, also generate runner_code as a complete executable test program/script that embeds
the fixed code and prints a clear pass/fail summary. Keep runner_code empty if not practical.

JSON schema:
{_schema(TestAgentResult)}

Language:
{language}

Assignment:
{assignment_text}

RequirementAgent result:
{requirement_result}

Fixed code:
```{language}
{fixed_code}
```
"""


def build_reviewer_prompt(
    assignment_text: str,
    language: str,
    requirement_result: str,
    debugger_result: str,
    fixer_result: str,
    test_result: str,
) -> str:
    return f"""Act as ReviewerAgent.

Do a final submission review. Check required signature, input/output, edge cases,
time complexity, space complexity, residual risks, and whether the code is ready to submit.
Give a final_score from 0 to 100.

JSON schema:
{_schema(ReviewerResult)}

Language:
{language}

Assignment:
{assignment_text}

RequirementAgent result:
{requirement_result}

DebuggerAgent result:
{debugger_result}

FixerAgent result:
{fixer_result}

TestAgent result:
{test_result}
"""
