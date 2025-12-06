import streamlit as st
import requests
import pandas as pd
import json
from pathlib import Path

# Config
API_URL = "http://localhost:8000/api"

st.set_page_config(
    page_title="Text2Chart",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Text2Chart - Natural Language to Visualization")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    llm_provider = st.selectbox(
        "LLM Provider",
        options=["openai", "gemini"],
        index=0
    )
    
    st.markdown("---")
    st.header("📁 Upload Data")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv']
    )
    
    if uploaded_file:
        # Upload file to backend
        files = {"file": uploaded_file}
        response = requests.post(f"{API_URL}/upload-csv", files=files)
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ Uploaded: {result['rows']} rows")
            st.session_state['csv_path'] = result['file_path']
            
            # Show data info
            with st.expander("Data Preview"):
                info_response = requests.get(f"{API_URL}/data-info")
                if info_response.status_code == 200:
                    data_info = info_response.json()['data']
                    st.write(f"**Columns:** {', '.join(data_info['columns'])}")
                    st.dataframe(pd.DataFrame(data_info['sample']))

# Main area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Ask a Question")
    
    question = st.text_area(
        "Enter your question about the data:",
        placeholder="Ví dụ: Show top 10 products by revenue",
        height=100
    )
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        submit = st.button("🚀 Generate", type="primary", use_container_width=True)
    with col_btn2:
        clear = st.button("🗑️ Clear", use_container_width=True)

with col2:
    st.header("📝 Examples")
    examples = [
        "Show sales by month",
        "Top 5 customers by revenue",
        "Average order value by category",
        "Product distribution (pie chart)"
    ]
    
    for ex in examples:
        if st.button(ex, use_container_width=True):
            question = ex
            st.rerun()

# Process query
if submit and question:
    if 'csv_path' not in st.session_state:
        st.error("❌ Please upload a CSV file first!")
    else:
        with st.spinner("🔄 Processing your question..."):
            # Send request
            payload = {
                "question": question,
                "csv_path": st.session_state['csv_path'],
                "llm_provider": llm_provider
            }
            
            response = requests.post(f"{API_URL}/query", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                if result['success']:
                    st.success("✅ Query executed successfully!")
                    
                    # Show SQL
                    with st.expander("🔍 Generated SQL", expanded=True):
                        st.code(result['sql'], language='sql')
                    
                    # Show data
                    st.subheader("📋 Result Data")
                    df = pd.DataFrame(result['data'])
                    st.dataframe(df, use_container_width=True)
                    
                    # Show chart
                    st.subheader("📊 Visualization")
                    st.components.v1.html(
                        result['chart_html'],
                        height=600,
                        scrolling=True
                    )
                    
                    # Download options
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        csv = df.to_csv(index=False)
                        st.download_button(
                            "📥 Download CSV",
                            csv,
                            "result.csv",
                            "text/csv"
                        )
                    with col_d2:
                        st.download_button(
                            "📥 Download HTML",
                            result['chart_html'],
                            "chart.html",
                            "text/html"
                        )
                else:
                    st.error(f"❌ Error: {result.get('error')}")
            else:
                st.error("❌ API request failed!")

if clear:
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Made with ❤️ using FastAPI, Streamlit & LLMs</p>
    </div>
    """,
    unsafe_allow_html=True
)