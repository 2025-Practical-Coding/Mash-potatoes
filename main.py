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
            "subtitle": current.subtitle
        } if current else None,

        #마을에 남아있는 대화횟수
        "total_remaining": total_remaining,

        #캐릭터와 남아있는 대화횟수
        "current_remaining": current_remaining
    }

@app.get("/opening")
def get_opening_route():
    """지역 및 캐릭터 오프닝 출력"""
    region = GS.current_region
    if not region:
        raise HTTPException(status_code=404, detail="Game over")
    for c in GS.chosen:
        if GS.conv_counts.get(c.slug, 0) < GS.conv_limit:
            return {"opening": get_opening(GS, c), "slug": c.slug}
    raise HTTPException(status_code=400, detail="All characters in region completed. Call /next to advance.")

@app.post("/chat")
def post_chat(req: ChatRequest = Body(...)):
    """Handle a chat turn, return payload for frontend"""
    # ensure current region
    if not GS.current_region:
        raise HTTPException(status_code=404, detail="Game over")
    # find character
    char = next((c for c in GS.chosen if c.slug == req.slug), None)
    if not char:
        raise HTTPException(status_code=400, detail="Character not in current region")
    # perform chat
    try:
        response = chat_with_character(GS, req.slug, req.user_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response

@app.post("/next")
def next_region():
    """Advance to next region after current completed"""
    if not GS.is_region_complete():
        raise HTTPException(status_code=400, detail="Current region not complete")
    if not GS.next_region():
        return {"game_over": True, "result": GS.result()}
    return {"region": GS.current_region.name, "characters": [c.slug for c in GS.chosen]}

@app.get("/result")
def get_result():
    """Return final game result"""
    if not GS.is_game_over():
        return {"game_over": False}
    return {"game_over": True, "result": GS.result()}
