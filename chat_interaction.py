import os
import re
import json
import random
from openai import OpenAI
from dotenv import load_dotenv
from game_state import GameState, Character

# 환경변수에서 OpenAI 키 로드 및 클라이언트 초기화
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_prompt(gs: GameState, character: Character, user_input: str) -> list[dict]:
    """
    LLM에게 보낼 메시지 리스트 생성
    - system: 현재 지역과 캐릭터 배경 기반 오프닝 + 캐릭터 역할 지시
    - user: 실제 유저 입력
    """
    # 현재 지역 이름
    region = gs.current_region.name if gs.current_region else ""
    # 캐릭터 배경 스토리에서 첫 문장 요약
    story = character.story.replace("\n", " ").strip()
    first_sentence = story.split(".")[0]
    if len(first_sentence) > 100:
        first_sentence = first_sentence[:100] + "..."

    # 동적 오프닝 생성
    opening = (
        f"처음에 {region} 지역에서 {character.name}({character.subtitle})과(와) 마주쳤습니다. "
        f"{first_sentence}. 대화를 시작하세요."
    )

    system_msg = (
        opening + "\n\n"
        f"당신은 게임 캐릭터 {character.name}({character.subtitle})입니다.\n"
        f"스토리: {character.story}\n\n"
        "유저와 몰입하여 대화하세요.\n"
        "응답에는 반드시 다음 양식으로 출력하세요:\n"
        "```json\n"
        "{\n"
        "  \"reply\": \"<대화 내용>\",\n"
        "  \"delta\": <호감도 변화량: 정수>\n"
        "}```\n"
        "delta 값은 -10에서 +10 사이의 정수로, 캐릭터의 성향과 대화 맥락에 맞게 산정하세요."
    )
    return [
        {"role": "system", "content": system_msg},
        {"role": "user",   "content": user_input}
    ]


def chat_with_character(gs: GameState, slug: str, user_input: str, model: str = "gpt-3.5-turbo") -> str:
    """
    1) 현재 선택된 지역에서 slug에 해당하는 캐릭터 조회
    2) LLM 호출로 JSON 응답 생성 (reply, delta)
    3) 파싱된 delta로 GameState.talk 업데이트
    4) 상태와 호감도 출력 후 reply 반환
    """
    if not gs.current_region:
        raise RuntimeError("지역이 선택되지 않았습니다.")

    character = next((c for c in gs.current_region.characters if c.slug == slug), None)
    if not character:
        raise ValueError(f"'{slug}' 캐릭터를 찾을 수 없습니다.")

    messages = get_prompt(gs, character, user_input)
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=200
    )
    text = resp.choices[0].message.content.strip()

    # JSON 블록 추출
    match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
    if match:
        json_str = match.group(1)
    else:
        m2 = re.search(r'{[\s\S]*?}', text)
        if not m2:
            raise ValueError(f"LLM 응답에서 JSON 형식을 찾을 수 없습니다. 응답:\n{text}")
        json_str = m2.group(0)

    parsed = json.loads(json_str)
    reply = parsed.get("reply", "")
    delta = int(parsed.get("delta", 0))

    # 디버그: 추출된 JSON 확인
    print("── Extracted JSON string ──")
    print(json_str)
    print("──────────────────────────")

    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError as e:
        print("JSON 파싱 오류:", e)
        print("잘못된 JSON:", json_str)
        raise

    reply = parsed.get("reply", "")
    delta = int(parsed.get("delta", 0))

    # 게임 상태 업데이트
    gs.talk(slug, affinity_change=delta)

    # 현재 상태 및 캐릭터 호감도 출력
    print(gs)
    print(f"Affinity with {character.slug}: {character.affinity} (Δ{delta})")

    return reply

#반복말고 단순 대화
# if __name__ == "__main__":
#     # 게임 시작: 랜덤 지역 및 캐릭터 선택
#     gs = GameState.load_from_file("Data.json")
#     random.shuffle(gs.regions)
#     gs.next_region()
#     # 현재 지역 및 선택된 캐릭터 중 하나 랜덤
#     region = gs.current_region.name
#     character = random.choice(gs.chosen)
#     slug = character.slug

#     # 오프닝 메시지
#     print(f"처음에 {region} 지역에서 {character.name}({character.subtitle})과(와) 마주쳤습니다.")
#     user_input = input("당신: ")

#     # 대화 실행 및 결과 출력
#     reply = chat_with_character(gs, slug, user_input)
#     print("캐릭터 응답:", reply)
#     print(gs)

if __name__ == "__main__":
    # 1) 게임 초기화
    gs = GameState.load_from_file("Data.json")
    random.shuffle(gs.regions)
    gs.next_region()

    # 2) 메인 루프: 게임 오버가 아닐 동안
    while not gs.is_game_over():
        # a) 현재 지역 & 캐릭터 선택
        region = gs.current_region.name
        character = random.choice(gs.chosen)
        slug = character.slug

        # b) 오프닝 (매 라운드마다도 띄워도 좋고, 지역 입장 시 한 번만)
        print(f"\n-- {region} 지역, 상대: {character.name}({character.subtitle}) --")
        user_input = input("당신: ")

        # c) 대화 호출
        reply = chat_with_character(gs, slug, user_input)
        print(f"{character.name}:", reply)

        # d) 지역 완료 체크: 두 캐릭터 모두 대화가 끝났다면 다음 지역으로
        if gs.is_region_complete():
            print(f">> {region} 지역을 마무리했습니다.")
            gs.next_region()

    # 3) 게임 종료 & 결과
    print("\n게임 종료!", gs)
    print("최종 결과:", gs.result())
