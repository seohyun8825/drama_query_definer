import json

# 파일 이름 정의
input_files = [
    "요약본기반(한국어)_넘길거1.json",
    "대사 기반(한국어)쿼리 넘길거 2.json",
    "long_time_eng_version_번역본_3번.json",
    "long_time_eng_요약번역본_4번.json",
    "long_time_onestage_번역요약다시번역_5번.json"
]

output_files = [
    "json/한국어요약본기반1.json",
    "json/한국어대본기반2.json",
    "json/영어대본기반3.json",
    "json/영어요약본기반4.json",
    "json/영어요약본의번역본기반5.json"
]

# 데이터 추출 및 저장 함수
def extract_last_prompt_segments(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        data = json.load(infile)

    # 마지막 Prompt에서 모든 Segment의 Start Time과 End Time 추출
    last_prompt = data[-1]  # 마지막 Prompt
    segments = last_prompt['Timeline']

    time_list = []
    for segment in segments.values():
        time_list.append({
            "Start Time": segment['Start Time'],
            "End Time": segment['End Time']
        })

    # JSON 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(time_list, outfile, ensure_ascii=False, indent=4)

# 파일 처리 루프
for input_file, output_file in zip(input_files, output_files):
    extract_last_prompt_segments(input_file, output_file)

print("JSON 파일이 성공적으로 생성되었습니다.")
