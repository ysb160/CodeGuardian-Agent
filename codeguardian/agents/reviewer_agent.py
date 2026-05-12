from __future__ import annotations

from codeguardian.llm import LLMClient
from codeguardian.models import (
    DebuggerResult,
    FixerResult,
    RequirementResult,
    ReviewerResult,
    TestAgentResult,
    parse_model_from_text,
)
from codeguardian.prompts import SYSTEM_PROMPT, build_reviewer_prompt


class ReviewerAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(
        self,
        assignment_text: str,
        language: str,
        requirement: RequirementResult,
        debugger: DebuggerResult,
        fixer: FixerResult,
        test: TestAgentResult,
    ) -> ReviewerResult:
        response = self.llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=build_reviewer_prompt(
                assignment_text=assignment_text,
                language=language,
                requirement_result=requirement.model_dump_json(indent=2),
                debugger_result=debugger.model_dump_json(indent=2),
                fixer_result=fixer.model_dump_json(indent=2),
                test_result=test.model_dump_json(indent=2),
            ),
        )
        return parse_model_from_text(ReviewerResult, response)
