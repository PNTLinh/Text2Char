import json
import re

def clean_json_string(json_str: str) -> str:
    """Clean JSON string that might contain extra characters or markdown code blocks."""
    # Remove markdown code block if present
    json_str = re.sub(r'```json\s*', '', json_str)
    json_str = re.sub(r'\s*```', '', json_str)
    # Remove extra whitespace
    json_str = json_str.strip()
    return json_str

def safe_json_loads(json_str: str) -> dict:
    """Safely parse JSON string, trying to fix common issues."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # Try to fix common issues
        json_str = clean_json_string(json_str)
        # Try again
        try:
            return json.loads(json_str)
        except:
            raise ValueError(f"Invalid JSON: {e}")