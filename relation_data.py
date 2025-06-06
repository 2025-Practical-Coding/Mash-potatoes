import openai
import json
import os
import time
from typing import List, Dict, Any, Tuple, Optional

# ========== 설정 ==========
DATA_PATH = "lol_champion_relationships_namu.json"
RESULT_JSON = "lol_champion_relationships_extracted.json"
LOG_PATH = "relation_extractor.log"
OPENAI_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 256
TEMPERATURE = 0

# ========== 로깅 함수 ==========
def log(message: str):
    """간단한 파일 로깅"""
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {message}\n")

# ========== 데이터 로드 ==========
def load_champion_data(path: str) -> List[Dict[str, Any]]:
    """챔피언 json 데이터 파일을 읽어옴"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        log(f"Loaded champion data: {len(data)} champs")
        return data
    except Exception as e:
        log(f"Error loading champion data: {e}")
        raise

# ========== 관계 추출 프롬프트 생성 ==========
def build_prompt(champ: str, text: str) -> str:
    """관계 추출을 위한 프롬프트 생성"""
    prompt = (
        f"아래는 리그오브레전드 챔피언({champ})의 관계 설명입니다.\n"
        f"이 텍스트에서 '{champ}'의 '친구'와 '적'을 각각 쉼표(,)로 구분해서 한글 이름만 뽑아주세요.\n"
        "- 친구: 긍정적/호의적/신뢰/동맹 등\n"
        "- 적: 적대적/원수/갈등/반목/숙적 등\n"
        "형식 예시:\n"
        "친구 : 친구1, 친구2, ...\n"
        "적 : 적1, 적2, ...\n\n"
        "텍스트:\n"
        f"{text}\n"
    )
    return prompt

# ========== 챔피언 이름 정규화 ==========
def normalize_name(name: str) -> str:
    """챔피언 이름 정규화(공백/특수문자 제거 등, 필요에 따라 확장)"""
    return name.strip().replace("•", "").replace(".", "").replace("(", "").replace(")", "")

# ========== GPT 결과 파싱 ==========
def parse_gpt_response(response: str) -> Tuple[List[str], List[str]]:
    """
    GPT 응답에서 친구/적 추출. 없는 경우 빈 리스트 반환.
    """
    friends, enemies = [], []
    lines = response.split('\n')
    for line in lines:
        if line.strip().startswith("친구"):
            friends = [normalize_name(x) for x in line.split(":", 1)[-1].split(",") if x.strip() and "없음" not in x]
        elif line.strip().startswith("적"):
            enemies = [normalize_name(x) for x in line.split(":", 1)[-1].split(",") if x.strip() and "없음" not in x]
    return friends, enemies

# ========== 챔피언관계 추출 클래스 ==========
class ChampionRelationshipExtractor:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.failed_champions: List[str] = []
        self.results: Dict[str, Dict[str, List[str]]] = {}

    def extract_for_champion(self, champ: str, text: str) -> Tuple[List[str], List[str]]:
        """챔피언 하나에 대해 관계 추출. 실패시 예외 처리."""
        prompt = build_prompt(champ, text)
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            answer = response.choices[0].message.content
            friends, enemies = parse_gpt_response(answer)
            log(f"{champ} 추출 완료 | 친구 {len(friends)} | 적 {len(enemies)}")
            return friends, enemies
        except Exception as e:
            log(f"{champ} 관계 추출 실패: {e}")
            self.failed_champions.append(champ)
            return [], []

    def process(self, champion_data: List[Dict[str, Any]]):
        """전체 챔피언 데이터 처리 및 결과 누적 저장"""
        for entry in champion_data:
            champ = entry.get('champ', 'Unknown')
            text = entry.get('text', '')
            friends, enemies = self.extract_for_champion(champ, text)
            self.results[champ] = {
                "friends": friends,
                "enemies": enemies
            }
            # 진행상황 콘솔 출력
            print(f"{champ} | 친구: {', '.join(friends) if friends else '없음'} | 적: {', '.join(enemies) if enemies else '없음'}")
            # 호출 간 rate limit 방지 (1초 대기)
            time.sleep(1)

    def save_results(self, path: str):
        """최종 결과를 JSON 파일로 저장"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            log(f"Saved results to {path}")
        except Exception as e:
            log(f"결과 저장 실패: {e}")
            raise

    def save_failed(self, path: str = "failed_champions.txt"):
        """실패한 챔피언 리스트 저장"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                for champ in self.failed_champions:
                    f.write(champ + "\n")
            log(f"Failed champions saved ({len(self.failed_champions)})")
        except Exception as e:
            log(f"Failed champions 저장 실패: {e}")

# ========== 유틸 함수 ==========
def show_summary(results: Dict[str, Dict[str, List[str]]]):
    """전체 결과 요약 (관계 많은 챔피언 등)"""
    print("\n--- 관계 많은 챔피언 Top 3 ---")
    sorted_by_friends = sorted(results.items(), key=lambda x: len(x[1]["friends"]), reverse=True)
    sorted_by_enemies = sorted(results.items(), key=lambda x: len(x[1]["enemies"]), reverse=True)
    print("친구 많은 챔피언:")
    for champ, rel in sorted_by_friends[:3]:
        print(f"{champ}: {len(rel['friends'])}명")
    print("적 많은 챔피언:")
    for champ, rel in sorted_by_enemies[:3]:
        print(f"{champ}: {len(rel['enemies'])}명")

# ========== 메인 ==========
def main():
    # 환경변수에서 OPENAI_API_KEY 불러오기
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY 환경변수 미설정! export 후 재실행 필요.")
        return

    # 데이터 읽기
    champion_data = load_champion_data(DATA_PATH)

    # 추출기 인스턴스 생성
    extractor = ChampionRelationshipExtractor(api_key)

    # 전체 데이터 처리
    extractor.process(champion_data)

    # 결과 저장 (json)
    extractor.save_results(RESULT_JSON)

    # 실패한 챔피언도 따로 저장
    if extractor.failed_champions:
        extractor.save_failed()

    # 전체 결과 요약 출력
    show_summary(extractor.results)

    print("\n[모든 작업 완료] 결과 파일:", RESULT_JSON)

if __name__ == "__main__":
    main()
