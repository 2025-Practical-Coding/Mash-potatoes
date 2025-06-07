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
    cur_conv = gs.conv_counts[character.slug] + 1
    is_over = cur_conv >= gs.conv_limit
    system_msg = (
        opening + "\n\n"
        f"당신은 게임 캐릭터 {character.name}({character.subtitle})입니다.\n"
        f"스토리: {character.story}\n\n"
        "유저와 자신의 스토리에 맞춰 몰입하여 대화하세요.\n"
        f"{character.affinity}가 유저에 대한 당신의 호감도 입니다.\n"
        "호감도가 높다면 함께하는 것에 고민하고, 낮다면 함께하지 않겠다고고 대응하세요.\n"
        "긍정적이라도 함께하겠다는 확답은 절대로 하면 안됩니다.\n"
        "아래 **반드시** JSON 코드블록(Triple backticks)으로만 응답하세요:\n"
        "```json\n"
        "{\n"
        "  \"reply\": \"<대화 내용>\",\n"
        "  \"delta\": <호감도 변화량: 정수>,\n"
        "  \"narration\": \"<호감도 변화와 상황 설명 텍스트>\"\n"
        "}```\n"
        "delta 값은 -10에서 10사이의 정수, narration은 delta에 따른 서사적 설명을 포함하세요.\n"
    )
    return [
        {"role": "system", "content": system_msg},
        {"role": "user",   "content": user_input}
    ]

def say_good_bye(gs: GameState, character: Character) -> list[dict]:
    """
    대화가 끝났을 때 응답 생성성
    """
    if character.affinity >= gs.affinity_threshold:
        system_msg = (
            f"당신은 게임 캐릭터 {character.name}({character.subtitle})입니다.\n"
            f"스토리: {character.story}\n\n"
            "당신은 이제 유저와 대화를 마무리하려 합니다.\n"
            "반드시 유저가 가는 길에 함께 하겠다는 응답을 스토리를 기반으로 구성하세요.\n"
            "아래 **반드시** JSON 코드블록(Triple backticks)으로만 응답하세요:\n"
            "```json\n"
            "{\n"
            "  \"reply\": \"<대화 내용>\",\n"
            "  \"narration\": \"<상황 설명 텍스트>\"\n"
            "}```\n"
        )
    else:
        system_msg = (
            f"당신은 게임 캐릭터 {character.name}({character.subtitle})입니다.\n"
            f"스토리: {character.story}\n\n"
            "당신은 이제 유저와 대화를 마무리하려 합니다.\n"
            "유저가 가는 길에 함께하지 않않겠다는 응답을 스토리를 기반으로 구성하세요.\n"
            "아래 **반드시** JSON 코드블록(Triple backticks)으로만 응답하세요:\n"
            "```json\n"
            "{\n"
            "  \"reply\": \"<대화 내용>\",\n"
            "  \"narration\": \"<상황 설명 텍스트>\"\n"
            "}```\n"
        )
    
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": system_msg}
        ],
        max_tokens=350
    )
    text = resp.choices[0].message.content.strip()

    match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
    if match:
        json_str = match.group(1)
    else:
        fallback = re.search(r'\{[\s\S]*\}', text)
        if fallback:
            json_str = fallback.group(0)
        else : 
            print("json parsing error")
            return {
                "region": gs.current_region.name,
                "character": {"slug": character.slug, "name": character.name, "subtitle": character.subtitle},
                "reply": text,               # LLM이 보낸 텍스트 전부
                "narration": "",             # 별도 내러티브 없음
                "total_affinity": character.affinity,
                "conv_count": gs.conv_counts[character.slug],
                "conv_limit": gs.conv_limit
            }
        
    data = json.loads(json_str)
    reply = data.get("reply", "")
    narration = data.get("narration", "")

    return {
        "region": gs.current_region.name,
        "character": {"slug": character.slug, "name": character.name, "subtitle": character.subtitle},
        "reply": reply,               # LLM이 보낸 텍스트 전부
        "narration": narration,             # 별도 내러티브 없음
        "total_affinity": character.affinity,
        "conv_count": gs.conv_counts[character.slug],
        "conv_limit": gs.conv_limit
    }

