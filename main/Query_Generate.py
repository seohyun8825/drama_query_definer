# -*- coding: utf-8 -*-
from model.llm_output import GPT4
from dotenv import load_dotenv
import os
from moviepy.editor import concatenate_videoclips, VideoFileClip
from datetime import datetime, timedelta
import json
load_dotenv()
api_key = os.getenv('API_KEY')


def run_query_generate(
    prompt, 
    file_path, 
    template_path,
    output_text_file=None,
    use_korean=True 
):
    print("[run_query_generate] calling GPT4...")


    text, _ = GPT4(
        prompt=prompt, 
        key=api_key, 
        file_path=file_path, 
        template_path=template_path,
        use_korean=use_korean  
    )

    if output_text_file:
        with open(output_text_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[run_query_generate] text saved to {output_text_file}")

    return text

