import requests
from bs4 import BeautifulSoup
import ujson
import json

# 설정한 지역마다 챔피언과 해당 데이터 전체 긁어 오는 함수
def get_champions_metaData(region_en):
    URL = f"https://universe-meeps.leagueoflegends.com/v1/ko_kr/factions/{region_en}/index.json"
    # 예외처리 부분
    try:
        result = requests.get(URL, timeout = 10) #10초 제한
        result.raise_for_status() 
        data = result.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP 에러 {region_en}: {e}")
        return []
    except requests.exceptions.ConnectionError as e:
        print(f"Conn 에러 {region_en}: {e}")
        return []
    except requests.exceptions.Timeout as e:
        print(f"제한시간초과 에러 {region_en}: {e}")
        return []
    except ValueError as e:
        print(f"Json 파싱 에러 {region_en}: {e}")
        return []
    except Exception as e:
        print(f"에러 [not-find] {region_en}: {e}")
        return []
    
    # 'associated-champions'라는 키에 챔피언 목록이 들어 있음
    return data.get("associated-champions", [])


#단일 챔피언 dict로 만드는 함수
def dict_champions_data(champ_data):
    # 이름
    if "name" in champ_data:
        name = champ_data["name"]
    else:
        name = ""

    # slug (영문 명)
    if "slug" in champ_data:
        slug = champ_data["slug"]
    else:
        slug = ""

    # 별명
    if "subtitle" in champ_data:
        subtitle = champ_data["subtitle"]
    else:
        subtitle = ""

    # 스토리 (일단 일부만)
    if "biography" in champ_data and "full" in champ_data["biography"]:
        story = champ_data["biography"]["full"]
        soup = BeautifulSoup(story, 'html.parser')
        origin_story = ' '.join(c for c in soup.strings)
    else:
        origin_story = ""
    return {
        "name": name,
        "slug": slug,
        "subtitle": subtitle,
        "story": origin_story
    }

#데이터 출력 함수
def print_data(region_kor, champions_metaData):
    # 데이터가 없을 경우 오류 메시지
    if not champions_metaData:
        print(f"[{region_kor}] 데이터 없음")
    else:
        print(f"[{region_kor}] 지역 챔피언 목록")
        i = 1
        for champ_data in champions_metaData:
            champion = dict_champions_data(champ_data)
            print(f"{i}. {champion['name']} [{champion['slug']}]")
            print("    별명:", champion['subtitle'])
            print("    스토리:", champion['story'][:100])
            print("-"*100)
            i += 1


if __name__ == "__main__":
    # 한글 지역이름 : 영문 slug
    regions = {
        "공허": "void",
        "녹서스": "noxus",
        "데마시아": "demacia",
        "밴들시티": "bandle-city",
        "빌지워터": "bilgewater",
        "프렐요드": "freljord",
        "필트오버": "piltover",
        "아이오니아": "ionia",
    }

    result_data = {}

    for region_kor, region_en in regions.items():
        champions_metaData = get_champions_metaData(region_en)

        #테스트용
        print_data(region_kor, champions_metaData)

        #저장
        champion_list = []
        un_dupli_slug_set = set()
        for champ_data in champions_metaData:
            #중복 저장 방지 코드
            slug = champ_data.get("slug", "")
            if slug in un_dupli_slug_set:
                continue
            un_dupli_slug_set.add(slug)
            
            champion = dict_champions_data(champ_data)
            champion_list.append(champion)
        result_data[region_kor] = champion_list

    #ujson으로 빠른 저장
    with open("Data_u.json", "w", encoding="utf-8") as f:
        f.write(ujson.dumps(result_data, ensure_ascii = False))
    print("usjon형식으로 저장 완료")

    #ujson파일을 json으로 변환
    with open("Data_u.json", "r", encoding="utf-8") as f:
        data = ujson.loads(f.read())

    with open("Data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii = False, indent = 2)
    print("json형식으로 저장 완료")