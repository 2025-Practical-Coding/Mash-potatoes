import openai
import json
import os
import time

# 정의
DATA_FILE = "champ_relationship.json"
RESULT_DATA = "extract_relationship.json"
LOG = "relation_log.log"
MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 256
TEMPERATURE = 0

# json 파일 읽어오는
def read_json(path):
    #python 객체로 반환
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 데이터를 json으로 저장하는 함수
def save_json(path, data):
    # 지정된 경로에 데이터를 JSON 형식으로 저장
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 텍스트 파일에 문자열 리스트를 줄 단위로 저장하는 함수
def save_txt_list(path, lines):
    with open(path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + "\n")

# 로그 메시지 추가 함수
def add_log(msg):
    # 전역 변수 LOG_PATH에 정의된 경로에 로그 메시지를 한 줄 추가
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(msg + "\n")
        