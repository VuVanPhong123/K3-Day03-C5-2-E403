"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer / Integrator)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import sys
import re
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import random

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter & Mock Data
from tools import (
    AVAILABLE_TOOLS,
    get_candidate_profile,
    get_job_requirements,
    evaluate_fit,
    check_interview_schedule,
    schedule_interview,
    send_notification,
    get_interview_status
)
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider
from mock_data import CANDIDATES_DB, JOBS_DB, INTERVIEW_SCHEDULE, BOOKED_INTERVIEWS

load_dotenv()


def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def execute_tool(tool_name: str, args: list) -> str:
    """
    Hàm cầu nối thực thi Tool với Dependency Injection (truyền DB vào các hàm).
    """
    try:
        if tool_name == "get_candidate_profile":
            candidate_id = args[0] if args else "CV_001"
            return get_candidate_profile(candidate_id, CANDIDATES_DB)

        elif tool_name == "get_job_requirements":
            job_id = args[0] if args else "backend_senior"
            return get_job_requirements(job_id, JOBS_DB)

        elif tool_name == "evaluate_fit":
            candidate_id = args[0] if len(args) > 0 else "CV_001"
            job_id = args[1] if len(args) > 1 else "backend_senior"
            return evaluate_fit(candidate_id, job_id, CANDIDATES_DB, JOBS_DB)

        elif tool_name == "check_interview_schedule":
            date = args[0] if args else "2026-08-05"
            return check_interview_schedule(date, INTERVIEW_SCHEDULE, BOOKED_INTERVIEWS)

        elif tool_name == "schedule_interview":
            candidate_id = args[0] if len(args) > 0 else "CV_001"
            date = args[1] if len(args) > 1 else "2026-08-05"
            time = args[2] if len(args) > 2 else "10:00"
            job_id = args[3] if len(args) > 3 else "backend_senior"
            return schedule_interview(candidate_id, date, time, job_id, CANDIDATES_DB, INTERVIEW_SCHEDULE, BOOKED_INTERVIEWS)

        elif tool_name == "send_notification":
            candidate_id = args[0] if len(args) > 0 else "CV_001"
            notif_type = args[1] if len(args) > 1 else "interview_scheduled"
            return send_notification(candidate_id, notif_type, CANDIDATES_DB, BOOKED_INTERVIEWS)

        elif tool_name == "get_interview_status":
            candidate_id = args[0] if args else "CV_001"
            return get_interview_status(candidate_id, CANDIDATES_DB, BOOKED_INTERVIEWS)

        else:
            return f"LỖI: Công cụ '{tool_name}' không tồn tại trong Registry."

    except Exception as e:
        return f"LỖI khi gọi tool {tool_name}: {str(e)}"


def parse_action(text: str):
    """
    Trích xuất tên tool và tham số từ chuỗi 'Action: tool_name[arg1, arg2]'
    """
    match = re.search(r'Action:\s*(\w+)\[(.*?)\]', text, re.IGNORECASE)
    if match:
        tool_name = match.group(1).strip()
        raw_args = match.group(2).strip()
        # Tách các argument
        if raw_args:
            args = [a.strip().strip("'\"") for a in raw_args.split(",")]
        else:
            args = []
        return tool_name, args
    return None, []


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT[:120]}...\n")
    
    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot Baseline Phản Hồi:\n{'-'*40}\n{response}\n{'-'*40}")
    return response


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) có Guardrails.
    """
    print(f"\n🧠 [REACT AGENT] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {REACT_SYSTEM_PROMPT[:120]}...\n")
    
    history = f"User Query: {user_query}\n"
    step = 0
    trace_logs = []
    
    while step < MAX_ITERATIONS:
        step += 1
        print(f"--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")
        
        # Gọi LLM với prompt tích lũy history
        full_prompt = history + "\nHãy tiếp tục theo định dạng Thought/Action hoặc Final Answer:"
        response = provider.generate(full_prompt, system_prompt=REACT_SYSTEM_PROMPT)
        
        print(f"🤖 Agent Response:\n{response}")
        trace_logs.append(f"Step {step}:\n{response}")
        
        if "Final Answer:" in response:
            print("\n🏁 RE-ACT LOOP HOÀN THÀNH - ĐÃ CÓ FINAL ANSWER!")
            break
            
        tool_name, args = parse_action(response)
        if tool_name:
            print(f"🛠️ Thực thi Tool: {tool_name} với tham số: {args}")
            observation = execute_tool(tool_name, args)
            print(f"👁️ Observation: {observation}")
            
            history += f"\n{response}\nObservation: {observation}\n"
            trace_logs.append(f"Observation: {observation}")
        else:
            # Nếu LLM chưa ra Action cũng chưa ra Final Answer
            history += f"\n{response}\n"
            
    if step >= MAX_ITERATIONS and "Final Answer:" not in response:
        print(f"\n🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!")
        
    return "\n".join(trace_logs)


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("==================================================")
    
    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")
    
    # Mốc 2: Chạy thử Chatbot Baseline trên 3 câu hỏi ngẫu nhiên từ test_cases.json
    print("==================================================")
    print("🚀 MỐC 2: KIỂM THỬ CHATBOT BASELINE (3 CÂU NGẪU NHIÊN)")
    print("==================================================")
    
    selected_tests = random.sample(tests, min(3, len(tests)))
    for tc in selected_tests:
        print(f"\n📌 [TEST CASE {tc['id']}] ({tc['category']}): {tc['question']}")
        run_baseline_chatbot(tc['question'], provider)
