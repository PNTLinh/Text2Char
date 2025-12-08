import chromadb
from chromadb.config import Settings
import pandas as pd
from typing import List, Dict, Any
import os
from app.config import config

class VectorService:
    def __init__(self):
        # Persistent client
        self.client = chromadb.PersistentClient(
            path=config.VECTOR_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=config.CHROMA_COLLECTION_NAME
        )
    
    def index_dataframe(self, df: pd.DataFrame, metadata: Dict[str, Any] = None):
        """Index the DataFrame into ChromaDB."""
        # Convert each row into a document
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in df.iterrows():
            # Create a text representation of the row
            doc = " ".join([f"{col}: {row[col]}" for col in df.columns])
            documents.append(doc)
            # Add metadata (including column names and row index)
            meta = {
                "row_index": idx,
                "columns": list(df.columns),
                **metadata
            } if metadata else {"row_index": idx, "columns": list(df.columns)}
            metadatas.append(meta)
            ids.append(f"row_{idx}")
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Query the vector database for similar rows."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                "document": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i]
            })
        return formatted_results