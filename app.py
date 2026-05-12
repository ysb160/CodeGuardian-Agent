from __future__ import annotations

import json

import streamlit as st

from codeguardian.orchestrator import CodeGuardianOrchestrator


st.set_page_config(page_title="CodeGuardian Multi-Agent Debugger", layout="wide")
st.title("CodeGuardian Multi-Agent Debugger")

assignment_text = st.text_area("作业要求", height=180)
code_text = st.text_area("代码", height=260)
error_text = st.text_area("报错信息", height=120)
language = st.selectbox("编程语言", ["C++", "Python", "Java", "Other"])
run_tests = st.checkbox("是否运行测试", value=False)

if st.button("开始分析", type="primary"):
    if not assignment_text.strip() or not code_text.strip():
        st.error("请先填写作业要求和代码。")
    else:
        log_box = st.empty()
        progress_lines: list[str] = []

        def progress(agent_name: str, message: str) -> None:
            progress_lines.append(f"{agent_name}: {message}")
            log_box.info("\n".join(progress_lines))

        try:
            with st.spinner("多 Agent 正在协作分析..."):
                orchestrator = CodeGuardianOrchestrator(progress_callback=progress)
                result = orchestrator.analyze(
                    assignment_text=assignment_text,
                    code_text=code_text,
                    error_text=error_text,
                    language=language,
                    run_tests=run_tests,
                )
        except Exception as exc:  # noqa: BLE001 - UI should show a friendly error.
            st.error(str(exc))
        else:
            st.subheader("RequirementAgent 结果")
            st.json(result.requirement.model_dump())

            st.subheader("DebuggerAgent 结果")
            st.json(result.debugger.model_dump())

            st.subheader("FixerAgent 修复后代码")
            st.code(result.fixer.fixed_code, language=language.lower())
            st.json(
                {
                    "patch_summary": result.fixer.patch_summary,
                    "explanation": result.fixer.explanation,
                }
            )

            st.subheader("TestAgent 测试用例和运行结果")
            st.json(result.test.model_dump())

            st.subheader("ReviewerAgent 最终建议")
            st.json(result.reviewer.model_dump())

            st.download_button(
                "下载 Markdown 报告",
                data=result.markdown_report,
                file_name="report.md",
                mime="text/markdown",
            )

            with st.expander("完整结构化结果"):
                st.code(
                    json.dumps(result.model_dump(), ensure_ascii=False, indent=2),
                    language="json",
                )
