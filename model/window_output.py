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
    with open('template/temp_long_frame_based_window.txt', 'r', encoding='utf-8') as f:
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
        prompt = f"{prompt}\n\n 대본:\n{script_text}"
        
    user_textprompt = f"프롬프트:{prompt} \n:"
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

#Llama-VARCO-8B-Instruct




def local_llm(prompt):
    '''
    if model_path==None:
        model_id = "Llama-2-13b-chat-hf" 
        #model_id = "Llama-VARCO-8B-Instruct"
    else:
        model_id=model_path
    print('Using model:',model_id)
    model = LlamaForCausalLM.from_pretrained(model_id, load_in_8bit=False, device_map='auto', torch_dtype=torch.float16)
    '''
    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-2-13b-hf",
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-13b-hf")


    with open('template/template.txt', 'r', encoding='utf-8') as f:
        template = f.readlines()

    user_textprompt=f"Caption:{prompt} \n Let's think step by step:"
    textprompt= f"{' '.join(template)} \n {user_textprompt}"
    model_input = tokenizer(textprompt, return_tensors="pt").to("cuda")


    model.eval()
    with torch.no_grad():
        print('waiting for LLM response')
        res = model.generate(**model_input, max_new_tokens=4096)[0]
        output=tokenizer.decode(res, skip_special_tokens=True)
        output = output.replace(textprompt,'')


        print(output)
    return get_params_dict(output)


def get_params_dict(output_text):
    """
    Extract video segments by capturing start and end times using a stack-based approach.
    """
    # Regex to find all time ranges (e.g., 00:01:32,967 --> 00:01:50,350)
    pattern = r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})"
    
    # Find all matches
    matches = re.findall(pattern, output_text)

    # Debugging: Log matches for inspection
    print(f"DEBUG: Matches found: {matches}")
    if not matches:
        raise ValueError("No valid segments found in the response.")

    # Create parameter dictionary
    para_dict = {}
    for i, (start_time, end_time) in enumerate(matches, start=1):
        para_dict[f"Segment {i}"] = {
            "Start Time": start_time.strip(),
            "End Time": end_time.strip()
        }

    return para_dict



def get_params_dict_frame(output_text):
    """
    Convert frame ranges to timestamps using a hardcoded JSON path and store in a dictionary.
    """
    # Hardcoded JSON file path
    mapped_json_path = r"C:\Users\user\Thumbnail_Generation\utils\mapped_json.json"

    # Load mapped JSON file
    with open(mapped_json_path, 'r', encoding='utf-8') as file:
        frame_to_time_map = json.load(file)

    # Regex to find all frame ranges (e.g., 45-64)
    pattern = r"(\d+)\s*-\s*(\d+)"
    matches = re.findall(pattern, output_text)

    # Debugging: Log matches for inspection
    print(f"DEBUG: Matches found: {matches}")
    if not matches:
        raise ValueError("No valid segments found in the response.")

    # Create parameter dictionary
    para_dict = {}
    for i, (start_frame, end_frame) in enumerate(matches, start=1):
        start_frame, end_frame = int(start_frame), int(end_frame)

        # Get timestamps for start and end frames from the JSON map
        start_time = frame_to_time_map.get(str(start_frame), [None])[0]
        end_time = frame_to_time_map.get(str(end_frame), [None])[1]

        if not start_time or not end_time:
            raise ValueError(f"Timestamps not found for frame range {start_frame}-{end_frame}.")

        # Save to dictionary
        para_dict[f"Segment {i}"] = {
            "Start Time": start_time.strip(),
            "End Time": end_time.strip()
        }

    return para_dict



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
