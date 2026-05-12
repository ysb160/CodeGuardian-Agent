from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional, TypeVar

from pydantic import BaseModel, Field, ValidationError


class RequirementResult(BaseModel):
    task_goal: str = ""
    required_signature: str = ""
    input_output: str = ""
    constraints: list[str] = Field(default_factory=list)
    hidden_cases: list[str] = Field(default_factory=list)
    raw_response: str = ""


class DebuggerResult(BaseModel):
    issues: list[str] = Field(default_factory=list)
    root_causes: list[str] = Field(default_factory=list)
    severity: str = "unknown"
    affected_lines: list[str] = Field(default_factory=list)
    raw_response: str = ""


class FixerResult(BaseModel):
    fixed_code: str = ""
    patch_summary: list[str] = Field(default_factory=list)
    explanation: str = ""
    raw_response: str = ""


class TestCase(BaseModel):
    name: str = ""
    input: str = ""
    expected_output: str = ""
    rationale: str = ""


class ExecutionResult(BaseModel):
    attempted: bool = False
    success: bool = False
    stdout: str = ""
    stderr: str = ""
    returncode: Optional[int] = None
    message: str = "Tests were not run."


class TestAgentResult(BaseModel):
    test_cases: list[TestCase] = Field(default_factory=list)
    execution_result: ExecutionResult = Field(default_factory=ExecutionResult)
    failed_cases: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    runner_code: str = ""
    raw_response: str = ""


class ReviewerResult(BaseModel):
    final_score: int = 0
    checklist: dict[str, bool] = Field(default_factory=dict)
    risks: list[str] = Field(default_factory=list)
    submit_recommendation: str = ""
    raw_response: str = ""


class AnalysisRunResult(BaseModel):
    requirement: RequirementResult
    debugger: DebuggerResult
    fixer: FixerResult
    test: TestAgentResult
    reviewer: ReviewerResult
    markdown_report: str
    report_path: Path


ModelT = TypeVar("ModelT", bound=BaseModel)


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract the first JSON object from plain text or a fenced code block."""
    stripped = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, re.DOTALL)
    candidate = fenced.group(1) if fenced else stripped

    if not candidate.startswith("{"):
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("No JSON object found in model response.")
        candidate = candidate[start : end + 1]

    return json.loads(candidate)


def parse_model_from_text(model_cls: type[ModelT], text: str) -> ModelT:
    """Parse a model response into a Pydantic model, preserving raw text on failure."""
    try:
        data = extract_json_object(text)
        if isinstance(data, dict):
            data.setdefault("raw_response", text)
        return model_cls.model_validate(data)
    except (ValueError, json.JSONDecodeError, ValidationError):
        return model_cls(raw_response=text)
