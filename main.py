from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from codeguardian.orchestrator import CodeGuardianOrchestrator
from codeguardian.tools.file_loader import read_optional_text_file, read_text_file


app = typer.Typer(help="CodeGuardian multi-agent programming assignment debugger.", no_args_is_help=True)
console = Console()


@app.callback()
def cli() -> None:
    """CodeGuardian multi-agent programming assignment debugger."""


@app.command()
def analyze(
    assignment: Path = typer.Option(
        ...,
        "--assignment",
        help="Path to the assignment requirement text file.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    code: Path = typer.Option(
        ...,
        "--code",
        help="Path to the current source code file.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    error: Optional[Path] = typer.Option(
        None,
        "--error",
        help="Optional path to compiler/runtime error text.",
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    language: str = typer.Option("C++", "--language", help="Programming language."),
    run_tests: bool = typer.Option(False, "--run-tests", help="Run generated local tests when possible."),
    output: Path = typer.Option(Path("outputs/report.md"), "--output", help="Markdown report output path."),
) -> None:
    """Analyze, fix, test, and review a programming assignment submission."""
    console.print(Panel.fit("CodeGuardian Multi-Agent Debugger", style="bold cyan"))

    assignment_text = read_text_file(assignment)
    code_text = read_text_file(code)
    error_text = read_optional_text_file(error)

    def progress(agent_name: str, message: str) -> None:
        console.print(f"[bold green]{agent_name}[/bold green] {message}")

    try:
        orchestrator = CodeGuardianOrchestrator(progress_callback=progress)
        result = orchestrator.analyze(
            assignment_text=assignment_text,
            code_text=code_text,
            error_text=error_text,
            language=language,
            run_tests=run_tests,
            output_path=output,
        )
    except Exception as exc:  # noqa: BLE001 - CLI should surface a clean failure message.
        console.print(Panel(str(exc), title="Analysis failed", style="bold red"))
        raise typer.Exit(code=1) from exc

    table = Table(title="Final Review")
    table.add_column("Item", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Report", str(result.report_path))
    table.add_row("Score", str(result.reviewer.final_score))
    table.add_row("Submit Recommendation", result.reviewer.submit_recommendation)
    table.add_row("Tests", result.test.execution_result.message)
    console.print(table)


if __name__ == "__main__":
    app()
