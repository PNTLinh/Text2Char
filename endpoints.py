from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.schemas import QueryRequest, SQLResponse, VisualizationRequest, VisualizationResponse, UploadResponse
from app.services.data_service import DataService
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService
import pandas as pd
import plotly
import os

app = FastAPI()
data_service = DataService()
vector_service = VectorService()
llm_service = LLMService()

# Global variable to store current DataFrame (for simplicity, in production use a database)
current_df = None

@app.post("/api/upload-csv", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    global current_df
    try:
        # Save the uploaded file
        file_path = data_service.save_uploaded_file(file)
        
        # Read CSV into DataFrame
        df = data_service.read_csv_to_df(file_path)
        current_df = df
        
        # Index data into vector database
        vector_service.index_dataframe(df, metadata={"filename": file.filename})
        
        # Get data info
        info = data_service.get_data_info(df)
        
        return UploadResponse(
            filename=file.filename,
            message="File uploaded successfully",
            columns=info["columns"],
            preview=info["preview"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query", response_model=SQLResponse)
async def process_query(request: QueryRequest):
    global current_df
    if current_df is None:
        raise HTTPException(status_code=400, detail="No data uploaded. Please upload a CSV file first.")
    
    try:
        # Get data info
        info = data_service.get_data_info(current_df)
        
        # Generate SQL from natural language query
        sql = llm_service.generate_sql(request.query, info, use_openai=request.use_openai)
        
        # Run the SQL query
        result_df = data_service.run_sql_query(sql, current_df)
        
        # Convert result to list of dictionaries
        data = result_df.to_dict(orient="records")
        
        return SQLResponse(
            sql_query=sql,
            data=data,
            error=None
        )
    except Exception as e:
        return SQLResponse(
            sql_query="",
            data=[],
            error=str(e)
        )

@app.post("/api/visualize", response_model=VisualizationResponse)
async def create_visualization(request: VisualizationRequest):
    try:
        # Generate chart specification using LLM
        chart_spec = llm_service.generate_chart_spec(
            request.data, 
            f"Create a {request.chart_type} chart with x={request.x_column} and y={request.y_column}. Title: {request.title}",
            use_openai=True  # or let the user choose
        )
        
        # Create Plotly figure from the specification
        fig = plotly.graph_objs.Figure(chart_spec)
        
        # Convert figure to JSON
        chart_json = fig.to_dict()
        
        return VisualizationResponse(
            chart_json=chart_json,
            error=None
        )
    except Exception as e:
        return VisualizationResponse(
            chart_json={},
            error=str(e)
        )

@app.get("/api/data-info")
async def get_data_info():
    global current_df
    if current_df is None:
        raise HTTPException(status_code=400, detail="No data uploaded.")
    
    info = data_service.get_data_info(current_df)
    return info

@app.get("/health")
async def health_check():
    return {"status": "healthy"}