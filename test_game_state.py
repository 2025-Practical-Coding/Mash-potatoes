from game_state import GameState

def main():
    # 1) JSON 로드
    gs = GameState.load_from_file("Data.json")
    # 2) 기본 상태 출력
    print(gs)
    # 3) 각 지역과 첫 캐릭터 정보 일부를 출력해 보기
    for region in gs.regions:
        print(region)
        # 캐릭터가 비어있지 않다면 첫 번째 캐릭터 정보도 보여주기
        if region.characters:
            print("  첫 캐릭터 예시:", region.characters[0])
    print("✅ GameState 로드 및 객체 생성 성공!")

if __name__ == "__main__":
    main()
