import requests
import json
import re
import os
import torch



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


def GPT4(prompt, key, file_path=None, template_path='template/temp_long_query_rewrite_search.txt', use_korean=True):
    url = "https://api.openai.com/v1/chat/completions"
    api_key = key
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.readlines()

    # SRT 또는 TXT 파일 처리
    if file_path:
        if file_path.endswith('.srt'):
            script_text = extract_script_from_srt(file_path)
            print("Processed SRT file")
        elif file_path.endswith('.txt'):
            script_text = read_script_from_txt(file_path)
            print("Processed TXT file")
        else:
            raise ValueError("Unsupported file type. Only .srt and .txt files are supported.")

        if use_korean:
            prompt = f"{prompt}\n\n 대본:\n{script_text}"
        else:
            prompt = f"{prompt}\n\n script:\n{script_text}"

    if use_korean:
        user_textprompt = f"프롬프트:{prompt} \n:"
    else:
        user_textprompt = f"prompt:{prompt} \n:"

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
    input : gpt 아웃풋(text)
    output : paradict segment[i] 에 해당하는 Description, Start time, End time

    Start time 과 End time은 구간에 저장되고, Description은 다음 window 구간추출에 쓰임.

    """
    pattern = r"(\d+)\.\s*(.+?)\s*\((\d+)\s*-\s*(\d+)\)"

    matches = re.findall(pattern, output_text)

    print(f"debug: Matches found: {matches}")

    if not matches:
        print("debug: No valid matches found in GPT response.")
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


