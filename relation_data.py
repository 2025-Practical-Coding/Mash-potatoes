import openai
import json
import os
import time

# 정의
DATA_FILE = "champ_relationship.json"       # 입력 데이터 파일 경로
RESULT_DATA = "extract_relationship.json"   # 결과 데이터저장 파일 경로
LOG = "relation_log.log"                    # 로그 파일 경로
MODEL = "gpt-3.5-turbo"                     # 사용할 3.5터보 모델
MAX_TOKENS = 256                            # 응답 최대 토큰 수
TEMPERATURE = 0                             # 창의성 없이 정확하게 결과 도출

# 데이터 파일 읽기
def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 데이터를 json 파일로 저장
def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 텍스트 리스트를 파일로 저장.
def save_txt_list(path, lines):
    with open(path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + "\n")

# 로그 메시지 파일 추가
def add_log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(msg + "\n")

# api 키 가져오기 (환경 변수로)
def api_key():
    return os.getenv("OPENAI_API_KEY")

# API 호출 함수
def call_api(prompt):
    client = openai.OpenAI(api_key=api_key())
    # 챗 지피티 호출 (프롬프트 엔지니어링 입력으로)
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )
    # 결과 텍스트만 반환하는 코드
    return r.choices[0].message.content

#프롬프트 엔지니어링 부분
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

# 친구 반환 함수
def return_friends(line):
    # '친구'로 시작하는 줄에서 이름만 추출
    if not line.startswith("친구"):
        return []
    items = line.split(':', 1)[-1]
    return [x.strip() for x in items.split(',') if x.strip() and "없음" not in x]

# 적 반환 함수
def return_enemies(line):
    # '적'으로 시작하는 줄에서 이름만 추출
    if not line.startswith("적"):
        return []
    items = line.split(':', 1)[-1]
    return [x.strip() for x in items.split(',') if x.strip() and "없음" not in x]

# gpt응답을 친구/ 적 리스트로 파싱함.
def parse_response(r):
    # 응답에서 각 줄을 분석해 친구/적 추출
    lines = [l.strip() for l in r.split('\n')]
    friends = []
    enemies = []
    for line in lines:
        if line.startswith("친구"):
            friends = return_friends(line)
        if line.startswith("적"):
            enemies = return_enemies(line)
    return friends, enemies

# 관계 추출 함수
def result_champ(entry):
    # 챔피언 이름 부분
    champ = entry.get("champ", "")
    # 설명 부분
    text = entry.get("text", "")
    prompt = prompt_engin(champ, text)
    try:
        # GPT 호출
        answer = call_api(prompt)
        # 응답 파싱
        friends, enemies = parse_response(answer)
        add_log(f"{champ}: 성공 ({len(friends)}:{len(enemies)})")
        return champ, friends, enemies, None
    except Exception as e:
        add_log(f"{champ}: 실패 ({e})")
        return champ, [], [], e

# 진행 상황 및 결과 터미널에 출력 (테스트 용)
def print_stat(idx, total, champ, friends, enemies, err=None):
    if err:
        print(f"[{idx}/{total}] {champ} | 실패 ({err})")
    else:
        print(f"[{idx}/{total}] {champ} | 친구: {', '.join(friends) if friends else '없음'} | 적: {', '.join(enemies) if enemies else '없음'}")

# 실패하면 실패한 것들 모아서 리스트에 저장
def save_failed_list(failed):
    if failed:
        save_txt_list("failed_champions.txt", failed)
        print("실패 챔피언:", failed)

# 메인 함수
def main():
    # API 키가 환경변수로 잘 설정 되었는지 여부 확인
    if not api_key():
        print("OPENAI_API_KEY 환경변수 설정 필요")
        return

    # 데이터 읽기
    try:
        data = read_json(DATA_FILE)
    except Exception as e:
        print("로드 실패:", e)
        return

    #결과 저장
    results = {}
    # 실패한 챔피언 리스트
    failed = []

    #각 챔피언별로 친구/적 관계 추출
    for idx, entry in enumerate(data, 1):
        champ, friends, enemies, err = result_champ(entry)
        results[champ] = {"friends": friends, "enemies": enemies}
        print_stat(idx, len(data), champ, friends, enemies, err)
        if err:
            failed.append(champ)
        # API 과다 호출 방지를 위한 대기 시간 (1초)
        time.sleep(1)

    #결과 저장하는 부분
    try:
        save_json(RESULT_DATA, results)
        print("결과 저장 완료")
    except Exception as e:
        print("결과 저장 실패 | ", e)

    # 실패한 챔피언 저장하는 함수 호출
    save_failed_list(failed)

# 시작.
if __name__ == "__main__":
    main()
