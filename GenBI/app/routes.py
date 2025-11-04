from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
from pathlib import Path
from app.models.schemas import QueryRequest, QueryResponse, ChartConfig
from app.services.llm_service import LLMService
from app.services.query_runner import QueryRunner
from app.services.chart_builder import ChartBuilder

router = APIRouter()

# Global instances
query_runner = QueryRunner()
chart_builder = ChartBuilder()

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV file"""
    try:
        # Lưu file vào thư mục data
        file_path = Path("data") / file.filename
        file_path.parent.mkdir(exist_ok=True)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Load vào query runner
        df = query_runner.load_csv(str(file_path))
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_path": str(file_path),
            "rows": len(df),
            "columns": list(df.columns)
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Xử lý câu hỏi và tạo biểu đồ"""
    try:
        # Load CSV nếu có
        if request.csv_path:
            query_runner.load_csv(request.csv_path)
        
        # Lấy schema
        schema = query_runner.get_table_schema()
        
        # Generate SQL từ LLM
        llm_service = LLMService(provider=request.llm_provider)
        llm_result = llm_service.generate_sql(request.question, schema)
        
        # Execute SQL
        result_df = query_runner.execute_sql(llm_result['sql'])
        
        # Tạo chart config
        chart_config = ChartConfig(
            chart_type=llm_result.get('chart_type', 'bar'),
            x_column=llm_result['x_column'],
            y_column=llm_result['y_column'],
            title=llm_result['title']
        )
        
        # Generate chart
        chart_html = chart_builder.create_chart(result_df, chart_config)
        
        return QueryResponse(
            success=True,
            sql=llm_result['sql'],
            data=result_df.to_dict('records'),
            chart_config=chart_config,
            chart_html=chart_html
        )
    
    except Exception as e:
        return QueryResponse(
            success=False,
            sql="",
            error=str(e)
        )

@router.get("/data-info")
async def get_data_info():
    """Lấy thông tin về dữ liệu hiện tại"""
    try:
        info = query_runner.get_data_info()
        return {"success": True, "data": info}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))