import requests
from bs4 import BeautifulSoup

# 크롤링할 API 주소 (지역) | 일단 공허 지역
URL = "https://universe-meeps.leagueoflegends.com/v1/ko_kr/factions/void/index.json"

# API로 데이터 받아오기
response = requests.get(URL)
data = response.json()        #받은 응답을 파이썬 딕셔너리로 변환

# 'associated-champions'라는 키에 챔피언 목록이 들어 있음
champions_data = data.get("associated-champions", [])

# 오류 메시지
if not champions_data:
  print("데이터 없음")
else :
  print("챔피언 목록")
  i = 1
  for champ_data in champions_data:
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
    # biography 안에 full 안에 스토리가 있음 ( quote 축약판도 있음 )
    if "biography" in champ_data and "full" in champ_data["biography"]:
      story = champ_data["biography"]["full"][:300]
      soup = BeautifulSoup(story, 'html.parser')
      origin_story = ' '.join(c for c in soup.strings)
    else:
      origin_story = ""

    #테스트 출력
    print(str(i)+ ". "+ name+" [" + slug+"]" )
    print("    별명:", subtitle)
    print("   스토리:", origin_story)
    print("--------------------------------------------")
    i +=1