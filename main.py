from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import random
import os
from dotenv import load_dotenv
from game_state import GameState, Character, Region
from chat_interaction import chat_with_character, get_opening

load_dotenv()

# FastAPI app
app = FastAPI(title="RPG Chat Game API")

GS = GameState.load_from_file("Data.json")
random.shuffle(GS.regions)
GS.next_region()

class ChatRequest(BaseModel):
    slug: str
    user_input: str

#현재 상태를 출력하는 api
#대화중인 캐릭터, 8회중 몇번 대화하고있는지 등 정보를 출력함
@app.get("/state")
def get_state():
    """지역, 상태 리턴"""
    region = GS.current_region
    if not region:
        raise HTTPException(status_code=404, detail="Game over")
    # 현재 대화 중인 캐릭터
    current = next((c for c in GS.chosen if GS.conv_counts.get(c.slug, 0) < GS.conv_limit), None)
    # 총 남은 대화 횟수 (모든 캐릭터)
    total_remaining = sum(GS.conv_limit - GS.conv_counts.get(c.slug, 0) for c in GS.chosen)
    # 현재 캐릭터 남은 횟수
    current_remaining = GS.conv_limit - GS.conv_counts.get(current.slug, 0) if current else 0
    return {
        "region": region.name,
        "current_character": {
            "slug": current.slug,
            "name": current.name,
            "subtitle": current.subtitle,
            "affinity" : current.affinity
        } if current else None,

        #마을에 남아있는 대화횟수
        "total_remaining": total_remaining,

        #캐릭터와 남아있는 대화횟수
        "current_remaining": current_remaining
    }


#첫 지역 방문했을때 캐릭터및 지역 랜덤으로 나오게끔 하는 api
#지역당 2캐릭터, 캐리터당 7,8회 대화 했을 때 캐릭터와 지역이 다시 선택되게끔 수정해야함.
@app.get("/opening")
def get_opening_route():
    """지역 및 캐릭터 오프닝 출력"""
    region = GS.current_region
    if not region:
        raise HTTPException(status_code=404, detail="Game over")
    for c in GS.chosen:
        if GS.conv_counts.get(c.slug, 0) < GS.conv_limit:
            GS.current_slug = c.slug
            return {"opening": get_opening(GS, c), "slug": c.slug}
    raise HTTPException(status_code=400, detail="All characters in region completed. Call /next to advance.")

# 사용자가 입력한 대화내용을 보내는 api
# 남아있는 대화 횟수, 호감도, 호감도 상태 메세지 출력함
@app.post("/chat")
def post_chat(req: ChatRequest = Body(...)):
    """Handle a chat turn, return payload for frontend"""
    # ensure current region
    if not GS.current_region:
        raise HTTPException(status_code=404, detail="Game over")
    # find character
    if req.slug != GS.current_slug:
        raise HTTPException(status_code=400, detail="This is not a character you are currently talking to.")
    # perform chat
    try:
        response = chat_with_character(GS, req.slug, req.user_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response

# 7,8회로 1캐릭터와 대화가 종료되었을 때 다른 캐릭터와 대화하게끔 해야함.
# 만약 2명 모두와 대화했을 경우에는 랜덤 지역으로 나오게끔
@app.post("/next")
def next_region():
    """Advance to next region after current completed"""
    if not GS.is_region_complete():
        raise HTTPException(status_code=400, detail="Current region not complete")
    if not GS.next_region():
        return {"game_over": True, "result": GS.result()}
    return {"region": GS.current_region.name, "characters": [c.slug for c in GS.chosen]}


# 게임 종료되었는지 확인하는 api
@app.get("/result")
def get_result():
    """Return final game result"""
    if not GS.is_game_over():
        return {"game_over": False}
    return {"game_over": True, "result": GS.result()}


'''
7번 채웠을때 호감도에 따른 멘트, 만약 n넘을경우 동료가 되는 느낌으로
안될 경우 떠나는 느낌으로

지역 2번 캐릭터 넘어갈시 다른 지역으로 이동하기


7번 단위로 넘어갈 때마다

/next
14번 /next
지역 랜덤으로 다음거 선택하고, Opening 캐릭터도 랜덤 선택해서 return
지역 랜덤 선택, 캐릭터 선택


'''

'''
API 호출 흐름 정리
1. /opening 시작 -> 랜덤 지역, 캐릭터 선택 첫 시작 멘트 출력됨
2. /chat 으로 대화 시작 
   -> return 정보로 대답 및 호감도, 변화 해설 출력, 총 8회중 현재 몇번 남았는지 출력됨
3. if 횟수가 7,8회로 꽉 찼을 경우 
   다시 /opening 출력하게끔 해야함
'''

'''
의존성 API 한번에 다운받을 수 있게끔 requirements.txt 생성
가상환경 아래와 같은 명령어로 실행

# macOS / Linux
source venv/bin/activate

# Windows (CMD)
venv\Scripts\activate

이 후 아래 명령어를 사용하면 의존성 한번에 주입 가능함.

pip install -r requirements.txt 


'''