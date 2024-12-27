# -*- coding: utf-8 -*-
from model.llm_output import GPT4
from dotenv import load_dotenv
import os
from moviepy.editor import concatenate_videoclips, VideoFileClip
from datetime import datetime, timedelta
import json
load_dotenv()
api_key = os.getenv('API_KEY')
file_path = r"Daebon\chatgpt_summarization.txt"


################## for one prompt####################

# User query input
prompt = '''
여우 같은 동료와 무능한 상사의 대환장 콜라보 
'''
#para_dict = GPT4(prompt, key=api_key, file_path = None)
####################################################3


prompts = [
    '''
강지원과 경욱 간의 기획안 경쟁
지원과 민환의 관계 회복 시도
희연과 지원의 새로운 관계 형성
동창회 출석을 통해 과거 흑역사를 극복하려는 지원
'''
]

# Placeholder for the API key (replace with your actual key)

# Result list to store the JSON data
result_data = []

# Process each prompt
for i, prompt in enumerate(prompts, start=1):
    try:
        # Generate para_dict using GPT4 function
        para_dict = GPT4(prompt, key=api_key, file_path=file_path)
        
        # Append data in the desired format
        result_data.append({
            "Prompt": f"Prompt {i}",
            "Timeline": para_dict
        })
    except Exception as e:
        print(f"Error processing Prompt {i}: {str(e)}")
        continue

# Save result_data to a JSON file
output_file = "long_time_onestage.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(result_data, f, ensure_ascii=False, indent=4)

print(f"JSON data saved to {output_file}")


def adjust_time_with_offset(time_str, offset=5):
    """
    Adjusts the time string by adding an offset in seconds.
    """
    time_format = "%H:%M:%S,%f"  # Format with milliseconds
    original_time = datetime.strptime(time_str, time_format)
    adjusted_time = original_time + timedelta(seconds=offset)
    return adjusted_time.strftime("%H:%M:%S.%f")[:-3]  # Return adjusted time string in MoviePy format

def process_video_moviepy(para_dict, video_path, output_path, time_offset=5):
    """
    Processes video clips based on provided time segments and concatenates them.
    """
    clips = []
    for segment_key, segment_info in para_dict.items():
        # Adjust start and end times using offset
        adjusted_start_time = adjust_time_with_offset(segment_info["Start Time"], time_offset)
        adjusted_end_time = adjust_time_with_offset(segment_info["End Time"], time_offset)

        # Load video and extract subclip
        video = VideoFileClip(video_path)
        clip = video.subclip(adjusted_start_time, adjusted_end_time)  # 오디오 포함 기본 설정
        clips.append(clip)

    # Concatenate clips
    final_video = concatenate_videoclips(clips, method="compose")
    final_output_path = os.path.join(output_path, "final_output.mp4")
    final_video.write_videofile(final_output_path, codec="libx264", audio_codec="libmp3lame")


    for clip in clips:
        clip.close()
    final_video.close()

    print(f"Final video saved at: {final_output_path}")

# Define paths
video_path = r"C:\Users\user\Thumbnail_Generation\marry_2.mp4"
output_path = r"C:\Users\user\Thumbnail_Generation\marry_2"

# Process video
process_video_moviepy(para_dict, video_path, output_path)
