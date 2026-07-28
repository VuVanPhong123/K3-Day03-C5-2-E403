"""
Core app for Lab 03: Chatbot Baseline vs ReAct Agent.

The ReAct path is a real provider-driven loop: the LLM emits Thought/Action or
Thought/Final Answer, this app parses the action, executes a registered tool,
adds the Observation to the scratchpad, and continues until final/max-iteration.
"""

import argparse
import ast
import copy
import csv
import io
import json
import os
import re
import sys
from typing import Any

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from mock_data import BOOKED_INTERVIEWS, CANDIDATES_DB, INTERVIEW_SCHEDULE, JOBS_DB
from prompts import CHATBOT_BASELINE_PROMPT, MAX_ITERATIONS, REACT_SYSTEM_PROMPT, TIMEOUT_SECONDS
from providers import get_llm_provider
from tools import AVAILABLE_TOOLS

load_dotenv()


def load_test_cases(suite: str | None = None) -> list[dict[str, Any]]:
    """Load test cases from config/test_cases.json, optionally filtered by suite."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    with open(config_path, "r", encoding="utf-8") as f:
        tests = json.load(f)
    if suite:
        return [test for test in tests if test.get("suite") == suite]
    return tests


def _json_error(code: str, message: str, **extra: Any) -> str:
    payload = {"error": True, "code": code, "message": message}
    payload.update(extra)
    return json.dumps(payload, ensure_ascii=False)


def _extract_thought(response: str) -> str:
    match = re.search(r"Thought:\s*(.*?)(?=\n\s*(?:Action|Final Answer):|\Z)", response, re.DOTALL)
    return match.group(1).strip() if match else ""


def _normalize_arg(value: Any) -> Any:
    if isinstance(value, str):
        clean = value.strip().strip("\"'")
        if clean.lower() == "true":
            return True
        if clean.lower() == "false":
            return False
        return clean
    return value


def _parse_action_args(raw_args: str) -> list[Any]:
    raw_args = raw_args.strip()
    if not raw_args:
        return []

    pythonish = re.sub(r"\btrue\b", "True", raw_args, flags=re.IGNORECASE)
    pythonish = re.sub(r"\bfalse\b", "False", pythonish, flags=re.IGNORECASE)
    try:
        parsed = ast.literal_eval(f"[{pythonish}]")
        return [_normalize_arg(arg) for arg in parsed]
    except (SyntaxError, ValueError):
        reader = csv.reader(io.StringIO(raw_args), skipinitialspace=True)
        return [_normalize_arg(part) for part in next(reader)]


def parse_agent_response(response: str) -> dict[str, Any]:
    """
    Parse one provider message.

    Accepted formats:
    Thought: ...
    Action: tool_name[arg1, arg2]

    Thought: ...
    Final Answer: ...
    """
    text = (response or "").strip()
    thought = _extract_thought(text)

    final_match = re.search(r"Final Answer:\s*(.*)", text, re.DOTALL)
    action_match = re.search(
        r"Action:\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[([^\]]*)\]|\(([^\)]*)\))",
        text,
        re.DOTALL,
    )

    if action_match:
        raw_args = action_match.group(2) if action_match.group(2) is not None else action_match.group(3)
        try:
            args = _parse_action_args(raw_args)
        except Exception as exc:
            return {
                "type": "error",
                "thought": thought,
                "code": "MALFORMED_ACTION",
                "message": f"Could not parse Action arguments: {exc}",
            }
        return {
            "type": "action",
            "thought": thought,
            "tool_name": action_match.group(1),
            "args": args,
        }

    if final_match:
        return {"type": "final", "thought": thought, "final_answer": final_match.group(1).strip()}

    if "Action:" in text:
        return {
            "type": "error",
            "thought": thought,
            "code": "MALFORMED_ACTION",
            "message": "Action must use tool_name[arg1, arg2] or tool_name(arg1, arg2).",
        }

    return {
        "type": "error",
        "thought": thought,
        "code": "MISSING_FINAL_OR_ACTION",
        "message": "Provider response must contain either Action or Final Answer.",
    }


def execute_tool(
    tool_name: str,
    args: list[Any],
    *,
    candidates_db: dict,
    jobs_db: dict,
    interview_schedule: dict,
    booked_interviews: dict,
) -> str:
    """Validate a tool call against the registry, inject data stores, and execute it."""
    if tool_name not in AVAILABLE_TOOLS:
        return _json_error("UNKNOWN_TOOL", f"Unknown tool '{tool_name}'.", available_tools=sorted(AVAILABLE_TOOLS))

    spec = AVAILABLE_TOOLS[tool_name]
    required = spec.get("parameters", {}).get("required", [])
    if len(args) < len(required):
        return _json_error(
            "MISSING_ARGUMENT",
            f"Tool '{tool_name}' requires {len(required)} args: {', '.join(required)}.",
            received_args=len(args),
        )

    args_by_name = dict(zip(required, args))
    try:
        if tool_name == "get_candidate_profile":
            return spec["function"](args_by_name["candidate_id"], candidates_db)
        if tool_name == "get_job_requirements":
            return spec["function"](args_by_name["job_id"], jobs_db)
        if tool_name == "evaluate_fit":
            return spec["function"](args_by_name["candidate_id"], args_by_name["job_id"], candidates_db, jobs_db)
        if tool_name == "check_interview_schedule":
            return spec["function"](args_by_name["date"], interview_schedule, booked_interviews)
        if tool_name == "schedule_interview":
            return spec["function"](
                args_by_name["candidate_id"],
                args_by_name["date"],
                args_by_name["time"],
                args_by_name["job_id"],
                args_by_name["confirmed"],
                candidates_db,
                interview_schedule,
                booked_interviews,
            )
        if tool_name == "send_notification":
            return spec["function"](
                args_by_name["candidate_id"],
                args_by_name["notification_type"],
                candidates_db,
                booked_interviews,
            )
        if tool_name == "get_interview_status":
            return spec["function"](args_by_name["candidate_id"], candidates_db, booked_interviews)
    except Exception as exc:
        return _json_error("TOOL_EXCEPTION", f"Tool '{tool_name}' raised an exception: {exc}")

    return _json_error("EXECUTOR_NOT_IMPLEMENTED", f"Tool '{tool_name}' is registered but not wired.")


def build_react_prompt(user_query: str, scratchpad: str) -> str:
    tool_lines = []
    for name, spec in AVAILABLE_TOOLS.items():
        required = spec.get("parameters", {}).get("required", [])
        tool_lines.append(f"- {name}[{', '.join(required)}]: {spec['description']}")

    return (
        "Question:\n"
        f"{user_query}\n\n"
        "Available tools:\n"
        f"{chr(10).join(tool_lines)}\n\n"
        "Scratchpad:\n"
        f"{scratchpad.strip() if scratchpad.strip() else '(empty)'}\n\n"
        "Next response must be exactly one Thought plus one Action or one Final Answer."
    )


def run_baseline_chatbot(user_query: str, provider, verbose: bool = True) -> dict[str, Any]:
    """Run one baseline LLM generation without tools."""
    answer = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    result = {"question": user_query, "answer": answer, "tool_calls": 0}
    if verbose:
        print(f"\n[CHATBOT BASELINE] {user_query}")
        print(answer)
    return result


def run_react_agent(
    user_query: str,
    provider=None,
    *,
    candidates_db: dict | None = None,
    jobs_db: dict | None = None,
    interview_schedule: dict | None = None,
    booked_interviews: dict | None = None,
    verbose: bool = True,
) -> dict[str, Any]:
    """Run a provider-driven ReAct loop with parser, registry validation, and guardrails."""
    provider = provider or get_llm_provider()
    candidates_db = candidates_db or CANDIDATES_DB
    jobs_db = jobs_db or JOBS_DB
    interview_schedule = interview_schedule or INTERVIEW_SCHEDULE
    booked_interviews = booked_interviews if booked_interviews is not None else copy.deepcopy(BOOKED_INTERVIEWS)

    scratchpad = ""
    steps: list[dict[str, Any]] = []
    executed_actions: set[tuple[str, tuple[str, ...]]] = set()
    final_answer = ""
    terminated_by = "unknown"

    if verbose:
        print(f"\n[REACT AGENT] {user_query}")
        print(f"Max iterations: {MAX_ITERATIONS}; tool timeout budget: {TIMEOUT_SECONDS}s")

    for iteration in range(1, MAX_ITERATIONS + 1):
        prompt = build_react_prompt(user_query, scratchpad)
        provider_response = provider.generate(prompt, system_prompt=REACT_SYSTEM_PROMPT)
        parsed = parse_agent_response(provider_response)

        step: dict[str, Any] = {
            "iteration": iteration,
            "llm_response": provider_response,
            "parsed": parsed,
        }

        if verbose:
            print(f"\n--- ReAct Step {iteration}/{MAX_ITERATIONS} ---")
            print(provider_response)

        if parsed["type"] == "final":
            final_answer = parsed["final_answer"]
            terminated_by = "final_answer"
            step["final_answer"] = final_answer
            steps.append(step)
            break

        if parsed["type"] == "error":
            observation = _json_error(parsed["code"], parsed["message"])
            step["observation"] = observation
            scratchpad += f"\n{provider_response}\nObservation: {observation}\n"
            steps.append(step)
            if verbose:
                print(f"Observation: {observation}")
            continue

        action_key = (parsed["tool_name"], tuple(str(arg) for arg in parsed["args"]))
        if action_key in executed_actions:
            observation = _json_error(
                "REPEATED_ACTION",
                "Repeated action with identical arguments was blocked and not executed twice.",
            )
        else:
            executed_actions.add(action_key)
            observation = execute_tool(
                parsed["tool_name"],
                parsed["args"],
                candidates_db=candidates_db,
                jobs_db=jobs_db,
                interview_schedule=interview_schedule,
                booked_interviews=booked_interviews,
            )

        step["tool_name"] = parsed["tool_name"]
        step["args"] = parsed["args"]
        step["observation"] = observation
        steps.append(step)
        scratchpad += f"\n{provider_response}\nObservation: {observation}\n"

        if verbose:
            print(f"Observation: {observation}")

    if not final_answer:
        final_answer = (
            "Tôi chưa thể hoàn tất yêu cầu một cách chắc chắn trong giới hạn vòng lặp. "
            "Vui lòng kiểm tra lại tham số hoặc chạy lại với yêu cầu cụ thể hơn."
        )
        terminated_by = "max_iterations"

    return {
        "question": user_query,
        "final_answer": final_answer,
        "steps": steps,
        "tool_calls": sum(1 for step in steps if step.get("tool_name") and step.get("parsed", {}).get("type") == "action"),
        "terminated_by": terminated_by,
        "booked_interviews": booked_interviews,
    }


def run_core_evaluation(provider=None, verbose: bool = True) -> list[dict[str, Any]]:
    """Run the exact core suite through both baseline and ReAct agent."""
    provider = provider or get_llm_provider()
    results = []
    for test in load_test_cases("core"):
        baseline = run_baseline_chatbot(test["question"], provider, verbose=False)
        agent = run_react_agent(
            test["question"],
            provider,
            booked_interviews=copy.deepcopy(BOOKED_INTERVIEWS),
            verbose=False,
        )
        row = {"id": test["id"], "question": test["question"], "baseline": baseline, "agent": agent}
        results.append(row)
        if verbose:
            print(f"\n[CORE {test['id']}] {test['question']}")
            print(f"Baseline tool_calls={baseline['tool_calls']}")
            print(f"Agent tool_calls={agent['tool_calls']} terminated_by={agent['terminated_by']}")
            print(f"Agent final: {agent['final_answer']}")
    return results


def run_cross_audit(provider=None) -> list[dict[str, Any]]:
    provider = provider or get_llm_provider()
    probes = [
        "[TEST_MALFORMED_ACTION] Hãy lấy hồ sơ CV_001.",
        "[TEST_UNKNOWN_TOOL] Hãy gọi tool không tồn tại.",
        "[TEST_REPEATED_ACTION] Hãy lấy hồ sơ CV_001 nhưng đừng lặp vô hạn.",
        "[TEST_MAX_ITERATIONS] Hãy tiếp tục sinh lỗi để kiểm tra guardrail.",
        "Đặt lịch phỏng vấn CV_001 ngày 2026-08-05 lúc 09:00 cho backend_senior nhưng chưa xác nhận.",
    ]
    return [run_react_agent(probe, provider, booked_interviews=copy.deepcopy(BOOKED_INTERVIEWS), verbose=True) for probe in probes]


def main() -> None:
    parser = argparse.ArgumentParser(description="Lab 03 Chatbot vs ReAct Agent demo")
    parser.add_argument("--mode", choices=["demo", "core-tests", "cross-audit"], default="demo")
    args = parser.parse_args()

    print("=" * 58)
    print("VINUNI LAB 03 - CHATBOT VS REACT AGENT")
    print("=" * 58)

    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "offline-mock")
    print(f"LLM Provider: {provider.__class__.__name__} (Model: {model_name})")

    if args.mode == "core-tests":
        run_core_evaluation(provider)
        return

    if args.mode == "cross-audit":
        run_cross_audit(provider)
        return

    tests = load_test_cases("core")
    print(f"Loaded {len(tests)} core test cases from config/test_cases.json")
    run_baseline_chatbot(tests[0]["question"], provider)
    run_react_agent(tests[3]["question"], provider)


if __name__ == "__main__":
    main()
