import json

def extract_json(content):
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
        # 2. Fallback: Try cleaning markdown manually
        clean_content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_content)

def test_extraction():
    test_cases = [
        # 1. Standard Markdown
        """```json
[
    {"word": "hello"}
]
```""",
        # 2. Text before/after
        """Here is the result:
[
    {"word": "world"}
]
Hope this helps!""",
        # 3. No markdown, just array
        """[{"word": "test"}]""",
        # 4. Markdown with spaces
        """ ```json
[{"word": "space"}]
``` """
    ]

    for i, text in enumerate(test_cases):
        print(f"Test {i+1}: ", end="")
        try:
            res = extract_json(text)
            if isinstance(res, list) and 'word' in res[0]:
                print("PASS")
            else:
                print(f"FAIL (Invalid structure): {res}")
        except Exception as e:
            print(f"FAIL (Exception): {e}")

if __name__ == "__main__":
    test_extraction()
