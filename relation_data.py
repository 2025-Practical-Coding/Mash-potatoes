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
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(msg + "\n")

#AI 연동 GPT-3.5-Turbo
# 환경 변수로 키 입력
def api_key():
    return os.getenv("OPENAI_API_KEY")

#API 호출
def call_api(prompt):
    r = openai.chat.completions.create(
        model=MODEL,
        messages = [{"role":"user", "content":prompt}],
        max_tokens = MAX_TOKENS,
        temperature = TEMPERATURE
    )
    return r.choices[0].message.content

#프롬프트 엔지니어링
def prompt_engin(champ, text):
    prompt = (
        f"아래는 롤 챔피언({champ})의 관계에 대한 설명이야.\n"
        f"이 텍스트에서 '{champ}'의 '친구'와 '적'을 각각 , 로 구분해서 한글 이름만 뽑아줘.\n"
        "- 친구 : 긍정적/호의적/신뢰/동맹 등\n"
        "- 적 : 적대적/원수/갈등/반목/숙적 등\n"
        "형식 예시:\n"
        "친구 : 친구1, 친구2, ...\n"
        "적 : 적1, 적2, ...\n\n"
        "텍스트:\n"
        f"{text}\n"
    )
    return prompt

# 결과 반환
def return_friends(line):
    if not line.startswith("친구"):
        return []
    items = line.split(':', 1)[-1]
    return [x.strip() for x in items.split(',') if x.strip() and "없음" not in x]

def return_enemies(line):
    if not line.startswith("적"):
        return []
    items = line.split(':', 1)[-1]
    return [x.strip() for x in items.split(',') if x.strip() and "없음" not in x]

def parse_response(r):
    lines = [l.strip() for l in r.split('\n')]
    friends = []
    enemies = []
    for line in lines:
        if line.startswith("친구"):
            friends = return_friends(line)
        if line.startswith("적"):
            enemies = return_enemies(line)
    return friends, enemies

# 처리 함수
def result_champ(entry):
    champ = entry.get("champ", "")
    text = entry.get("text", "")
    prompt = prompt_engin(champ, text)
    try:
        answer = call_api(prompt)
        friends, enemies = parse_response(answer)
        add_log(f"{champ}: 성공 ({len(friends)}:{len(enemies)})")
        return champ, friends, enemies, None
    except Exception as e:
        add_log(f"{champ}: 실패 ({e})")
        return champ, [], [], e

#출력
def print_stat(idx, total, champ, friends, enemies, err=None):
    if err:
        print(f"[{idx}/{total}] {champ} | 실패 ({err})")
    else:
        print(f"[{idx}/{total}] {champ} | 친구: {', '.join(friends) if friends else '없음'} | 적: {', '.join(enemies) if enemies else '없음'}")

def save_failed_list(failed):
    if failed:
        write_txt_file("failed_champions.txt", failed)
        print("실패 챔피언:", failed)
