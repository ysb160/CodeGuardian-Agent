from codeguardian.prompts import build_debugger_prompt, build_requirement_prompt


def test_requirement_prompt_contains_assignment_text():
    prompt = build_requirement_prompt("实现 sumEven")

    assert "实现 sumEven" in prompt
    assert "RequirementAgent" in prompt


def test_debugger_prompt_contains_assignment_and_code():
    prompt = build_debugger_prompt(
        assignment_text="实现 sumEven",
        code_text="int sumEven(vector<int>& nums) { return 0; }",
        error_text="暂无报错",
        language="C++",
    )

    assert "实现 sumEven" in prompt
    assert "int sumEven" in prompt
    assert "暂无报错" in prompt
