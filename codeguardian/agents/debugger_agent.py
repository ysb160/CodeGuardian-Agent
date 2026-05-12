from __future__ import annotations

from codeguardian.llm import LLMClient
from codeguardian.models import DebuggerResult, parse_model_from_text
from codeguardian.prompts import SYSTEM_PROMPT, build_debugger_prompt


class DebuggerAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(
        self,
        assignment_text: str,
        code_text: str,
        error_text: str,
        language: str,
    ) -> DebuggerResult:
        response = self.llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=build_debugger_prompt(
                assignment_text=assignment_text,
                code_text=code_text,
                error_text=error_text,
                language=language,
            ),
        )
        return parse_model_from_text(DebuggerResult, response)
