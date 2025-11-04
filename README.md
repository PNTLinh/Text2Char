# Text2Chart

Phát triển một công cụ AI có khả năng hiểu nội dung văn bản mô tả dữ liệu và tự động tạo biểu đồ trực quan, cho phép người dùng tùy chỉnh biểu đồ.

## Features

- 🤖 Tích hợp OpenAI GPT và Google Gemini
- 🗄️ Xử lý dữ liệu với DuckDB & Pandas
- 📊 Tự động tạo biểu đồ với Plotly
- 🎨 Giao diện Streamlit thân thiện
- 🚀 REST API với FastAPI

## Project Structure

```
text2chart/
├─ app/
│  ├─ main.py              # FastAPI entrypoint
│  ├─ routes.py            # API routes
│  ├─ services/
│  │   ├─ llm_service.py   # Gọi GPT hoặc Gemini
│  │   ├─ query_runner.py  # DuckDB/Pandas xử lý SQL
│  │   └─ chart_builder.py # Tạo biểu đồ từ dataframe
│  ├─ models/
│  │   └─ schemas.py       # Pydantic models
│  └─ utils/               # helper functions
├─ frontend/
│  └─ app.py               # Streamlit UI
├─ data/                   # CSV / SQLite sample
├─ requirements.txt
└─ README.md
```

## Installation

### Create virtual environment
```bash
python -m venv myenv
myenv\Scripts\activate  # Windows
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Setup .env
```bash
cp .env.example .env
```

## Usage

### Start Backend
```bash
python -m app.main
```

### Start Frontend
```bash
streamlit run ui.py
```
Streamlit sẽ chạy tại: http://localhost:8501

## API Endpoints

- `POST /api/upload-csv` - Upload CSV file
- `POST /api/query` - Process natural language query
- `GET /api/data-info` - Get current data info

## Tech Stack

- **Backend**: FastAPI, DuckDB, Pandas
- **LLM**: OpenAI GPT-4, Google Gemini
- **Visualization**: Plotly
- **Frontend**: Streamlit