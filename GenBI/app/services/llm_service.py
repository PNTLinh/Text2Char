import os
from typing import Dict, Any
import json
from openai import OpenAI
import google.generativeai as genai
from app.models.schemas import LLMProvider, SQLResponse

class LLMService:
    def __init__(self, provider: LLMProvider = LLMProvider.OPENAI):
        self.provider = provider
        
        if provider == LLMProvider.OPENAI:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif provider == LLMProvider.GEMINI:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_sql(self, question: str, table_schema: Dict[str, str]) -> SQLResponse:
        """
        Generate SQL từ natural language question
        
        Args:
            question: Câu hỏi từ người dùng
            table_schema: Dictionary với format {column_name: data_type}
        """
        schema_str = "\n".join([f"- {col}: {dtype}" for col, dtype in table_schema.items()])
        
        prompt = f"""Bạn là một SQL expert. Dựa vào câu hỏi và schema của bảng dữ liệu, 
hãy tạo câu SQL phù hợp.

SCHEMA của bảng 'data':
{schema_str}

CÂU HỎI: {question}

Hãy trả về JSON với format:
{{
    "sql": "SELECT ... FROM data WHERE ...",
    "explanation": "Giải thích câu SQL này làm gì",
    "chart_type": "bar/line/pie/scatter/histogram",
    "x_column": "tên cột trục X",
    "y_column": "tên cột trục Y",
    "title": "Tiêu đề biểu đồ"
}}

LÀM ỚN TRÊN NHẤT LÀ SQL QUERY CHỈ SELECT CÁC CỘT CẦN THIẾT.
Tên bảng PHẢI là 'data'.
"""
        
        if self.provider == LLMProvider.OPENAI:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a SQL expert that generates valid SQL and chart configurations in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            result = json.loads(response.choices[0].message.content)
        
        elif self.provider == LLMProvider.GEMINI:
            response = self.model.generate_content(prompt)
            # Parse JSON từ response
            text = response.text
            # Tìm JSON trong response
            start = text.find('{')
            end = text.rfind('}') + 1
            result = json.loads(text[start:end])
        
        return result
    
    def suggest_chart_type(self, data_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gợi ý loại biểu đồ phù hợp dựa trên dữ liệu
        """
        prompt = f"""Dựa vào thông tin dữ liệu sau, hãy gợi ý loại biểu đồ phù hợp nhất:

Số dòng: {data_info.get('row_count')}
Các cột: {data_info.get('columns')}
Kiểu dữ liệu: {data_info.get('dtypes')}

Trả về JSON:
{{
    "chart_type": "bar/line/pie/scatter",
    "reason": "Lý do chọn loại biểu đồ này",
    "x_column": "cột nên dùng cho trục X",
    "y_column": "cột nên dùng cho trục Y"
}}
"""
        
        if self.provider == LLMProvider.OPENAI:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        
        elif self.provider == LLMProvider.GEMINI:
            response = self.model.generate_content(prompt)
            text = response.text
            start = text.find('{')
            end = text.rfind('}') + 1
            return json.loads(text[start:end])