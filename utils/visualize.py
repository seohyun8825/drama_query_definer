import matplotlib.pyplot as plt
import json
import re

# JSON 파일 경로
json_path = r"C:\Users\user\Thumbnail_Generation\long_time_onestage.json"

# JSON 데이터 로드
with open(json_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# 시간을 초 단위로 변환하는 함수
def parse_time_to_seconds(time_str):
    pattern = r"(\d+):(\d+):(\d+),(\d+)"
    match = re.match(pattern, time_str)
    if match:
        hours, minutes, seconds, milliseconds = map(int, match.groups())
        return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
    return 0

# JSON 데이터에서 시간 정보 추출
def extract_segments_from_json(json_data):
    queries_in_seconds = []
    for item in json_data:
        timeline = item["Timeline"]
        segments = []
        for segment in timeline.values():
            start_time = parse_time_to_seconds(segment["Start Time"])
            end_time = parse_time_to_seconds(segment["End Time"])
            segments.append((start_time, end_time))
        queries_in_seconds.append(segments)
    return queries_in_seconds

# JSON 데이터에서 타임라인 정보 변환
queries_in_seconds = extract_segments_from_json(json_data)

# 비디오 전체 길이 계산 (최대 끝시간)
video_end_time = max(end for query in queries_in_seconds for _, end in query)

# 시각화
fig, ax = plt.subplots(figsize=(12, 8))
for i, query in enumerate(queries_in_seconds):
    bars = [(start, end - start) for start, end in query]
    ax.broken_barh(bars, (i - 0.4, 0.8), facecolors=f"C{i}")

# 그래프 레이블 설정
ax.set_ylim(-1, len(queries_in_seconds))
ax.set_xlim(0, video_end_time)
ax.set_xlabel("Time (seconds)")
ax.set_ylabel("Queries")
ax.set_yticks(range(len(queries_in_seconds)))
ax.set_yticklabels([f"Query {i+1}" for i in range(len(queries_in_seconds))])
ax.grid(True)

plt.title("Timeline Coverage by Queries")

# 그래프 저장
output_path = r"C:\Users\user\Thumbnail_Generation\long_time_two_stage_whole.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()
