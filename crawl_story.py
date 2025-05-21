import requests
from bs4 import BeautifulSoup

# 설정한 지역마다 챔피언과 해당 데이터 전체 긁어 오는 함수
def get_champions_metaData(region_en):
    URL = f"https://universe-meeps.leagueoflegends.com/v1/ko_kr/factions/{region_en}/index.json"
    result = requests.get(URL)
    data = result.json()
    # 'associated-champions'라는 키에 챔피언 목록이 들어 있음
    return data.get("associated-champions", [])

'''
def dict_champions_data(champ_data):

def print_data(region_kor, champions_metaData):
'''
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
    for region_kor, region_en in regions.items():
        champions_metaData = get_champions_metaData(region_en)
        print_data(region_kor, champions_metaData)