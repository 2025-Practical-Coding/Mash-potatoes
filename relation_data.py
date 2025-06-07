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

def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_txt_list(path, lines):
    with open(path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + "\n")

def add_log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(msg + "\n")

def api_key():
    return os.getenv("OPENAI_API_KEY")

# openai 1.x 버전 기준
def call_api(prompt):
    client = openai.OpenAI(api_key=api_key())
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )
    return r.choices[0].message.content

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

def print_stat(idx, total, champ, friends, enemies, err=None):
    if err:
        print(f"[{idx}/{total}] {champ} | 실패 ({err})")
    else:
        print(f"[{idx}/{total}] {champ} | 친구: {', '.join(friends) if friends else '없음'} | 적: {', '.join(enemies) if enemies else '없음'}")

def save_failed_list(failed):
    if failed:
        save_txt_list("failed_champions.txt", failed)
        print("실패 챔피언:", failed)

def main():
    if not api_key():
        print("OPENAI_API_KEY 환경변수 설정 필요")
        return

    try:
        data = read_json(DATA_FILE)
    except Exception as e:
        print("로드 실패:", e)
        return

    results = {}
    failed = []

    for idx, entry in enumerate(data, 1):
        champ, friends, enemies, err = result_champ(entry)
        results[champ] = {"friends": friends, "enemies": enemies}
        print_stat(idx, len(data), champ, friends, enemies, err)
        if err:
            failed.append(champ)
        time.sleep(1)

    try:
        save_json(RESULT_DATA, results)
        print("결과 저장 완료")
    except Exception as e:
        print("결과 저장 실패 | ", e)

    save_failed_list(failed)

if __name__ == "__main__":
    main()
