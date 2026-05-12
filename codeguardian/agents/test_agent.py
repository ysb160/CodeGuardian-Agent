from __future__ import annotations

from codeguardian.llm import LLMClient
from codeguardian.models import RequirementResult, TestAgentResult, parse_model_from_text
from codeguardian.prompts import SYSTEM_PROMPT, build_test_prompt
from codeguardian.tools.code_runner import run_code

__test__ = False


class TestAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(
        self,
        assignment_text: str,
        fixed_code: str,
        language: str,
        requirement: RequirementResult,
        run_tests: bool,
    ) -> TestAgentResult:
        response = self.llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=build_test_prompt(
                assignment_text=assignment_text,
                fixed_code=fixed_code,
                language=language,
                requirement_result=requirement.model_dump_json(indent=2),
            ),
        )
        result = parse_model_from_text(TestAgentResult, response)
        if not run_tests:
            result.execution_result.message = "Test generation completed; local execution disabled."
            return result

        executable_code = result.runner_code.strip() or fixed_code
        result.execution_result = run_code(executable_code, language=language)
        if result.execution_result.attempted and not result.execution_result.success:
            result.failed_cases.append(result.execution_result.message)
            if result.execution_result.stderr:
                result.failed_cases.append(result.execution_result.stderr)
        return result
