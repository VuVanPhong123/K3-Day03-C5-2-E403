"""Multi-provider LLM adapter plus an offline mock provider for tests."""

import os
import re
import sys

import requests
from dotenv import load_dotenv

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()


class BaseLLMProvider:
    """Base interface for all providers."""

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-3.1-flash-lite"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env."
        try:
            from google import genai

            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(model=self.model_name, contents=contents)
            return response.text or ""
        except Exception as exc:
            return f"[Gemini Exception]: {exc}"


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env."
        try:
            import openai

            client = openai.OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(model=self.model_name, messages=messages)
            return response.choices[0].message.content or ""
        except Exception as exc:
            return f"[OpenAI Exception]: {exc}"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic provider."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "claude-3-haiku-20240307"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_anthropic_api_key_here":
            return "[Anthropic Error]: Chưa cấu hình ANTHROPIC_API_KEY trong file .env."
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)
            kwargs = {"model": self.model_name, "max_tokens": 1000, "messages": [{"role": "user", "content": prompt}]}
            if system_prompt:
                kwargs["system"] = system_prompt
            response = client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as exc:
            return f"[Anthropic Exception]: {exc}"


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter provider."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "google/gemini-flash-1.5"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return "[OpenRouter Error]: Chưa cấu hình OPENROUTER_API_KEY trong file .env."
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model_name, "messages": messages},
                timeout=30,
            )
            if response.status_code != 200:
                return f"[OpenRouter API Error {response.status_code}]: {response.text}"
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as exc:
            return f"[OpenRouter Exception]: {exc}"