# def chat_with_character(gs: GameState, slug: str, user_input: str, model: str = "gpt-3.5-turbo") -> tuple[str,int,str]:
def chat_with_character(gs: GameState, slug: str, name: str, user_input: str) -> dict:
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
    match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
    if match:
        json_str = match.group(1)
    else:
        fallback = re.search(r'\{[\s\S]*\}', text)
        if fallback:
            json_str = fallback.group(0)
        else : 
            print("json parsing error")
            return {
                "region": gs.current_region.name,
                "character": {"slug": character.slug, "name": character.name, "subtitle": character.subtitle},
                "user_input": user_input,
                "reply": text,               # LLM이 보낸 텍스트 전부
                "delta": 0,                  # 변화량 0 으로 처리
                "narration": "",             # 별도 내러티브 없음
                "total_affinity": character.affinity,
                "conv_count": gs.conv_counts[slug],
                "conv_limit": gs.conv_limit
            }

    data = json.loads(json_str)
    reply = data.get("reply", "")
    delta = int(data.get("delta", 0))
    narration = data.get("narration", "")

    gs.talk(slug, name, affinity_change=delta)

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

def ending(gs: GameState):
    # 동료 수가 충분한지 확인
    if len(gs.allies) < gs.ally_threshold:
        msg = (
            "당신은 리그 오브 레전드 세계관에 정통한 내러티브 작가입니다.\n"
            "한 유저가 동료를 영입해 바론을 잡으려 했지만 충분한 수의 동료를 영입하지 못한 유저는 바론을 잡는 것에 실패했습니다.\n"
            "이에 맞춰서 바론 도전 결과와 그 이후 마무리 텍스트트를 생성하세요.\n"
            "아래 **반드시** JSON 코드블록(Triple backticks)으로만 응답하세요:\n"
            "```json\n"
            "{\n"
            "  \"narration\": \"<게임 결과 설명 텍스트>\"\n"
            "  \"result\": \"Fail\""
            "}```\n"
        )
    # 동료간 관계 확인인
    elif gs.total_relationship < gs.relationship_threshold:
        msg = (
            "당신은 리그 오브 레전드 세계관에 정통한 내러티브 작가입니다.\n"
            "한 유저가 동료를 영입해 바론을 잡으려 했고 충분한 수의 동료를 영입했지만 몇몇 동료들의 연계가 좋지않아 잡는 것에 실패했습니다.\n"
            "이에 맞춰서 바론 도전 결과와 그 이후 마무리 텍스트를 생성하세요.\n"
            "동료들 간의 서로 사이가 좋지 않은 관계가 있다는 것을 강조하세요.\n"
            "아래 **반드시** JSON 코드블록(Triple backticks)으로만 응답하세요:\n"
            "```json\n"
            "{\n"
            "  \"narration\": \"<게임 결과 설명 텍스트>\"\n"
            "  \"result\": \"Fail\""
            "}```\n"
        )
    else:
        msg = (
            "당신은 리그 오브 레전드 세계관에 정통한 내러티브 작가입니다.\n"
            "한 유저가 동료를 영입해 바론을 잡으려 충분한 수의 동료를 영입했고 동료들의 연계가 훌륭하여 드디어 바론을 잡는 것에 성공했습니다.\n"
            "이에 맞춰서 바론 도전 결과와 그 이후 마무리 텍스트트를 생성하세요.\n"
            "아래 **반드시** JSON 코드블록(Triple backticks)으로만 응답하세요:\n"
            "```json\n"
            "{\n"
            "  \"narration\": \"<게임 결과 설명 텍스트>\"\n"
            "  \"result\": \"Success\""
            "}```\n"
        )
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": msg},
    ],
        max_tokens=350
    )
    text = resp.choices[0].message.content.strip()

    # JSON 블록 추출
    match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
    if match:
        json_str = match.group(1)
    else:
        fallback = re.search(r'\{[\s\S]*\}', text)
        if fallback:
            json_str = fallback.group(0)
        else : 
            print("json parsing error")
            return {
                "game_over": True,
                "narration": "",             # 별도 내러티브 없음
                "result": "",
                "relationship": gs.relationship,
                "alliies": len(gs.allies)
            }

    data = json.loads(json_str)
    narration = data.get("narration", "")
    return {
        "game_over": True,
        "narration": narration,
        "result": "Success",
        "relationship": gs.relationship,
        "alliies": len(gs.allies)
    }