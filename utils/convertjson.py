import json

#실험에서 최종적으로 나온 json 파일은 segment(i) - description/start/end 로 구성되어있음
#evaluation/시각화를 위해 start - end 로 구성되어있는 json 파일로 변환하기 위한 코드입니다.




#run_experiment 를 돌려서 나온 json 파일을 input file, 원하는 파일명을 output file로 지정하면 됩니다.


input_files = [
    "long_time_onestage_추가실험_query_rewrite_with대본.json",
    "long_time_onestage_추가실험_query_rewrite_with요약본.json",
]

output_files = [
    "json/Query_rewrite_대본1.json",
    "json/Query_rewrite_요약본1.json",
]


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


    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(time_list, outfile, ensure_ascii=False, indent=4)

for input_file, output_file in zip(input_files, output_files):
    extract_last_prompt_segments(input_file, output_file)

print("JSON 파일이 성공적으로 생성되었습니다.")
