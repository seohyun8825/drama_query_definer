# -*- coding: utf-8 -*-
import json
import os
import argparse
from dotenv import load_dotenv
from main.Query_Generate import run_query_generate
from main.window_generate import run_window_generate

def main():
    parser = argparse.ArgumentParser(description="Run experiment with specified config file.")
    parser.add_argument("--config", type=str, required=True, help="Path to the config file.")
    args = parser.parse_args()

    config_file = args.config
    if not os.path.exists(config_file):
        print(f"Config file '{config_file}' does not exist.")
        return

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    experiment_name = config.get("experiment_name", "no_name")
    steps = config.get("steps", [])
    print(f"=== Running {experiment_name} ===")

    if not steps:
        print("No steps found in config.")
        return

    prev_text_file = None

    for i, step in enumerate(steps):
        step_name       = step["step_name"]
        which_py        = step["which_py"]            
        file_path       = step.get("file_path", "")
        template_path   = step.get("template_path", "")
        prompt          = step.get("prompt", "")
        output_text_file= step.get("output_text_file", "")
        use_first_line = step.get("use_first_line", False)
        use_korean      = step.get("use_korean", True)
        print(f"\n--- STEP {i+1}: {step_name} ---")
        print(f" which_py = {which_py}")
        print(f" file_path = {file_path}")
        print(f" template_path = {template_path}")
        print(f" prompt = {prompt or '[EMPTY]'}")
        print(f" output_text_file = {output_text_file}")

        if not prompt and prev_text_file and os.path.exists(prev_text_file):
            with open(prev_text_file, "r", encoding="utf-8") as f:
                if use_first_line:
                    lines = f.readlines()
                    if lines:
                        prompt = lines[0].rstrip('\n')
                    else:
                        prompt = ""
                    print(f" [INFO] Used only the FIRST line of {prev_text_file} as prompt")
                else:
                    # 전체 내용
                    prompt = f.read()
                    print(f" [INFO] Used ENTIRE content of {prev_text_file} as prompt")

        # 2-2) which_py에 따라 run_query_generate or run_window_generate 실행
        if which_py == "Query_Generate.py":
            text = run_query_generate(
                prompt=prompt,
                file_path=file_path,
                template_path=template_path,
                output_text_file=output_text_file,
                use_korean=use_korean  
            )
            if output_text_file:
                prev_text_file = output_text_file

        elif which_py == "window_generate.py":
            mapped_json_path = step.get("mapped_json_path", "")
            output_json = step.get("output_json", "")
            video_path = step.get("video_path", "")
            output_video_path = step.get("output_video_path", "")
            use_previous_chunk = step.get("previous_chunk", False)

            load_dotenv()
            api_key = os.getenv('API_KEY')

            run_window_generate(
                prompts=[prompt],
                file_path=file_path,
                template_path=template_path,
                key=api_key,
                mapped_json_path=mapped_json_path,
                output_json=output_json,
                video_path=video_path,
                output_video_path=output_video_path,
                use_previous_chunk=use_previous_chunk,
                use_korean=use_korean  
            )

            if output_text_file:
                with open(output_text_file, 'w', encoding='utf-8') as f:
                    f.write("window_generate done.\n")
                prev_text_file = output_text_file

        else:
            print(f"Unknown which_py: {which_py}")
            continue

    print(f"\n=== {experiment_name}: All steps finished ===")

if __name__ == "__main__":
    main()
