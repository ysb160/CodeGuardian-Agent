from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from codeguardian.models import ExecutionResult


def run_code(code: str, language: str, timeout_seconds: int = 5) -> ExecutionResult:
    normalized = language.strip().lower()
    if normalized in {"python", "py"}:
        return _run_python(code, timeout_seconds)
    if normalized in {"c++", "cpp", "cxx"}:
        return _run_cpp(code, timeout_seconds)
    return ExecutionResult(
        attempted=False,
        success=False,
        message=f"Local execution for language '{language}' is not supported yet.",
    )


def _run_python(code: str, timeout_seconds: int) -> ExecutionResult:
    with tempfile.TemporaryDirectory(prefix="codeguardian_py_") as tmp:
        source = Path(tmp) / "main.py"
        source.write_text(code, encoding="utf-8")
        try:
            completed = subprocess.run(
                [sys.executable, str(source)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return ExecutionResult(
                attempted=True,
                success=False,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                message=f"Python execution timed out after {timeout_seconds} seconds.",
            )

    return ExecutionResult(
        attempted=True,
        success=completed.returncode == 0,
        stdout=completed.stdout,
        stderr=completed.stderr,
        returncode=completed.returncode,
        message="Python tests passed." if completed.returncode == 0 else "Python tests failed.",
    )


def _run_cpp(code: str, timeout_seconds: int) -> ExecutionResult:
    compiler = shutil.which("g++")
    if compiler is None:
        return ExecutionResult(
            attempted=True,
            success=False,
            message="g++ was not found on this system, so C++ tests could not be run.",
        )

    with tempfile.TemporaryDirectory(prefix="codeguardian_cpp_") as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "main.cpp"
        binary = tmp_path / ("main.exe" if sys.platform.startswith("win") else "main")
        source.write_text(code, encoding="utf-8")

        try:
            compile_result = subprocess.run(
                [compiler, "-std=c++17", str(source), "-o", str(binary)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return ExecutionResult(
                attempted=True,
                success=False,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                message=f"C++ compilation timed out after {timeout_seconds} seconds.",
            )

        if compile_result.returncode != 0:
            return ExecutionResult(
                attempted=True,
                success=False,
                stdout=compile_result.stdout,
                stderr=compile_result.stderr,
                returncode=compile_result.returncode,
                message="C++ compilation failed.",
            )

        try:
            run_result = subprocess.run(
                [str(binary)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return ExecutionResult(
                attempted=True,
                success=False,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                message=f"C++ execution timed out after {timeout_seconds} seconds.",
            )

    return ExecutionResult(
        attempted=True,
        success=run_result.returncode == 0,
        stdout=run_result.stdout,
        stderr=run_result.stderr,
        returncode=run_result.returncode,
        message="C++ tests passed." if run_result.returncode == 0 else "C++ tests failed.",
    )
