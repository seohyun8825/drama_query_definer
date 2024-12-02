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
    """
    SRT 파일에서 번호와 시간을 제외한 대본(텍스트)만 추출하는 함수
    """
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 번호와 시간 제거
    script_lines = re.sub(r'\d+\n|\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', content)
    # 빈 줄 제거
    script_text = '\n'.join([line.strip() for line in script_lines.split('\n') if line.strip()])
    return script_text


def GPT4(prompt, key, srt_path=None):
    url = "https://api.openai.com/v1/chat/completions"
    api_key = key
    with open('template/temp3.txt', 'r', encoding='utf-8') as f:
        template = f.readlines()
    if srt_path:
        script_text = extract_script_from_srt(srt_path)
        prompt = f"{prompt}\n\n 대본:\n{script_text}"
        print("added srt")
        
    user_textprompt=f"프롬프트:{prompt} \n:"
    
    textprompt= f"{' '.join(template)} \n {user_textprompt}"
    
    payload = json.dumps({
    "model": "gpt-4o", # we suggest to use the latest version of GPT, you can also use gpt-4-vision-preivew, see https://platform.openai.com/docs/models/ for details. 
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
    print('waiting for GPT-4 response')
    response = requests.request("POST", url, headers=headers, data=payload)
    obj=response.json()
    text=obj['choices'][0]['message']['content']
    print(text)


    return get_params_dict(text)

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




def test_llm():
    try:
        # 모델과 토크나이저 로드
        print("Loading model and tokenizer...")
        model = AutoModelForCausalLM.from_pretrained(
            "NCSOFT/Llama-VARCO-8B-Instruct",
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        tokenizer = AutoTokenizer.from_pretrained("NCSOFT/Llama-VARCO-8B-Instruct")

        # 간단한 텍스트 프롬프트 생성
        prompt = "What is the capital of France?"
        print(f"Prompt: {prompt}")
        
        model_input = tokenizer(prompt, return_tensors="pt").to("cuda")

        model.eval()

        print("Generating response...")
        with torch.no_grad():
            res = model.generate(**model_input, max_new_tokens=50)[0]
            output = tokenizer.decode(res, skip_special_tokens=True)

        print(f"Model output: {output}")
    except Exception as e:
        print(f"An error occurred: {e}")

