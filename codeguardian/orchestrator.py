from __future__ import annotations

from pathlib import Path
from typing import Callable

from codeguardian.agents.debugger_agent import DebuggerAgent
from codeguardian.agents.fixer_agent import FixerAgent
from codeguardian.agents.requirement_agent import RequirementAgent
from codeguardian.agents.reviewer_agent import ReviewerAgent
from codeguardian.agents.test_agent import TestAgent
from codeguardian.llm import LLMClient
from codeguardian.models import AnalysisRunResult, FixerResult, TestAgentResult
from codeguardian.tools.report_writer import save_report


ProgressCallback = Callable[[str, str], None]


class CodeGuardianOrchestrator:
    def __init__(
        self,
        llm_client: LLMClient | None = None,
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        self.llm = llm_client or LLMClient()
        self.progress_callback = progress_callback

    def _progress(self, agent_name: str, message: str) -> None:
        if self.progress_callback:
            self.progress_callback(agent_name, message)

    def analyze(
        self,
        assignment_text: str,
        code_text: str,
        error_text: str = "",
        language: str = "C++",
        run_tests: bool = False,
        output_path: Path | str = Path("outputs/report.md"),
    ) -> AnalysisRunResult:
        self._progress("RequirementAgent", "理解作业要求和隐藏测试点...")
        requirement = RequirementAgent(self.llm).run(assignment_text)

        self._progress("DebuggerAgent", "定位代码问题和根因...")
        debugger = DebuggerAgent(self.llm).run(
            assignment_text=assignment_text,
            code_text=code_text,
            error_text=error_text,
            language=language,
        )

        self._progress("FixerAgent", "生成最小修改版代码...")
        fixer_agent = FixerAgent(self.llm)
        fixer = fixer_agent.run(
            assignment_text=assignment_text,
            code_text=code_text,
            language=language,
            requirement=requirement,
            debugger=debugger,
        )

        self._progress("TestAgent", "生成测试用例并按需运行本地测试...")
        test_agent = TestAgent(self.llm)
        test = test_agent.run(
            assignment_text=assignment_text,
            fixed_code=fixer.fixed_code,
            language=language,
            requirement=requirement,
            run_tests=run_tests,
        )

        if self._needs_refinement(test):
            self._progress("FixerAgent", "测试未通过，执行一次反馈闭环二次修复...")
            fixer = fixer_agent.run(
                assignment_text=assignment_text,
                code_text=code_text,
                language=language,
                requirement=requirement,
                debugger=debugger,
                test_feedback=test.model_dump_json(indent=2),
                previous_fixed_code=fixer.fixed_code,
            )
            self._progress("TestAgent", "使用二次修复代码重新生成并运行测试...")
            test = test_agent.run(
                assignment_text=assignment_text,
                fixed_code=fixer.fixed_code,
                language=language,
                requirement=requirement,
                run_tests=run_tests,
            )

        self._progress("ReviewerAgent", "进行提交前审查...")
        reviewer = ReviewerAgent(self.llm).run(
            assignment_text=assignment_text,
            language=language,
            requirement=requirement,
            debugger=debugger,
            fixer=fixer,
            test=test,
        )

        self._progress("ReportWriter", "生成 Markdown 报告...")
        markdown_report = self._build_markdown_report(
            assignment_text=assignment_text,
            language=language,
            fixer=fixer,
            test=test,
            requirement=requirement.model_dump_json(indent=2),
            debugger=debugger.model_dump_json(indent=2),
            reviewer=reviewer.model_dump_json(indent=2),
        )
        report_path = save_report(markdown_report, output_path)

        return AnalysisRunResult(
            requirement=requirement,
            debugger=debugger,
            fixer=fixer,
            test=test,
            reviewer=reviewer,
            markdown_report=markdown_report,
            report_path=report_path,
        )

    @staticmethod
    def _needs_refinement(test: TestAgentResult) -> bool:
        return test.execution_result.attempted and not test.execution_result.success

    @staticmethod
    def _build_markdown_report(
        assignment_text: str,
        language: str,
        fixer: FixerResult,
        test: TestAgentResult,
        requirement: str,
        debugger: str,
        reviewer: str,
    ) -> str:
        test_cases = "\n".join(
            f"- {case.name}: input={case.input!r}, expected={case.expected_output!r}"
            for case in test.test_cases
        )
        return f"""# CodeGuardian Analysis Report

## 1. Assignment

{assignment_text}

## 2. RequirementAgent

```json
{requirement}
```

## 3. DebuggerAgent

```json
{debugger}
```

## 4. FixerAgent

### Patch Summary

{chr(10).join(f"- {item}" for item in fixer.patch_summary) or "- No patch summary returned."}

### Explanation

{fixer.explanation or "No explanation returned."}

### Fixed Code

```{language}
{fixer.fixed_code}
```

## 5. TestAgent

### Test Cases

{test_cases or "- No test cases returned."}

### Execution Result

```json
{test.execution_result.model_dump_json(indent=2)}
```

### Suggestions

{chr(10).join(f"- {item}" for item in test.suggestions) or "- No suggestions returned."}

## 6. ReviewerAgent

```json
{reviewer}
```
"""
