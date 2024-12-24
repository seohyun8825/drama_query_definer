import json
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips

# JSON 파일 목록 정의
input_json_files = [
    "json\short.json",
    "json\영어대본기반3.json",
    "json\영어요약본기반4.json",
    "json\영어요약본의번역본기반5.json",
    "json\한국어대본기반2.json",
    "json\한국어요약본기반1.json"
]

# 비디오 파일 및 출력 경로 정의
video_path = r"marry_2.mp4"
output_folder = r"C:\Users\user\Thumbnail_Generation\Output"

# 비디오 처리 함수
def process_video_from_json(json_file, video_path, output_path):
    # JSON 파일 읽기
    with open(json_file, 'r', encoding='utf-8') as infile:
        time_segments = json.load(infile)

    clips = []
    
    # 각 구간에 대해 클립 생성
    for segment in time_segments:
        start_time = segment["Start Time"]
        end_time = segment["End Time"]

        # 비디오 파일 로드 및 서브클립 생성
        video = VideoFileClip(video_path)
        clip = video.subclip(start_time, end_time)
        clips.append(clip)

    # 클립 병합
    final_video = concatenate_videoclips(clips, method="compose")

    # 출력 파일 이름 생성
    output_file_name = os.path.splitext(os.path.basename(json_file))[0] + "_output.mp4"
    final_output_path = os.path.join(output_path, output_file_name)

    # 비디오 저장
    final_video.write_videofile(final_output_path, codec="libx264", audio_codec="libmp3lame")

    # 자원 정리
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
