from __future__ import annotations

from codeguardian.llm import LLMClient
from codeguardian.models import RequirementResult, parse_model_from_text
from codeguardian.prompts import SYSTEM_PROMPT, build_requirement_prompt


class RequirementAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(self, assignment_text: str) -> RequirementResult:
        response = self.llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=build_requirement_prompt(assignment_text),
        )
        return parse_model_from_text(RequirementResult, response)
