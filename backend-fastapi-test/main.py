from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
from pydantic import BaseModel

# 사용자가 보낸 메시지
class ChatRequest(BaseModel):
    user_input: str  # 사용자 입력 메시지
    slug: str        # AI 캐릭터 식별자

# AI가 보내는 응답
class ChatResponse(BaseModel):
    region: str          # 현재 지역
    character: dict      # AI 캐릭터 정보
    user_input: str      # 사용자의 입력 메시지
    reply: str           # AI의 응답
    delta: int           # 친밀도 변화
    narration: str       # 내러티브
    total_affinity: int  # 총 친밀도
    conv_count: int      # 대화 횟수
    conv_limit: int      # 대화 한계

app = FastAPI()

# 기본 ChatResponse 객체 생성 함수
def create_default_response(request: ChatRequest, reply: str) -> ChatResponse:
    character = {
        "slug": request.slug,
        "name": "벨베스",
        "subtitle": "신비한 존재"
    }

    return ChatResponse(
        region="도시",  # 고정된 지역
        character=character,  # 고정된 캐릭터
        user_input=request.user_input,  # 사용자의 입력 메시지
        reply=reply,  # AI의 응답
        delta=random.randint(1, 5),  # 임의의 친밀도 변화
        narration="모험을 떠나는 중입니다.",  # 고정된 내러티브
        total_affinity=50,  # 임의의 총 친밀도
        conv_count=1,  # 대화 횟수
        conv_limit=10  # 대화 한계
    )

# /chat 엔드포인트: 사용자 메시지에 대한 AI 응답 생성
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    ai_reply = generate_ai_reply(request.user_input)
    return create_default_response(request, ai_reply)

# /opening 엔드포인트: 오프닝 메시지 반환
@app.get("/opening", response_model=ChatResponse)
async def opening():
    reply = "안녕하세요, 어떤 지역으로 모험을 떠나실 건가요? (도시, 숲, 공허 중 선택해주세요)"
    return create_default_response(ChatRequest(user_input="", slug="npc_slug"), reply)

# /state 엔드포인트: 현재 상태 반환
@app.get("/state", response_model=ChatResponse)
async def state():
    reply = "현재 상태를 확인하세요."
    return create_default_response(ChatRequest(user_input="", slug="npc_slug"), reply)

# /next 엔드포인트: 다음 지역으로 이동
@app.post("/next", response_model=ChatResponse)
async def next_region():
    reply = "숲으로 이동합니다. 조심하세요!"
    return create_default_response(ChatRequest(user_input="", slug="npc_slug"), reply)

# /result 엔드포인트: 결과 반환
@app.get("/result", response_model=ChatResponse)
async def result():
    reply = "여기까지 모험을 마쳤습니다."
    return create_default_response(ChatRequest(user_input="", slug="npc_slug"), reply)

# AI 응답 생성 함수
def generate_ai_reply(user_input: str) -> str:
    # 입력에 따라 다르게 응답을 생성
    if "도시" in user_input:
        return "도시로 이동합니다. 활기찬 분위기를 느껴보세요!"
    elif "숲" in user_input:
        return "숲으로 가는 길을 안내할게요. 조심하세요!"
    elif "공허" in user_input:
        return "공허로 이동합니다. 신비롭고 위험한 곳이에요."
    else:
        return "무슨 말씀이신지 잘 모르겠어요. 지역을 선택하시려면 '도시로 갈래'처럼 입력해 주세요."
