import re
from typing import Any, Dict, List

import requests #HTTP 요청
import ujson as json # 빠른 json 처리
from bs4 import BeautifulSoup #HTML 파싱
from tqdm import tqdm # 진행 상황 시각화

Root_URL = "http://www.snuh.org/health/nMedInfo"

# 개별 상세 페이지를 크롤링하는 함수(의료정보 상세 페이지 하나를 크롤링)
# 입력 :href는 해당 상세 페이지의 하위 경로 ex) nList.do?pageIndex=1
# 반환 : 파싱된 데이터를 딕셔너리(Dict[] 형태로 반환)
def crawl_single_page(href: str) -> Dict[str, Any]:
  # href는 상세페이지 이므로 루트랑 합쳐서 전체 url 구성
  content_page_url = f"{Root_URL}/{href}"
  #웹 페이지 내용 가져오기
  res = requests.get(content_page_url)
  # HTML을 파이썬이 다룰 수 있도록 파씽
  content_page = BeautifulSoup(res.text, "lxml")

  # 주요 정보가 담긴 박스 찾기/ div.mdiInfoView는 주요 컨텐츠 전체를 감싸는 div
  medi_info_box = content_page.find("div", {"class" : "mediInfoView"})


  #제목 추출 및 정제/ text.strip() : 양쪽 공백 제거
  title = medi_info_box.find("div", {"class":"viewTitle"}).text.strip()
  title = " ".join(title.split()) # 공백이 여러 개일 경우 하나로 줄이기


  # 메타 정보 딕셔너리 생성
  meta_info = {} # 작성자, 등록일, 출처 등의 정보를 담을 딕셔너리
  meta_info_box = medi_info_box.find("div", {"class" : "clearFix"})
  for row in meta_info_box.find("div", {"class" : "viewRow"}):
    em = row.find("em") # em은 항목이름
    span = em.find("span") # span으로 보조설명
    if span is not None: #만약 span태그가 없다면
      span.extract() # span 태그 제거 (필요 없는 텍스트)

    key = em.text # 실제 항목명만 남기고 공백 처리
    key = " ".join(key.split()) # key 정제

    value = row.find("p").text # <p>태그 안에 있는 값 추출
    value = " ".join(value.split())

    meta_info[key] = value

  #상세 정보 딕셔너리 생성
  detail_box = medi_info_box.find("div", {"class": "detailWrap" })
  detail_info = {}
  for h5_tag, p_tag in zip(detail_box.find_all("h5"), detail_box.find_all("p")):
    tag = " ".join(h5_tag.text.split()) # 섹션 제목
    content = " ".join(p_tag.text.split()) # 해당 내용
    detail_info[tag] = content

  return{
    "title" : title,
    "url" : content_page_url,
    "meta_info" : meta_info,
    "detail_info" : detail_info,
  }

#전체 페이지를 순회하면 데이터 수집
def crawl_total_pages(crawled_data : List[Dict[str,Any]]):
  with tqdm(total = 124 ) as pbar : # 최대 페이지 수 기준 진행률 표시
    current_page =1
    while True:
      pagination_url = f"{Root_URL}/nList.do?pageIndex={current_page}" # 목록 페이지 url
      res = requests.get(pagination_url)
      list_page = BeautifulSoup(res.text, "lxml")

      # 항목(의학 정보) 리스트 추출
      items = list_page.find("div", {"class": "thumbType04"}).find_all("div",{"class":"item"})
      for item in items:
        href = item.find("div", {"class":"title"}).find("a")["href"] # 상세 페이지 경로

        crawled_datum = crawl_single_page(href) # 상세 정보 크롤링
        crawled_data.append(crawled_datum)

      pbar.update(1) # 진행률 갱신

      # 다음 페이지 존재 여부 확인
      next_href = list_page.find("a", {"class":"nextBtn"})["href"]
      next_page = re.search(r"\((\d+)\)", next_href)
      if next_page is None:
        break

      next_page = int(next_page.group(1))
      if next_page == current_page :
        break; #더이상 다음 페이지로 넘어가지 않음

      current_page += 1 # 페이지 증가



if __name__ == "__main__":
  crawled_data = []

  crawl_total_pages(crawled_data) # 전체 페이지 크롤링
  with open("medical_info.json", "w") as f : #Json 파일로 저장
    json.dump(crawled_data, f, ensure_ascii = False, indent=2)

