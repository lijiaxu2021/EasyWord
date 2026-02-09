import requests
import json

SILICON_FLOW_API_KEY = "sk-gxfzbsarwmnbmfeocgiozfpfmpbwqgaquxzirslobqjafmac"
SILICON_FLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"

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
    - "example": A string containing 2-3 example sentences. Each sentence should have its Chinese translation next to it.
    
    Ignore simple connecting words if the text is a sentence, focus on key vocabulary. If the text is a list of words, process all of them.
    Only return the JSON Array, no other text.
    """
    
    payload = {
        "model": "Qwen/Qwen2-7B-Instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful English dictionary assistant. Always output valid JSON Array."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2048
    }
    
    try:
        response = requests.post(SILICON_FLOW_API_URL, headers=headers, json=payload, timeout=30)
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
