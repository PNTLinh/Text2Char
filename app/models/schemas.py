from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"

class ChartType(str, Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    AREA = "area"

class QueryRequest(BaseModel):
    question: str = Field(..., description="Câu hỏi từ người dùng")
    csv_path: Optional[str] = Field(None, description="Đường dẫn file CSV")
    llm_provider: LLMProvider = Field(LLMProvider.OPENAI, description="Provider LLM")

class SQLResponse(BaseModel):
    sql: str = Field(..., description="Câu SQL được generate")
    explanation: str = Field(..., description="Giải thích câu SQL")
    
class ChartConfig(BaseModel):
    chart_type: ChartType
    x_column: str
    y_column: str
    title: str
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    color_column: Optional[str] = None

class QueryResponse(BaseModel):
    success: bool
    sql: str
    data: Optional[List[Dict[str, Any]]] = None
    chart_config: Optional[ChartConfig] = None
    chart_html: Optional[str] = None
    error: Optional[str] = None