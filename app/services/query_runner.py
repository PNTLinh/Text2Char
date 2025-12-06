import duckdb
import pandas as pd
from typing import Dict, Any, List
import os

class QueryRunner:
    def __init__(self):
        self.conn = None
        self.current_df = None
    
    def load_csv(self, csv_path: str) -> pd.DataFrame:
        """Load CSV file vào pandas DataFrame"""
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"File không tồn tại: {csv_path}")
        
        self.current_df = pd.read_csv(csv_path)
        return self.current_df
    
    def get_table_schema(self) -> Dict[str, str]:
        """Lấy schema của bảng hiện tại"""
        if self.current_df is None:
            raise ValueError("Chưa load dữ liệu")
        
        return {col: str(dtype) for col, dtype in self.current_df.dtypes.items()}
    
    def get_data_info(self) -> Dict[str, Any]:
        """Lấy thông tin tổng quan về dữ liệu"""
        if self.current_df is None:
            raise ValueError("Chưa load dữ liệu")
        
        return {
            "row_count": len(self.current_df),
            "columns": list(self.current_df.columns),
            "dtypes": {col: str(dtype) for col, dtype in self.current_df.dtypes.items()},
            "sample": self.current_df.head(3).to_dict('records')
        }
    
    def execute_sql(self, sql: str) -> pd.DataFrame:
        """
        Thực thi SQL query trên DataFrame hiện tại
        
        Args:
            sql: Câu SQL query
            
        Returns:
            DataFrame chứa kết quả
        """
        if self.current_df is None:
            raise ValueError("Chưa load dữ liệu")
        
        # DuckDB có thể query trực tiếp trên pandas DataFrame
        conn = duckdb.connect(':memory:')
        
        # Register DataFrame như một table tên 'data'
        conn.register('data', self.current_df)
        
        try:
            result_df = conn.execute(sql).fetchdf()
            return result_df
        except Exception as e:
            raise ValueError(f"Lỗi khi thực thi SQL: {str(e)}")
        finally:
            conn.close()
    
    def validate_sql(self, sql: str) -> bool:
        """Kiểm tra SQL có hợp lệ không"""
        try:
            conn = duckdb.connect(':memory:')
            conn.register('data', self.current_df)
            conn.execute(f"EXPLAIN {sql}")
            conn.close()
            return True
        except:
            return False