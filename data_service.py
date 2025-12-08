import pandas as pd
import duckdb
import os
from app.config import config

class DataService:
    def __init__(self):
        self.upload_folder = config.DATA_UPLOAD_FOLDER
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def save_uploaded_file(self, file) -> str:
        """Save uploaded CSV file and return file path."""
        file_path = os.path.join(self.upload_folder, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        return file_path
    
    def read_csv_to_df(self, file_path: str) -> pd.DataFrame:
        """Read CSV file into pandas DataFrame."""
        return pd.read_csv(file_path)
    
    def get_data_info(self, df: pd.DataFrame) -> dict:
        """Get basic information about the DataFrame."""
        info = {
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "shape": df.shape,
            "preview": df.head().to_dict(orient="records")
        }
        return info
    
    def run_sql_query(self, sql: str, df: pd.DataFrame) -> pd.DataFrame:
        """Run SQL query on DataFrame using DuckDB."""
        # Register the DataFrame as a view in DuckDB
        conn = duckdb.connect()
        conn.register('df', df)
        result = conn.execute(sql).fetchdf()
        conn.close()
        return result