import requests
from bs4 import BeautifulSoup

ROOT_URL = "https://universe.leagueoflegends.com/ko_KR/region"

REGIONS_URL = {
  "공허" : "void",
  "녹서스" : "noxus",
  "데마시아" : "demacia",
  "밴들시티" : "bandle-city",
  "빌지워터" : "bilgewater",
  "프렐요드" : "freljord",
  "필트오버" : "piltover",
  "아이오니아" : "ionia",
}
