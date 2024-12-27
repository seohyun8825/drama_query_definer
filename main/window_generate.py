# -*- coding: utf-8 -*-

from model.window_output import GPT4
from dotenv import load_dotenv
import os
import json
import re
from datetime import datetime, timedelta
from moviepy.editor import concatenate_videoclips, VideoFileClip

# .env 로드 -> API_KEY
load_dotenv()
api_key = os.getenv('API_KEY')



def map_frames_to_time(para_dict, frame_to_time_map):
    """
    Maps frame numbers to time strings using frame_to_time_map.
    """
    updated_para_dict = {}
    for segment, data in para_dict.items():
        try:
            start_frame = data.get("Start Time")
            end_frame = data.get("End Time")

            # Map frames to time
            start_time = frame_to_time_map.get(str(start_frame), [None])[0]
            end_time   = frame_to_time_map.get(str(end_frame), [None])[1]
            if not start_time or not end_time:
                raise ValueError(f"Frame {start_frame} or {end_frame} not mapped to time.")

            updated_para_dict[segment] = {
                "Description": data.get("Description"),
                "Start Time": start_time,
                "End Time": end_time
            }
        except Exception as e:
            print(f"DEBUG: Error mapping segment {segment}: {e}")

    return updated_para_dict


def merge_overlapping_segments(segments):
    """
    Merges overlapping or consecutive segments and returns a unified segment list.
    """
    if not segments:
        return []

    # Sort segments by start time
    sorted_segments = sorted(segments, key=lambda x: x['Start Time'])

    merged_segments = []
    current_segment = sorted_segments[0]

    for next_segment in sorted_segments[1:]:
        if current_segment['End Time'] >= next_segment['Start Time']:
            # Overlapping 
            current_segment['End Time'] = max(current_segment['End Time'], next_segment['End Time'])
            current_segment['Description'] += f" / {next_segment['Description']}"
        else:
            merged_segments.append(current_segment)
            current_segment = next_segment

    merged_segments.append(current_segment)
    return merged_segments


def split_text_with_overlap(lines, lines_per_chunk=200, overlap=10):
    """
    Split text into chunks with a specified overlap.
    """
    chunks = []
    start = 0
    while start < len(lines):
        end = start + lines_per_chunk
        if start == 0:
            chunk = lines[start:end]
        else:
            # Add overlap from previous chunk
            chunk = lines[start - overlap:end]  
        chunks.append(chunk)
        start += lines_per_chunk
    return chunks


def extract_script_from_srt(file_path):
    """
    Extracts the text from an SRT file, grouping lines by segment index.
    Removes timestamps but includes segment numbers and combined text.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    script = []
    index_pattern = re.compile(r"^\d+$")  
    timestamp_pattern = re.compile(r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})")

    current_segment = []
    current_index = None

    for line in lines:
        line = line.strip()

        # Match segment index
        if index_pattern.match(line):
            # If there's a previous segment, add to script
            if current_segment:
                script.append(f"구간 {current_index}\n" + " ".join(current_segment))
                current_segment = []
            current_index = line  
            continue

        # Skip timestamps
        if timestamp_pattern.match(line):
            continue

        # Add content
        if line:
            current_segment.append(line)

    # Add the last segment
    if current_segment and current_index is not None:
        script.append(f"구간 {current_index}\n" + " ".join(current_segment))

    return script


def read_script_from_txt(file_path):
    """
    Reads and returns lines from a TXT file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()

