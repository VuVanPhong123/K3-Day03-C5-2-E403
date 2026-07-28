"""
Level 2: LLM Chatbot Baseline.

Uses natural-language style answers but has no tool access.
This file is an offline demo so it can run without an API key.
"""

import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


CHATBOT_BASELINE_PROMPT = """You are a recruitment assistant in baseline chatbot mode.
You can only answer from information provided in the conversation.
You cannot read real CV files, access ATS data, check calendars, or send emails.
"""


def llm_chatbot(user_input: str) -> str:
    text = user_input.lower()

    if "cv" in text or "ung vien" in text or "phong van" in text:
        return (
            "[LLM Chatbot Baseline]: Toi co the ho tro tom tat/danh gia neu ban dan CV va JD vao chat. "
            "Hien tai toi khong co tool de doc he thong ATS hay kiem tra lich that."
        )

    return f"[LLM Chatbot Baseline]: Toi se tra loi than thien dua tren kien thuc co san cho cau hoi: {user_input}"


if __name__ == "__main__":
    print("=== DEMO LEVEL 2: LLM CHATBOT BASELINE ===")
    query = "CV cua Nguyen Van A co bao nhieu nam kinh nghiem?"
    print(f"User: {query}")
    print(f"Bot : {llm_chatbot(query)}")
