# Drama Query Definer - Preparation Guide

## Preparation

1. 
   ```bash
   git clone https://github.com/seohyun8825/drama_query_definer
   ```

2. 
   ```bash
   conda create -n drama_query python=3.8
   ```

3. 
   ```bash
   conda activate drama_query
   pip install -r requirements.txt
   ```

4. `data/drama` 폴더에 드라마 영상 추가:
   - 드라마 영상을 다운로드하여 `data/drama` 디렉토리에 넣기

5. `.env` 파일 생성:
   - `.env` 파일 안에 OpenAI API 키를 다음과 같이 추가하기
     ```
     API_KEY=your_openai_api_key
     ```

## 실행

### 사건 중심 영상 제작:
```bash
python run_experiment.py --config config/event_search.json
```

### 하이라이트 영상 제작:
```bash
python run_experiment.py --config config/highlight_search.json
```

## Customizing and Extra experiements

1. **`template_path` 변경:**
   - template path를 변경하여 원하는 template을 넣으면 됩니다

2. **`file_path` 업데이트:**
   - 요약본 스크립트, 전체 스크립트, 또는 영어 요약본 중에서 선택하여 처리할 수 있습니다.

3. **additional info**
   - `"use_first_line"`:  추출된 여러 쿼리 중 하나를 사용하여 다음 스텝에 넘겨주기 위해, 임의로 첫 줄만을 사용했습니다. `false` 로 설정하면 추출된 쿼리가 모두 한꺼번에 들어갑니다.
   - `"use_korean"`: `true`로 설정하면 한국어로 처리되며, `false`로 설정하면 영어로 처리됩니다.
   - `"previous_chunk"`: `true`로 설정하면 이전 구간의 요약 내용을 다음 구간을 찾기 위해 포함합니다

## 저장된 결과
저장된 결과는 `result` 폴더 안에 JSON, TXT, 그리고 영상 형태로 저장됩니다.

## Util
1. `result` 폴더에 저장된 JSON 파일을 evaluation을 위한 json 형태로 변환하려면:
   - `utils\convertjson.py`를 사용하여 평가를 위한 JSON 파일로 변환할 수 있습니다.

2. JSON 파일을 기반으로 영상을 만들고 싶다면:
   - `utils\tovideo.py`를 사용하면 됩니다

3. 각 쿼리의 위치를 영상에서 파악하고 시각화해보려면:
   - `utils\visualize.py`를 사용하면 됩니다.


