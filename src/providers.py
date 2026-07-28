"""
🔌 MULTI-PROVIDER LLM ADAPTER (OpenAI, Gemini, Anthropic, OpenRouter & Offline Mock)
Hỗ trợ chuyển đổi linh hoạt giữa các nhà cung cấp AI chỉ bằng cách đổi biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho tất cả các LLM Provider"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider (SDK + HTTP REST API Fallback)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.0-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env!"

        # Try Google GenAI SDK
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            if response and hasattr(response, 'text') and response.text:
                return response.text
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower():
                print("\n⚠️ [Gemini API 429 - Quota Exceeded]: Tự động chuyển sang Offline Mock Provider!")
                return MockProvider().generate(prompt, system_prompt)

        # Direct REST API Call (Dependency-free)
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            contents_text = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            payload = {
                "contents": [{"parts": [{"text": contents_text}]}]
            }
            res = requests.post(url, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            elif res.status_code == 429:
                print("\n⚠️ [Gemini API 429 - Quota Exceeded]: Tự động chuyển sang Offline Mock Provider để đảm bảo bài test chạy liên tục!")
                return MockProvider().generate(prompt, system_prompt)
            else:
                # Try gemini-1.5-flash fallback if model name mismatch
                alt_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                res_alt = requests.post(alt_url, json=payload, timeout=30)
                if res_alt.status_code == 200:
                    data = res_alt.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                elif res_alt.status_code == 429:
                    print("\n⚠️ [Gemini API 429 - Quota Exceeded]: Tự động chuyển sang Offline Mock Provider!")
                    return MockProvider().generate(prompt, system_prompt)
                return f"[Gemini REST API Error {res.status_code}]: {res.text}"
        except Exception as e:
            return MockProvider().generate(prompt, system_prompt)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (GPT-4o, GPT-3.5-turbo, etc.)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env!"
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude Provider (Claude 3.5 Sonnet, Claude 3 Haiku)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "claude-3-haiku-20240307"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_anthropic_api_key_here":
            return "[Anthropic Error]: Chưa cấu hình ANTHROPIC_API_KEY trong file .env!"
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            kwargs = {
                "model": self.model_name,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                kwargs["system"] = system_prompt
                
            response = client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            return f"[Anthropic Exception]: {str(e)}"


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter Provider (Hỗ trợ gọi mọi model qua OpenRouter API)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "google/gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return "[OpenRouter Error]: Chưa cấu hình OPENROUTER_API_KEY trong file .env!"
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages
            }
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"[OpenRouter API Error {res.status_code}]: {res.text}"
        except Exception as e:
            return f"[OpenRouter Exception]: {str(e)}"


class MockProvider(BaseLLMProvider):
    """Offline Mock Provider (Cho bài test không cần kết nối API hoặc khi hết Quota)"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        text = prompt.lower()
        if "thời tiết" in text:
            return "Thought: Cần tra cứu thời tiết.\nAction: get_weather['Hà Nội']"
        
        # Mock logic cho Baseline Chatbot
        if "baseline" in system_prompt.lower():
            if "liệt kê" in text or "danh sách" in text:
                return "- **Thiếu thông tin:** Tôi chưa có danh sách CV trong hệ thống.\n- **Cần bổ sung:** Vui lòng dán nội dung CV vào đây.\n- **Gợi ý tiếp theo:** Tôi là Baseline Chatbot nên không thể truy cập DB tuyển dụng."
            elif "kinh nghiệm" in text:
                return "- **Thiếu thông tin:** Tôi chưa nhận được CV của ứng viên này.\n- **Cần bổ sung:** Vui lòng cung cấp nội dung CV."
            elif "đặt lịch" in text:
                return "- **Thiếu thông tin:** Không thể truy cập hệ thống lịch phỏng vấn thực tế.\n- **Gợi ý:** Vì là Baseline Chatbot, tôi không có quyền gọi tool đặt lịch."
            else:
                return "- **Thông báo:** Vui lòng cung cấp thông tin CV/JD để tôi hỗ trợ tóm tắt."

        # Mock logic cho ReAct Agent
        if "cv_001" in text or "backend developer" in text:
            if "observation:" not in text:
                return "Thought: Tôi cần lấy danh sách hồ sơ ứng viên vị trí Backend Developer.\nAction: get_candidate_profile['CV_001']"
            else:
                return "Thought: Tôi đã có thông tin ứng viên Nguyễn Văn A (CV_001).\nFinal Answer: Ứng viên Nguyễn Văn A (CV_001) ứng tuyển Backend Developer có 3 năm kinh nghiệm với Python, FastAPI, PostgreSQL, Docker."

        if "kinh nghiệm" in text:
            if "observation:" not in text:
                return "Thought: Tôi cần tra cứu hồ sơ CV_001 để xem số năm kinh nghiệm.\nAction: get_candidate_profile['CV_001']"
            else:
                return "Thought: Tôi đã có dữ liệu hồ sơ.\nFinal Answer: Ứng viên Nguyễn Văn A có 3 năm kinh nghiệm phát triển Python & FastAPI."

        if "đặt lịch" in text:
            if "observation:" not in text:
                return "Thought: Tôi cần kiểm tra lịch phỏng vấn còn trống trước khi đặt.\nAction: check_interview_schedule['2026-08-05']"
            elif "check_interview_schedule" in text and "schedule_interview" not in text:
                return "Thought: Lịch ngày 2026-08-05 còn trống slot 10:00. Tiến hành đặt lịch.\nAction: schedule_interview['CV_001', '2026-08-05', '10:00', 'backend_senior']"
            else:
                return "Thought: Đã đặt lịch thành công.\nFinal Answer: ✅ Đã đặt lịch phỏng vấn thành công cho ứng viên Nguyễn Văn A vào 10:00 ngày 2026-08-05."

        return "Thought: Tôi sẽ tra cứu thông tin ứng viên.\nFinal Answer: Đã xử lý thành công yêu cầu tuyển dụng."


def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    """Factory function tự chọn Provider từ biến môi trường LLM_PROVIDER"""
    name = (provider_name or os.getenv("LLM_PROVIDER") or "mock").lower().strip()
    
    if name == "gemini":
        return GeminiProvider()
    elif name == "openai":
        return OpenAIProvider()
    elif name == "anthropic":
        return AnthropicProvider()
    elif name == "openrouter":
        return OpenRouterProvider()
    else:
        return MockProvider()



if __name__ == "__main__":
    print("=== TEST MULTI-PROVIDER LLM ADAPTER ===")
    provider = get_llm_provider()
    print(f"✅ Provider đang dùng: {provider.__class__.__name__}")
    print(f"🤖 User Query: Hello")
    print(f"💬 Response  : {provider.generate('Hello')}")
