import requests
import json

SILICON_FLOW_API_KEY = "sk-gxfzbsarwmnbmfeocgiozfpfmpbwqgaquxzirslobqjafmac"
SILICON_FLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
MODEL = "Qwen/Qwen2.5-7B-Instruct"  # Define model constant

def generate_word_info_bulk(text):
    """
    Use SiliconFlow API to generate info for multiple words extracted from text.
    Returns a list of dicts.
    """
    headers = {
        "Authorization": f"Bearer {SILICON_FLOW_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Analyze the following text, extract English words, and provide detailed information for each word in a JSON Array format.
    Text: "{text}"
    
    For each word, the JSON object must contain:
    - "word": The English word itself.
    - "phonetic": IPA phonetic symbol.
    - "definition_cn": A detailed Chinese definition with parts of speech. Format: "pos. meaning; meaning \\n pos. meaning". Example: "v. 推; 移动\\nn. 推动; 进取心".
    - "definition_en": A concise English definition.
    - "example": A string containing 3 example sentences. Each sentence should have its Chinese translation next to it.
    - "memory_method": A creative memory aid or mnemonic method (in Chinese). No strict length limit, make it effective.
    
    Ignore simple connecting words if the text is a sentence, focus on key vocabulary. If the text is a list of words, process all of them.
    Only return the JSON Array, no other text.
    """
    
    try:
        response = requests.post(SILICON_FLOW_API_URL, headers=headers, json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096, # Increase for more content
            "temperature": 0.7
        }, timeout=30) # Increase timeout
        
        response.raise_for_status()
        data = response.json()
        
        content = data['choices'][0]['message']['content']
        
        # Robust JSON extraction
        try:
            # 1. Try finding the JSON array boundaries
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != 0:
                json_str = content[start:end]
            else:
                json_str = content

            return json.loads(json_str)
        except json.JSONDecodeError:
            # 2. Fallback: Try cleaning markdown manually if regex didn't help
            clean_content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_content)
            
    except Exception as e:
        print(f"AI Bulk Generation Error: {e}")
        # Log the content that failed for debugging (in a real app, maybe to a file)
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
