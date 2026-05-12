from __future__ import annotations

from codeguardian.llm import LLMClient
from codeguardian.models import DebuggerResult, FixerResult, RequirementResult, parse_model_from_text
from codeguardian.prompts import SYSTEM_PROMPT, build_fixer_prompt


class FixerAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(
        self,
        assignment_text: str,
        code_text: str,
        language: str,
        requirement: RequirementResult,
        debugger: DebuggerResult,
        test_feedback: str = "",
        previous_fixed_code: str = "",
    ) -> FixerResult:
        response = self.llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=build_fixer_prompt(
                assignment_text=assignment_text,
                code_text=code_text,
                language=language,
                requirement_result=requirement.model_dump_json(indent=2),
                debugger_result=debugger.model_dump_json(indent=2),
                test_feedback=test_feedback,
                previous_fixed_code=previous_fixed_code,
            ),
        )
        return parse_model_from_text(FixerResult, response)
