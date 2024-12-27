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
    with open('eng_temp/temp_long_frame_based_extract_query.txt', 'r', encoding='utf-8') as f:
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

    return get_params_dict(text)


def get_params_dict(output_text):
    """
    input :  gpt output(text)
    output : seg(i)에 해당하는 start/ end time dictionary
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





##만약 GPT 말고 다른 local llm을 사용하고 싶다면 밑에 local_llm 함수 이용하시면 됩니다

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
