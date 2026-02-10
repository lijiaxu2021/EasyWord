import requests
import json

SILICON_FLOW_API_KEY = "sk-gxfzbsarwmnbmfeocgiozfpfmpbwqgaquxzirslobqjafmac"
SILICON_FLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
MODEL = "Qwen/Qwen2.5-7B-Instruct"  # Define model constant

def generate_word_info_bulk(text):
    """
    Use SiliconFlow API to generate info for multiple words extracted from text.
    Implements smart chunking to avoid token limits.
    """
    
    # 1. First, ask AI to just extract words (low token usage)
    # Or we can just split by spaces if it's a list, but user might paste a paragraph.
    # Let's try a direct approach: Split the text ourselves if it's too long, or ask AI to extract first.
    # A safe heuristic: If text > 1000 chars, it might be too long for a single rich response.
    # But even for short text, generating 50 words detailed info is huge.
    # Strategy:
    # Step A: Extract words (pure list) from text.
    # Step B: Process words in chunks of 5.
    
    # Step A: Extract Words
    extraction_prompt = f"""
    Identify and extract all unique English words from the following text that are suitable for learning (ignore common stop words like 'the', 'is', 'and', etc.).
    Return ONLY a JSON Array of strings. Example: ["apple", "banana", "cherry"]
    
    Text: "{text[:4000]}" 
    """
    # Truncate input text to 4000 chars for safety in extraction step
    
    try:
        print("DEBUG: Extracting words...")
        response = requests.post(SILICON_FLOW_API_URL, headers={
            "Authorization": f"Bearer {SILICON_FLOW_API_KEY}",
            "Content-Type": "application/json"
        }, json={
            "model": MODEL,
            "messages": [{"role": "user", "content": extraction_prompt}],
            "max_tokens": 1024,
            "temperature": 0.1
        }, timeout=30)
        
        response.raise_for_status()
        words_list = _parse_json_response(response.json())
        
        if not words_list or not isinstance(words_list, list):
            print("DEBUG: Failed to extract words or empty list")
            return None
            
        print(f"DEBUG: Extracted {len(words_list)} words: {words_list}")
        
    except Exception as e:
        print(f"AI Extraction Error: {e}")
        return None

    # Step B: Process in Chunks
    CHUNK_SIZE = 5 # Small chunk size to ensure quality and fit in context
    all_results = []
    
    for i in range(0, len(words_list), CHUNK_SIZE):
        chunk = words_list[i:i + CHUNK_SIZE]
        print(f"DEBUG: Processing chunk {i//CHUNK_SIZE + 1}: {chunk}")
        
        chunk_prompt = f"""
        Provide detailed learning information for these English words: {chunk}
        
        Return a JSON Array of objects. Each object must contain:
        - "word": The word itself.
        - "phonetic": IPA symbol.
        - "definition_cn": Detailed Chinese definition with parts of speech.
        - "definition_en": Concise English definition.
        - "example": String with 2 example sentences (bilingual).
        - "memory_method": A creative memory aid (Chinese, ~50 chars).
        
        Strict JSON Array only.
        """
        
        try:
            response = requests.post(SILICON_FLOW_API_URL, headers={
                "Authorization": f"Bearer {SILICON_FLOW_API_KEY}",
                "Content-Type": "application/json"
            }, json={
                "model": MODEL,
                "messages": [{"role": "user", "content": chunk_prompt}],
                "max_tokens": 2048,
                "temperature": 0.7
            }, timeout=45) # Longer timeout for batch
            
            response.raise_for_status()
            chunk_results = _parse_json_response(response.json())
            
            if chunk_results and isinstance(chunk_results, list):
                all_results.extend(chunk_results)
            else:
                print(f"DEBUG: Chunk failed parsing: {chunk}")
                
        except Exception as e:
            print(f"AI Chunk Error ({chunk}): {e}")
            # Continue to next chunk instead of failing all
            continue
            
    return all_results

def _parse_json_response(data):
    """Helper to safely parse JSON from AI response"""
    try:
        content = data['choices'][0]['message']['content']
        clean_content = content.replace("```json", "").replace("```", "").strip()
        start = clean_content.find('[')
        end = clean_content.rfind(']') + 1
        if start != -1 and end != 0:
            return json.loads(clean_content[start:end])
        # Try finding object if array failed (shouldn't happen for these prompts but good safety)
        if clean_content.startswith('{'):
            return json.loads(clean_content)
        return json.loads(clean_content)
    except Exception as e:
        print(f"JSON Parse Error: {e} | Content: {content[:100]}...")
        return None

def lookup_word_ai(word):
    """
    Single word lookup with detailed memory method (~300 chars).
    """
    headers = {
        "Authorization": f"Bearer {SILICON_FLOW_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    You are an English dictionary assistant. detailed analysis of the English word: "{word}".
    
    STRICTLY return ONLY a JSON Object. Do not include any markdown formatting, backticks, or explanatory text.
    
    JSON Structure:
    {{
        "word": "{word}",
        "phonetic": "IPA symbol",
        "definition_cn": "Detailed Chinese definition with parts of speech",
        "definition_en": "Concise English definition",
        "example": "3 example sentences with Chinese translations (separated by newlines)",
        "memory_method": "A creative memory aid in Chinese (approx. 300 chars)"
    }}
    """
    
    try:
        response = requests.post(SILICON_FLOW_API_URL, headers=headers, json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2048,
            "temperature": 0.5 # Lower temperature for more stable JSON
        }, timeout=20)
        
        response.raise_for_status()
        data = response.json()
        content = data['choices'][0]['message']['content']
        
        # Robust Clean up
        clean_content = content.replace("```json", "").replace("```", "").strip()
        print(f"DEBUG: AI Raw Content: {clean_content}") # LOG
        
        # Extract JSON if mixed with text
        start = clean_content.find('{')
        end = clean_content.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = clean_content[start:end]
            return json.loads(json_str)
        else:
            return json.loads(clean_content)
            
    except Exception as e:
        print(f"AI Lookup Error: {e}")
        import traceback
        traceback.print_exc()
        return None
