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
Text2Char/
├── .env                       # Biến môi trường (API Keys, Configs)
├── .gitignore
├── requirements.txt           # Thêm: chromadb, sentence-transformers
├── README.md
│
├── data/                      # Nơi lưu trữ dữ liệu
│   ├── uploads/               # File CSV người dùng upload
│   └── vector_db/             # Folder lưu dữ liệu của ChromaDB (Persist)
│
├── app/                       # BACKEND (FastAPI)
│   ├── __init__.py
│   ├── main.py                # Entry point của FastAPI
│   │
│   ├── endpoints.py       # API upload, query, health check
│   │
│   ├── config.py          # Load .env, cấu hình App
│   │   
│   ├── schemas.py         # Request/Response models (QueryRequest, SQLResponse...)
│   │   
│   ├── services/              # BUSINESS LOGIC (Quan trọng nhất)
│   │   ├── __init__.py
│   │   ├── data_service.py    # Xử lý Pandas, DuckDB (Đọc/Ghi file, chạy SQL)
│   │   ├── vector_service.py  # [MỚI] Quản lý ChromaDB (Indexing & Retrieval)
│   │   ├── llm_service.py     # Gọi OpenAI/Gemini (Generation)
│   │
│   └── helpers.py         # Hàm clean json, format text...
│
└── ui/                        # FRONTEND (Streamlit)
    ├── app.py                 # File chạy chính: streamlit run ui/app.py
    └── components/            # Tách nhỏ giao diện
        ├── sidebar.py         # Code phần cài đặt bên trái
        ├── chat.py            # Code hiển thị chat
        ├── visualization.py   # Code vẽ biểu đồ
```

## Installation

### Create virtual environment
```bash
python -m venv myenv
myenv\Scripts\activate  /  conda activate genbi
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Setup .env
```bash
cp .env .env
```

## Usagepyt

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