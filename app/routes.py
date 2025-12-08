from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import pandas as pd  # Cần import pandas để xử lý NaN
from pathlib import Path
from app.models.schemas import QueryRequest, QueryResponse, ChartConfig
from app.services.llm_service import LLMService
from app.services.query_runner import QueryRunner
from app.services.chart_builder import ChartBuilder

router = APIRouter()

# Global instances
query_runner = QueryRunner()
chart_builder = ChartBuilder()

# Định nghĩa đường dẫn lưu file
UPLOAD_DIR = Path("data")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV file"""
    try:
        # Lưu file vào thư mục data
        file_path = UPLOAD_DIR / file.filename
        
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
        # Load CSV nếu có đường dẫn mới, nếu không dùng cái cũ trong memory
        if request.csv_path:
            query_runner.load_csv(request.csv_path)
        
        # Lấy schema
        schema = query_runner.get_table_schema()
        
        # Generate SQL từ LLM
        llm_service = LLMService(provider=request.llm_provider)
        llm_result = llm_service.generate_sql(request.question, schema)
        
        # Execute SQL
        result_df = query_runner.execute_sql(llm_result['sql'])
        
        # --- FIX LỖI NAN QUAN TRỌNG (STEP 1) ---
        # Convert NaN thành None để JSON không bị lỗi
        result_df = result_df.where(pd.notnull(result_df), None)
        # ---------------------------------------

        # Tạo chart config
        chart_config = ChartConfig(
            chart_type=llm_result.get('chart_type', 'bar'),
            x_column=llm_result.get('x_column'),
            y_column=llm_result.get('y_column'),
            title=llm_result.get('title', 'Biểu đồ dữ liệu')
        )
        
        # Generate chart HTML (nếu cần)
        chart_html = chart_builder.create_chart(result_df, chart_config)
        
        return QueryResponse(
            success=True,
            sql=llm_result['sql'],
            data=result_df.to_dict('records'),
            chart_config=chart_config,
            chart_html=chart_html
        )
    
    except Exception as e:
        # In lỗi ra terminal để dễ debug
        print(f"Error processing query: {e}")
        return QueryResponse(
            success=False,
            sql="",
            error=str(e)
        )

@router.get("/data-info")
async def get_data_info():
    """Lấy thông tin về dữ liệu hiện tại"""
    try:
        # --- FIX LỖI NAN QUAN TRỌNG (STEP 2) ---
        # Logic: Tìm file mới nhất trong folder data để đọc
        files = sorted(UPLOAD_DIR.glob("*.csv"), key=os.path.getmtime)
        
        if not files:
            return {"success": False, "message": "Chưa có file nào được upload"}
            
        latest_file = files[-1]
        
        # Đọc file để lấy thông tin
        df = pd.read_csv(latest_file)
        
        # Xử lý NaN thành None cho phần preview
        df = df.where(pd.notnull(df), None)
        
        info = {
            "filename": latest_file.name,
            "row_count": len(df),
            "columns": list(df.columns),
            "dtypes": {k: str(v) for k, v in df.dtypes.items()},
            "sample": df.head(5).to_dict(orient='records')
        }
        
        return {"success": True, "data": info}
        # ---------------------------------------

    except Exception as e:
        print(f"Error getting data info: {e}")
        raise HTTPException(status_code=400, detail=str(e))