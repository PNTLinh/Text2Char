import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional
from app.models.schemas import ChartType, ChartConfig

class ChartBuilder:
    def __init__(self):
        pass
    
    def create_chart(self, df: pd.DataFrame, config: ChartConfig) -> str:
        """
        Tạo biểu đồ từ DataFrame và config
        
        Returns:
            HTML string của biểu đồ
        """
        chart_type = config.chart_type
        
        if chart_type == ChartType.BAR:
            fig = px.bar(
                df, 
                x=config.x_column, 
                y=config.y_column,
                title=config.title,
                labels={
                    config.x_column: config.x_label or config.x_column,
                    config.y_column: config.y_label or config.y_column
                },
                color=config.color_column
            )
        
        elif chart_type == ChartType.LINE:
            fig = px.line(
                df,
                x=config.x_column,
                y=config.y_column,
                title=config.title,
                labels={
                    config.x_column: config.x_label or config.x_column,
                    config.y_column: config.y_label or config.y_column
                },
                color=config.color_column
            )
        
        elif chart_type == ChartType.PIE:
            fig = px.pie(
                df,
                names=config.x_column,
                values=config.y_column,
                title=config.title
            )
        
        elif chart_type == ChartType.SCATTER:
            fig = px.scatter(
                df,
                x=config.x_column,
                y=config.y_column,
                title=config.title,
                labels={
                    config.x_column: config.x_label or config.x_column,
                    config.y_column: config.y_label or config.y_column
                },
                color=config.color_column
            )
        
        elif chart_type == ChartType.HISTOGRAM:
            fig = px.histogram(
                df,
                x=config.x_column,
                title=config.title,
                labels={config.x_column: config.x_label or config.x_column}
            )
        
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        # Customize layout
        fig.update_layout(
            template="plotly_white",
            hovermode="x unified",
            height=500
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="chart")