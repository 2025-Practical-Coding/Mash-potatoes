from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 – 개발 시 * 허용, 배포 시는 특정 도메인으로 제한
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 핑 테스트용 엔드포인트
@app.get("/ping")
async def ping():
    return "pong"

# 실제 사용될 다른 API도 여기에 추가 가능
