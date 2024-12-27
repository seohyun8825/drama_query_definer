# -*- coding: utf-8 -*-
from model.window_output import GPT4, local_llm
from dotenv import load_dotenv
import os
from moviepy.editor import concatenate_videoclips, VideoFileClip
from datetime import datetime, timedelta
import json
import re
load_dotenv()
api_key = os.getenv('API_KEY')

mapped_json_path = r"C:\Users\user\Thumbnail_Generation\utils\mapped_json.json"


with open(mapped_json_path, 'r', encoding='utf-8') as file:
    frame_to_time_map = json.load(file)
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
            end_time = frame_to_time_map.get(str(end_frame), [None])[1]

            if not start_time or not end_time:
                raise ValueError(f"Frame {start_frame} or {end_frame} could not be mapped to time.")

            # Update the dictionary with mapped times
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
    Merges overlapping or consecutive segments and returns a unified segment dictionary.
    """
    # Sort segments by start time
    sorted_segments = sorted(segments, key=lambda x: x['Start Time'])

    merged_segments = []
    current_segment = sorted_segments[0]

    for next_segment in sorted_segments[1:]:
        if current_segment['End Time'] >= next_segment['Start Time']:
            # Overlapping or consecutive segments, merge them
            current_segment['End Time'] = max(current_segment['End Time'], next_segment['End Time'])
            current_segment['Description'] += f" / {next_segment['Description']}"
        else:
            # No overlap, push the current segment and move to the next
            merged_segments.append(current_segment)
            current_segment = next_segment

    # Append the last segment
    merged_segments.append(current_segment)
    return merged_segments

def split_text_with_overlap(lines, lines_per_chunk=200, overlap=10):
    """
    Split text into chunks with a specified overlap.
    """
    chunks = []
    start = 0
    while start < len(lines):
        # Include the current chunk and the overlap with the next chunk
        end = start + lines_per_chunk
        chunk = lines[start:end]
        if start > 0:
            chunk = lines[start - overlap:end]  # Add overlap from the previous chunk
        chunks.append(chunk)
        start += lines_per_chunk
    return chunks
def extract_script_from_srt(file_path):
    """
    Extracts the text from an SRT file, keeping the segment numbers and grouping lines by their segment.
    Removes timestamps but includes segment numbers and combined text.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    script = []
    index_pattern = re.compile(r"^\d+$")  # Matches subtitle indices
    timestamp_pattern = re.compile(r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})")

    current_segment = []
    current_index = None

    for line in lines:
        line = line.strip()

        # Match segment index
        if index_pattern.match(line):
            if current_segment:
                # Add previous segment to script
                script.append(f"구간 {current_index}\n" + " ".join(current_segment))
                current_segment = []
            current_index = line  # Update the segment index
            continue

        # Skip timestamps
        if timestamp_pattern.match(line):
            continue

        # Add content to the current segment
        if line:
            current_segment.append(line)

    # Add the last segment if it exists
    if current_segment and current_index is not None:
        script.append(f"구간 {current_index}\n" + " ".join(current_segment))

    return script


