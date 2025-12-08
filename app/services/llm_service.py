import os
import json
import re
import httpx
from typing import Dict, Any
from openai import OpenAI
import google.generativeai as genai
from app.models.schemas import LLMProvider, SQLResponse

class LLMService:
    def __init__(self, provider: LLMProvider = LLMProvider.OPENAI):
        self.provider = provider
        
        # --- CẤU HÌNH OPENAI ---
        if provider == LLMProvider.OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
            
            # Lấy proxy từ biến môi trường
            proxy_url = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
            
            # FIX LỖI PROXY: Sử dụng httpx.Client
            if proxy_url:
                # Lưu ý: tham số là 'proxies' (số nhiều), truyền string vào nó sẽ áp dụng cho cả http và https
                http_client = httpx.Client(proxies=proxy_url)
                self.client = OpenAI(api_key=api_key, http_client=http_client)
            else:
                self.client = OpenAI(api_key=api_key)
                
            self.model_name = "gpt-4o"

        # --- CẤU HÌNH GEMINI ---
        elif provider == LLMProvider.GEMINI:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config={"response_mime_type": "application/json"}
            )

    def _clean_and_parse_json(self, raw_text: str) -> Dict[str, Any]:
        """Hàm tiện ích để làm sạch chuỗi JSON trả về từ LLM"""
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                clean_json = match.group(0)
                try:
                    return json.loads(clean_json)
                except json.JSONDecodeError:
                    pass
            print(f"ERROR PARSING JSON: {raw_text}")
            return {}

    def generate_sql(self, question: str, table_schema: Dict[str, str]) -> SQLResponse:
        """Generate SQL compatible with DuckDB"""
        schema_str = "\n".join([f"- {col}: {dtype}" for col, dtype in table_schema.items()])
        
        prompt = f"""Bạn là chuyên gia về DuckDB SQL.
Nhiệm vụ: Chuyển đổi câu hỏi tự nhiên thành SQL và cấu hình biểu đồ.

THÔNG TIN BẢNG 'data':
{schema_str}

CÂU HỎI: "{question}"

YÊU CẦU:
1. SQL chạy được trên DuckDB.
2. Tên bảng là 'data'.
3. Trả về JSON thuần túy (không markdown).

OUTPUT JSON FORMAT:
{{
    "sql": "SELECT ... FROM data ...",
    "explanation": "Giải thích ngắn gọn",
    "chart_type": "bar" | "line" | "pie" | "scatter",
    "x_column": "tên_cột_x",
    "y_column": "tên_cột_y",
    "title": "Tiêu đề biểu đồ"
}}
"""
        
        if self.provider == LLMProvider.OPENAI:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful data assistant. Output valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            raw_content = response.choices[0].message.content
        
        elif self.provider == LLMProvider.GEMINI:
            response = self.model.generate_content(prompt)
            raw_content = response.text
            
        return self._clean_and_parse_json(raw_content)