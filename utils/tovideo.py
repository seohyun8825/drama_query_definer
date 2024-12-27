import json
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips


## json 파일(구간이 나와있는) 가지고 영상으로 합치기 위한 python 파일

# convertjson 파이썬 파일을 거쳐서 나온, start - end 로 구성되어있는 json 파일을 
# input json file로 넣으면 해당하는 구간에 맞게 영상으로 재구성해줌

'''
json 파일의 예시 형태
[
    {
        "Start Time": "00:39:15,000",
        "End Time": "00:40:27,000"
    },
    {
        "Start Time": "00:42:07,000",
        "End Time": "00:44:15,000"
    }
]

'''
#여러 인풋도 한꺼번에 처리 가능
input_json_files = [
    "json\short.json",
]


video_path = r"marry_2.mp4"
output_folder = r"C:\Users\user\Thumbnail_Generation\Output"


def process_video_from_json(json_file, video_path, output_path):

    with open(json_file, 'r', encoding='utf-8') as infile:
        time_segments = json.load(infile)
    clips = []
    
    for segment in time_segments:
        start_time = segment["Start Time"]
        end_time = segment["End Time"]
        video = VideoFileClip(video_path)
        clip = video.subclip(start_time, end_time)
        clips.append(clip)

    final_video = concatenate_videoclips(clips, method="compose")
    output_file_name = os.path.splitext(os.path.basename(json_file))[0] + "_output.mp4"
    final_output_path = os.path.join(output_path, output_file_name)
    final_video.write_videofile(final_output_path, codec="libx264", audio_codec="libmp3lame")
    for clip in clips:
        clip.close()
    final_video.close()

    print(f"Processed video saved at: {final_output_path}")

# 출력 폴더 생성
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 각 JSON 파일 처리
for json_file in input_json_files:
    process_video_from_json(json_file, video_path, output_folder)

print("모든 비디오 처리가 완료되었습니다.")
