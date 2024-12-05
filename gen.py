# -*- coding: utf-8 -*-
from model.llm_output import GPT4
from dotenv import load_dotenv
import os


load_dotenv()
api_key = os.getenv('API_KEY')
file_path = r"C:\Users\user\Thumbnail_Generation\chatgpt_summarization.txt"

# User query input
prompt = '''

'''
import json

# Define prompts
prompts = [
    "커피 한 잔에 담긴 운명의 비밀 - 지원의 사색",
    "서로 엇갈리는 사랑과 직장 - 지원과 민환의 재회",
    "동창회를 통해 흑역사 극복하기! 희연의 조언",
    "기획안을 둘러싼 치열한 관계 - 경욱, 지원, 수민의 경쟁",
    "웃픈 오해, 망가진 셔츠와 수민의 진심 - 지원의 반응",
    "아버지와 부장님의 사랑 속에서 퇴사 결심 번복한 지원",
    "사무실 데이트 제안? 민환과 지원의 뜨거운 대화",
    "카라멜라떼 속의 진리 - 누가 커피를 가져갔나?",
    "동료의 선량함을 통해 형성된 새로운 관계, 희연과 지원",
    "압박 속 피어난 아이디어! 경욱의 기획안 갈등"
]

# Placeholder for the API key (replace with your actual key)

# Result list to store the JSON data
result_data = []

# Process each prompt
for i, prompt in enumerate(prompts, start=1):
    try:
        # Generate para_dict using GPT4 function
        para_dict = GPT4(prompt, key=api_key, file_path=None)
        
        # Append data in the desired format
        result_data.append({
            "Prompt": f"Prompt {i}",
            "Timeline": para_dict
        })
    except Exception as e:
        print(f"Error processing Prompt {i}: {str(e)}")
        continue

# Save result_data to a JSON file
output_file = "prompt_timelines.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(result_data, f, ensure_ascii=False, indent=4)

print(f"JSON data saved to {output_file}")