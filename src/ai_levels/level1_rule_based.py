"""
Level 1: Rule-Based Bot.

Fixed if/else keyword matching. No LLM and no tools.
"""

import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def rule_based_bot(user_input: str) -> str:
    text = user_input.lower()

    if "hello" in text or "hi" in text or "chao" in text:
        return "Xin chao! Toi la bot rule-based cap 1."
    if "cv_001" in text or "nguyen van a" in text:
        return "Theo luat co dinh: CV_001 la ung vien backend co kinh nghiem Python."
    if "backend" in text:
        return "Theo luat co dinh: vi tri Backend can Python, API, database va kinh nghiem server-side."
    if "phong van" in text or "lich" in text:
        return "Toi chi co the nhac ban kiem tra lich thu cong, chua goi duoc tool."

    return "Xin loi, cau hoi nam ngoai tap keyword da cai dat san."


if __name__ == "__main__":
    print("=== DEMO LEVEL 1: RULE-BASED BOT ===")
    test_queries = [
        "Chao ban",
        "CV_001 co phu hop backend khong?",
        "Dat lich phong van cho ung vien",
    ]
    for query in test_queries:
        print(f"User: {query}")
        print(f"Bot : {rule_based_bot(query)}\n")