def read_script_from_txt(file_path):
    """
    Reads and returns the text from a TXT file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()
def process_with_gpt_sliding(prompts, file_path, key, frame_to_time_map, lines_per_chunk=200, overlap=20):
    """
    Process a text file or SRT file in sliding window chunks using GPT.
    """
    lines = extract_script_from_srt(file_path) if file_path.endswith('.srt') else read_script_from_txt(file_path)
    summarization_chunks = split_text_with_overlap(lines, lines_per_chunk, overlap)

    previous_content = ""
    processed_segments = []
    result_data = []

    for chunk_index, chunk in enumerate(summarization_chunks):
        chunk_text = "".join(chunk)
        current_prompt = f"쿼리:{prompts[0]}\n\n현재 내용:\n{chunk_text}"

        try:
            # Generate para_dict using GPT4 function
            para_dict = GPT4(current_prompt, key=key)
            print(f"DEBUG: para_dict for Chunk {chunk_index + 1}: {para_dict}")

            if not para_dict:
                print(f"DEBUG: No valid segments found for Chunk {chunk_index + 1}. Skipping.")
                continue

            # Filter new segments
            new_segments = list(para_dict.values())
            processed_segments.extend(new_segments)

            # Merge overlapping segments
            merged_segments = merge_overlapping_segments(processed_segments)
            print(f"DEBUG: Merged segments after Chunk {chunk_index + 1}: {merged_segments}")

            # Map frames to time
            para_dict_with_time = map_frames_to_time({f"Segment {i + 1}": seg for i, seg in enumerate(merged_segments)}, frame_to_time_map)
            print(f"DEBUG: para_dict_with_time for Chunk {chunk_index + 1}: {para_dict_with_time}")

            result_data.append({
                "Prompt": f"Prompt {chunk_index + 1}",
                "Timeline": para_dict_with_time
            })

            # Update previous content for the next chunk
            previous_content += "\n".join([seg['Description'] for seg in merged_segments])

        except Exception as e:
            print(f"Error processing Chunk {chunk_index + 1}: {e}")
            continue

    return result_data




# Example Usage
file_path = r"C:\Users\user\Thumbnail_Generation\Daebon\Marry_husband_daebon.srt"
prompts = ['''1. 강지원과 경욱 간의 기획안 경쟁
강지원과 경욱은 회사에서 중요한 기획안 발표를 앞두고 치열한 경쟁을 벌인다. 경욱은 회사를 상대로 강하게 자신의 의견을 주장하며 스트라이크를  언급하고, 지원은 그런 경욱에게 자신의 운명을 빼앗길 수 있다고 고백하는 장면이 긴장감을 조성한다. 경욱이 지혁 부장과 대화하는 동안 지원이 자 신의 기획안을 다시 제출하며 경욱으로부터 비판을 받는 장면이 주요 사건으로, 두 사람의 경쟁이 한층 격화된다.

2. 지원과 민환의 관계 회복 시도
지원과 그의 옛 사랑 민환은 서로의 관계 회복을 위해 노력한다. 민환이 예전과 같지 않다고 느낀 지원에게 앞으로 더 신경 쓰겠다고 말하며 관계 회 복을 시도하는 장면이 인상적으로 연출된다. 또한, 두 사람의 대화는 더 깊어지며, 서로에 대한 진심을 다시 확인하는 과정을 보여준다.

3. 희연과 지원의 새로운 관계 형성
희연과 지원은 새로운 관계를 형성하게 된다. 희연이 지원에게 생리대를 부탁하며 그간의 거리감을 허물게 되고, 이후 지원의 선량함을 칭찬하며 함께 식사하자는 제안을 통해 친밀한 관계로 발전하는 모습을 보여준다. 이 장면들은 새로운 우정이 시작되는 과정을 재미있고 따뜻하게 그려낸다.       

4. 동창회 출석을 통해 과거 흑역사를 극복하려는 지원
지원은 과거의 흑역사를 극복하기 위해 동창회 출석을 결심한다. 수민이 동창회 참석을 망설이는 지원을 설득하는 장면에서, 희연이 그를 응원하며 흑역사를 역사로 만들기 위해 가라고 권유하는 부분이 주요 장면이다. 지원은 일과 동창회 약속 사이에서 고민하지만, 긍정적으로 결심하면서 자신의 과거를 극복하고 성장하려는 모습이 잘 드러난다.
''']

# Load frame to time map
with open(mapped_json_path, 'r', encoding='utf-8') as file:
    frame_to_time_map = json.load(file)

result_data = process_with_gpt_sliding(prompts, file_path, api_key, frame_to_time_map)

# Save or inspect results
print(result_data)


# Save result_data to a JSON file
output_file = "long_time_onestage_추가실험_query_rewrite_with요약본.json"
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

def process_video_moviepy(para_dict_with_time, video_path, output_path, time_offset=5):
    """
    Processes video clips based on provided time segments (time-based `para_dict`) and concatenates them.
    """
    clips = []
    for segment_key, segment_info in para_dict_with_time.items():
        # Adjust start and end times using offset
        adjusted_start_time = adjust_time_with_offset(segment_info["Start Time"], time_offset)
        adjusted_end_time = adjust_time_with_offset(segment_info["End Time"], time_offset)

        # Load video and extract subclip
        video = VideoFileClip(video_path)
        clip = video.subclip(adjusted_start_time, adjusted_end_time)  # 오디오 포함 기본 설정
        clips.append(clip)

    # Concatenate clips
    final_video = concatenate_videoclips(clips, method="compose")
    final_output_path = os.path.join(output_path, "final_output_extra_experiment_요약본.mp4")
    final_video.write_videofile(final_output_path, codec="libx264", audio_codec="libmp3lame")

    # 자원 정리
    for clip in clips:
        clip.close()
    final_video.close()

    print(f"Final video saved at: {final_output_path}")

# Define paths
video_path = r"C:\Users\user\Thumbnail_Generation\marry_2.mp4"
output_path = r"C:\Users\user\Thumbnail_Generation\marry_2"


# Combine Timelines
final_segments = []
for chunk in result_data:
    if chunk["Timeline"]:
        final_segments.extend(chunk["Timeline"].values())

# Merge overlapping or consecutive segments
merged_segments = merge_overlapping_segments(final_segments)

# Rebuild para_dict_with_time
para_dict_with_time = {f"Segment {i + 1}": seg for i, seg in enumerate(merged_segments)}

# Process video
process_video_moviepy(para_dict_with_time, video_path, output_path)
