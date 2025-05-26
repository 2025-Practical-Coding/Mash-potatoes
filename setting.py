import os
from openai import OpenAI            
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


resp = client.chat.completions.create(
    model="gpt-3.5-turbo",              # 가장 저렴한 대화형 모델
    messages=[{"role": "user", "content": "연동 테스트"}],
    max_tokens=5                        # 응답 토큰도 최소화
)

print("reply:", resp.choices[0].message.content.strip())
print("usage:", resp.usage)
print("  prompt_tokens:", resp.usage.prompt_tokens)
print("  completion_tokens:", resp.usage.completion_tokens)
print("  total_tokens:", resp.usage.total_tokens)


#python3 -m venv venv 최초 가상서버 생성
#source venv/bin/activate  가상서버 실행, if Windows: venv\Scripts\activate

#나중에 Fast API실행
#uvicorn app.main:app --reload --host 0.0.0.0 --port 8000