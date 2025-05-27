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
        f"{region} 지역에서 {character.name}({character.subtitle})과 마주쳤습니다. "
        f"{first_sentence}. 대화를 시작하세요."
    )
    
    system_msg = (
        opening + "\n\n"
        f"당신은 게임 캐릭터 {character.name}({character.subtitle})입니다.\n"
        f"스토리: {character.story}\n\n"
        "유저와 몰입하여 대화하세요.\n"
        "응답에는 반드시 다음 JSON 형식으로 출력하세요:\n"
        "```json\n"
        "{\n"
        "  \"reply\": \"<대화 내용>\",\n"
        "  \"delta\": <호감도 변화량: 정수>,\n"
        "  \"narration\": \"<호감도 변화와 상황 설명 텍스트>\"\n"
        "}```\n"
        "delta 값은 -10에서 +10 사이의 정수, narration은 delta에 따른 서사적 설명을 포함하세요."
    )
    return [
        {"role": "system", "content": system_msg},
        {"role": "user",   "content": user_input}
    ]

# def chat_with_character(gs: GameState, slug: str, user_input: str, model: str = "gpt-3.5-turbo") -> tuple[str,int,str]:
def chat_with_character(gs: GameState, slug: str, user_input: str) -> dict:
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
        raise ValueError(f"Unknown character slug: {slug}")
    
    messages = get_prompt(gs, character, user_input)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=350
    )
    text = resp.choices[0].message.content.strip()

    # JSON 블록 추출
    # match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
    # json_str = match.group(1) if match else re.search(r'{[\s\S]*}', text).group(0)

    match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
    if match:
        json_str = match.group(1)
    else:
        fallback = re.search(r'\{[\s\S]*\}', text)
        if not fallback:
            raise ValueError(f"LLM 응답에 JSON이 없습니다:\n{text}")
        json_str = fallback.group(0)


    data = json.loads(json_str)
    reply = data.get("reply", "")
    delta = int(data.get("delta", 0))
    narration = data.get("narration", "")

    gs.talk(slug, affinity_change=delta)

    return {
        "region": gs.current_region.name,
        "character": {"slug": character.slug, "name": character.name, "subtitle": character.subtitle},
        "user_input": user_input,
        "reply": reply,
        "delta": delta,
        "narration": narration,
        "total_affinity": character.affinity,
        "conv_count": gs.conv_counts[slug],
        "conv_limit": gs.conv_limit
    }

def get_opening(gs: GameState, character: Character) -> str:
    """
    시스템 메시지(get_prompt)의 오프닝 부분을 재사용하여 출력용 오프닝을 반환
    """
    region = gs.current_region.name if gs.current_region else ""
    story = character.story.replace("\n", " ").strip()
    first_sentence = story.split(".")[0][:100]
    if len(first_sentence) > 100:
        first_sentence = first_sentence[:100] + "..."
    return f"{region} 지역에서 {character.name}({character.subtitle})과(와) 마주쳤습니다. {first_sentence}."