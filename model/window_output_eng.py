import requests
import json
import re

import requests
import json
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch
import re
import torch
from transformers import LlamaForCausalLM, LlamaTokenizer


def extract_script_from_srt(srt_path):
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    script_lines = re.sub(r'\d+\n|\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', content)

    script_text = '\n'.join([line.strip() for line in script_lines.split('\n') if line.strip()])
    return script_text

def read_script_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        script_text = f.read()
    return script_text

def GPT4(prompt, key, file_path=None):
    url = "https://api.openai.com/v1/chat/completions"
    api_key = key
    with open('eng_temp/temp_synop_based_window.txt', 'r', encoding='utf-8') as f:
        template = f.readlines()

    if file_path:
        if file_path.endswith('.srt'):
            script_text = extract_script_from_srt(file_path)
            print("Processed SRT file")
        elif file_path.endswith('.txt'):
            script_text = read_script_from_txt(file_path)
            print("Processed TXT file")
        else:
            raise ValueError("Unsupported file type. Only .srt and .txt files are supported.")
        prompt = f"{prompt}\n\n Script:\n{script_text}"
        
    user_textprompt = f"Prompt:{prompt} \n:"
    textprompt = f"{' '.join(template)} \n {user_textprompt}"
    
    payload = json.dumps({
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": textprompt
            }
        ]
    })
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }

    print('Waiting for GPT-4 response')
    response = requests.post(url, headers=headers, data=payload)
    obj = response.json()
    text = obj['choices'][0]['message']['content']
    print(text)

    return get_params_window(text)

def get_params_window(output_text):
    """
    Extract video segments and their descriptions from formatted text with flexible formatting.
    """
    # Regex to find segment descriptions with corresponding numbers and time ranges
    pattern = r"(\d+)\.\s*(.+?)\s*\((\d+)\s*-\s*(\d+)\)"

    # Find all matches
    matches = re.findall(pattern, output_text)

    # Debugging: Log matches for inspection
    print(f"DEBUG: Matches found: {matches}")

    if not matches:
        print("DEBUG: No valid matches found in GPT response.")
        return {}

    # Create parameter dictionary
    para_dict = {}
    for segment_num, description, start_time, end_time in matches:
        try:
            para_dict[f"Segment {segment_num}"] = {
                "Description": description.strip(),
                "Start Time": int(start_time.strip()),
                "End Time": int(end_time.strip())
            }
        except ValueError as e:
            print(f"DEBUG: Error parsing segment {segment_num}: {e}")
            continue

    return para_dict