def process_with_gpt_sliding(
    prompts,
    file_path,
    key,
    frame_to_time_map,
    template_path,
    lines_per_chunk=200,
    overlap=20,
    use_previous_chunk=False, 
    use_korean=True            
):
    """
    1) 파일 읽기 (srt/txt)
    2) split_text_with_overlap
    3) previous_content (옵션) 사용
    4) GPT4 호출
    """
    # 1) 파일 로드
    if file_path.endswith('.srt'):
        lines = extract_script_from_srt(file_path)
    else:
        lines = read_script_from_txt(file_path)

    # 2) 청크 분할
    summarization_chunks = split_text_with_overlap(lines, lines_per_chunk, overlap)

    processed_segments = []
    result_data = []

    # previous_content 초기화
    previous_content = ""

    for chunk_index, chunk in enumerate(summarization_chunks):
        chunk_text = "".join(chunk)

        # 한국어/영어 프롬프트 선택
        if use_korean:
            if use_previous_chunk:
                current_prompt = (
                    f"쿼리:{prompts[0]}\n\n"
                    f"이전 구간 내용:\n{previous_content}\n\n"
                    f"현재 내용:\n{chunk_text}"
                )
            else:
                current_prompt = (
                    f"쿼리:{prompts[0]}\n\n"
                    f"현재 내용:\n{chunk_text}"
                )
        else:
            if use_previous_chunk:
                current_prompt = (
                    f"query:{prompts[0]}\n\n"
                    f"previous content:\n{previous_content}\n\n"
                    f"current content:\n{chunk_text}"
                )
            else:
                current_prompt = (
                    f"query:{prompts[0]}\n\n"
                    f"current content:\n{chunk_text}"
                )

        try:
            para_dict = GPT4(
                current_prompt,
                key=key,
                file_path=None,
                template_path=template_path
            )
            print(f"DEBUG: para_dict for Chunk {chunk_index + 1}: {para_dict}")

            if not para_dict:
                print(f"DEBUG: No valid segments found for Chunk {chunk_index + 1}. Skipping.")
                continue

            # 병합
            new_segments = list(para_dict.values())
            processed_segments.extend(new_segments)
            merged_segments = merge_overlapping_segments(processed_segments)

            print(f"DEBUG: Merged segments after Chunk {chunk_index + 1}: {merged_segments}")

            para_dict_with_time = map_frames_to_time(
                {f"Segment {i+1}": seg for i, seg in enumerate(merged_segments)},
                frame_to_time_map
            )
            print(f"DEBUG: para_dict_with_time for Chunk {chunk_index + 1}: {para_dict_with_time}")

            result_data.append({
                "Prompt": f"Prompt {chunk_index + 1}",
                "Timeline": para_dict_with_time
            })

            if use_previous_chunk:
                desc_texts = [seg["Description"] for seg in merged_segments]
                previous_content = "\n".join(desc_texts)

        except Exception as e:
            print(f"Error processing Chunk {chunk_index+1}: {e}")
            continue

    return result_data




def adjust_time_with_offset(time_str, offset=5):
    """
    영상이 timestamp에 비해 조금씩 밀려있는 경우를 위한 함수입니다. 만약 timestamp랑 영상 초랑 딱 맞아 떨어진다면 사용하지 않아도 됩니다.
    현재 코드에서는 offset=0 으로 사용하지 않는걸로 되어있습니다.
    """
    time_format = "%H:%M:%S,%f"  # Format with milliseconds
    original_time = datetime.strptime(time_str, time_format)
    adjusted_time = original_time + timedelta(seconds=offset)
    return adjusted_time.strftime("%H:%M:%S.%f")[:-3]


def process_video_moviepy(para_dict_with_time, video_path, output_path, time_offset=0):
    """
    Processes video clips based on provided time segments (time-based para_dict) and concatenates them.
    """
    clips = []
    for segment_key, segment_info in para_dict_with_time.items():
        # Adjust times
        adjusted_start = adjust_time_with_offset(segment_info["Start Time"], time_offset)
        adjusted_end   = adjust_time_with_offset(segment_info["End Time"], time_offset)

        video = VideoFileClip(video_path)
        clip  = video.subclip(adjusted_start, adjusted_end) 
        clips.append(clip)

    final_video = concatenate_videoclips(clips, method="compose")
    final_output_path = os.path.join(output_path, "generated.mp4")
    final_video.write_videofile(final_output_path, codec="libx264", audio_codec="libmp3lame")

    for c in clips:
        c.close()
    final_video.close()

    print(f"Final video saved at: {final_output_path}")


####################################################
#run window generate // main으로 돌아가는 함수입니다
####################################################
def run_window_generate(
    prompts,
    file_path,
    template_path,        
    key,
    mapped_json_path,
    output_json,
    video_path,
    output_video_path,
    lines_per_chunk=200,
    overlap=20,
    use_previous_chunk=False,
    use_korean=True 
):
    """
    1) frame_to_time_map
    2) process_with_gpt_sliding(...) 호출해 result_data 받아오기
    3) result_data를 output_json에 저장
    4) segments 병합 -> 영상 생성
    """

    with open(mapped_json_path, 'r', encoding='utf-8') as file:
        frame_to_time_map = json.load(file)


    result_data = process_with_gpt_sliding(
        prompts=prompts,
        file_path=file_path,
        key=key,
        frame_to_time_map=frame_to_time_map,
        template_path=template_path,  
        lines_per_chunk=lines_per_chunk,
        overlap=overlap,
        use_previous_chunk=use_previous_chunk, 
        use_korean=use_korean 
    )

    print("=== Sliding GPT result_data ===")
    print(result_data)

    # 3) 결과 JSON 저장
    with open(output_json, "w", encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=4)
    print(f"JSON data saved to {output_json}")

    # 4) segments 병합 -> 영상 처리
    final_segments = []
    for chunk in result_data:
        if chunk["Timeline"]:
            final_segments.extend(chunk["Timeline"].values())

    merged_segments = merge_overlapping_segments(final_segments)
    para_dict_with_time = {f"Segment {i+1}": seg for i, seg in enumerate(merged_segments)}

    if para_dict_with_time:
        process_video_moviepy(para_dict_with_time, video_path, output_video_path)
