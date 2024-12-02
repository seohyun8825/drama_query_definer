# -*- coding: utf-8 -*-
from model.llm_output import GPT4, local_llm
from dotenv import load_dotenv
import os
from moviepy.editor import concatenate_videoclips, VideoFileClip
from datetime import datetime, timedelta

load_dotenv()
api_key = os.getenv('API_KEY')
srt_path = r"C:\Users\user\Thumbnail_Generation\Marry_husband_daebon.srt"

# User query input
prompt = '''
'''


para_dict = GPT4(prompt, key=api_key, srt_path = srt_path)
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

    # 자원 정리
    for clip in clips:
        clip.close()
    final_video.close()

    print(f"Final video saved at: {final_output_path}")

# Define paths
video_path = r"C:\Users\user\Thumbnail_Generation\marry_2.mp4"
output_path = r"C:\Users\user\Thumbnail_Generation\marry_2"

# Process video
process_video_moviepy(para_dict, video_path, output_path)
