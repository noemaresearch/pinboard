import pyclip
import re

def get_clipboard_content():
    return pyclip.paste().decode('utf-8')

def get_file_content(file_path: str):
    with open(file_path, 'r') as f:
        return f.read()

def parse_llm_response(response: str):
    artifact_pattern = r'(?m)^<artifact identifier="(.*?)">(.*?)^</artifact>'
    matches = re.findall(artifact_pattern, response, re.DOTALL)
    return {identifier: content.strip() for identifier, content in matches}