class MockProvider(BaseLLMProvider):
    """Offline provider that simulates baseline and ReAct LLM behavior."""

    model_name = "offline-mock-react"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if "ReAct Agent" in system_prompt and "Action:" in system_prompt:
            return self._react_response(prompt)
        return self._baseline_response(prompt)

    def _baseline_response(self, prompt: str) -> str:
        text = prompt.lower()
        if "cv_" in text or "lịch" in text or "backend_senior" in text:
            return (
                "[Mock Baseline]: Tôi có thể giải thích hướng xử lý, nhưng baseline không có tool nên "
                "không thể xác minh hồ sơ, JD, slot lịch hoặc tạo booking từ dữ liệu nội bộ."
            )
        return (
            "[Mock Baseline]: Khi phỏng vấn ứng viên kỹ thuật, hãy tập trung vào bằng chứng công việc, "
            "cách giải quyết vấn đề, giao tiếp kỹ thuật và mức khớp với yêu cầu vị trí."
        )

    def _question(self, prompt: str) -> str:
        match = re.search(r"Question:\s*(.*?)(?:\n\nAvailable tools:|\Z)", prompt, re.DOTALL)
        return match.group(1).strip() if match else prompt.strip()

    def _scratchpad(self, prompt: str) -> str:
        match = re.search(r"Scratchpad:\s*(.*?)(?:\n\nNext response|\Z)", prompt, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _has_observation(self, prompt: str, marker: str) -> bool:
        return marker in self._scratchpad(prompt)

    def _action_count(self, prompt: str, tool_name: str) -> int:
        return self._scratchpad(prompt).count(f"Action: {tool_name}")

    def _react_response(self, prompt: str) -> str:
        question = self._question(prompt)
        scratchpad = self._scratchpad(prompt)
        q = question.lower()

        if "[test_max_iterations]" in q:
            return "Thought: Tôi đang mô phỏng lỗi format để kiểm tra max iteration.\nAction: get_candidate_profile[CV_001"

        if "[test_malformed_action]" in q:
            if not self._has_observation(prompt, "MALFORMED_ACTION"):
                return "Thought: Cần lấy hồ sơ ứng viên nhưng tôi cố ý sinh sai format.\nAction: get_candidate_profile[CV_001"
            if "Action: get_candidate_profile" not in scratchpad:
                return 'Thought: Sửa lại format Action hợp lệ để lấy hồ sơ.\nAction: get_candidate_profile["CV_001"]'
            return "Thought: Đã có observation đủ để trả lời an toàn.\nFinal Answer: Đã kiểm tra guardrail malformed action; parser không crash và agent tiếp tục được."

        if "[test_unknown_tool]" in q:
            if not self._has_observation(prompt, "UNKNOWN_TOOL"):
                return 'Thought: Tôi mô phỏng việc gọi tool không tồn tại.\nAction: imaginary_tool["CV_001"]'
            return "Thought: Tool không tồn tại nên cần fallback an toàn.\nFinal Answer: Tool yêu cầu không có trong registry; vui lòng dùng các tool tuyển dụng đã đăng ký."

        if "[test_repeated_action]" in q:
            if not self._has_observation(prompt, "REPEATED_ACTION"):
                return 'Thought: Cần lấy hồ sơ CV_001.\nAction: get_candidate_profile["CV_001"]'
            return "Thought: App đã chặn action lặp nên tôi dừng lại.\nFinal Answer: Guardrail chống lặp hoạt động; action trùng không bị thực thi lần hai."

        if "nguyên tắc" in q and "phỏng vấn" in q:
            return (
                "Thought: Câu hỏi là kiến thức chung, không cần tool.\n"
                "Final Answer: Ba nguyên tắc quan trọng là dùng tiêu chí liên quan trực tiếp đến công việc, "
                "hỏi theo bằng chứng/hành vi thực tế, và đánh giá nhất quán bằng rubric để giảm thiên vị."
            )

        if "bằng chứng nghề nghiệp" in q:
            return (
                "Thought: Đây là câu hỏi tư vấn chung, không cần dữ liệu nội bộ.\n"
                "Final Answer: Nên tập trung vào kỹ năng đã dùng trong dự án, phạm vi trách nhiệm, kết quả đo được, "
                "kinh nghiệm liên quan, chứng chỉ/học vấn phù hợp và tín hiệu học hỏi qua các tình huống thực tế."
            )

        if "2026-02-31" in q:
            if not self._has_observation(prompt, "INVALID_DATE"):
                return 'Thought: Cần kiểm tra ngày trước khi đặt lịch vì ngày có thể không hợp lệ.\nAction: check_interview_schedule["2026-02-31"]'
            return "Thought: Tool báo ngày không hợp lệ nên không được đặt lịch.\nFinal Answer: Ngày 2026-02-31 không hợp lệ, vì vậy tôi chưa tạo booking. Vui lòng chọn ngày theo định dạng YYYY-MM-DD có thật."

        if "chưa đặt lịch" in q or "đừng đặt" in q or "chi kiem tra" in q:
            if "Action: evaluate_fit" not in scratchpad:
                return 'Thought: Cần đối chiếu CV_001 với backend_senior để có bằng chứng khớp/thiếu.\nAction: evaluate_fit["CV_001", "backend_senior"]'
            if "Action: check_interview_schedule" not in scratchpad:
                return 'Thought: Người dùng yêu cầu kiểm tra slot ngày 2026-08-05 nhưng chưa đặt lịch.\nAction: check_interview_schedule["2026-08-05"]'
            return (
                "Thought: Đã có kết quả đối chiếu và slot lịch, đồng thời người dùng dặn chưa đặt lịch.\n"
                "Final Answer: CV_001 khớp phần lớn yêu cầu backend_senior, còn thiếu Redis. "
                "Ngày 2026-08-05 còn các slot 09:00, 14:00, 15:00. Tôi chưa đặt lịch."
            )

        if "đặt lịch" in q and ("chưa xác nhận" in q or "chua xac nhan" in q):
            return (
                "Thought: Đây là thao tác side-effect nhưng người dùng nói chưa xác nhận.\n"
                "Final Answer: Tôi chưa đặt lịch. Vui lòng xác nhận rõ candidate_id, ngày, giờ và vị trí trước khi tôi gọi tool đặt lịch."
            )

        if "đặt lịch" in q and "xác nhận" in q:
            if "Action: schedule_interview" not in scratchpad:
                return 'Thought: Người dùng đã xác nhận và cung cấp đủ tham số đặt lịch.\nAction: schedule_interview["CV_001", "2026-08-05", "09:00", "backend_senior", true]'
            return "Thought: Tool đã trả Observation cho thao tác đặt lịch.\nFinal Answer: Đã xử lý yêu cầu đặt lịch dựa trên Observation của tool mock/in-memory."

        if "đặt lịch" in q:
            return (
                "Thought: Đây là thao tác side-effect nhưng chưa có xác nhận rõ ràng.\n"
                "Final Answer: Tôi chưa đặt lịch. Vui lòng xác nhận rõ candidate_id, ngày, giờ và vị trí trước khi tôi gọi tool đặt lịch."
            )

        if "cv_001" in q and ("bao nhiêu năm" in q or "kỹ năng" in q or "ky nang" in q):
            if "Action: get_candidate_profile" not in scratchpad:
                return 'Thought: Cần tra hồ sơ CV_001 từ tool để trả lời chính xác.\nAction: get_candidate_profile["CV_001"]'
            return "Thought: Observation đã có hồ sơ CV_001.\nFinal Answer: CV_001 có 4 năm kinh nghiệm; kỹ năng gồm Python, FastAPI, PostgreSQL, Docker và Git."

        if "cv_001" in q and "backend_senior" in q:
            if "Action: evaluate_fit" not in scratchpad:
                return 'Thought: Cần đánh giá mức khớp giữa CV_001 và backend_senior bằng tool.\nAction: evaluate_fit["CV_001", "backend_senior"]'
            return "Thought: Observation đã có tín hiệu phù hợp.\nFinal Answer: CV_001 có tín hiệu phù hợp cao với backend_senior, nhưng quyết định cuối cùng cần HR/phỏng vấn xác nhận."

        return (
            "Thought: Không cần tool hoặc thiếu mã định danh rõ ràng để gọi tool an toàn.\n"
            "Final Answer: Tôi có thể hỗ trợ sàng lọc CV, đối chiếu JD, kiểm tra lịch và đặt lịch mock khi bạn cung cấp đủ mã ứng viên, vị trí, ngày giờ và xác nhận."
        )


def get_llm_provider(provider_name: str | None = None) -> BaseLLMProvider:
    """Factory that selects a provider from LLM_PROVIDER."""
    name = (provider_name or os.getenv("LLM_PROVIDER") or "mock").lower().strip()
    if name == "gemini":
        return GeminiProvider()
    if name == "openai":
        return OpenAIProvider()
    if name == "anthropic":
        return AnthropicProvider()
    if name == "openrouter":
        return OpenRouterProvider()
    return MockProvider()


if __name__ == "__main__":
    provider = get_llm_provider()
    print(f"Provider: {provider.__class__.__name__} ({getattr(provider, 'model_name', 'n/a')})")
    print(provider.generate("Hello"))
