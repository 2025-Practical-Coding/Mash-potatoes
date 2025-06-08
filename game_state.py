import json
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from numpy import character

@dataclass
class Relationship:
    friend: List[str]
    enemy: List[str]

@dataclass
class Character:
    name: str
    slug: str
    subtitle: str
    story: str
    affinity: int = 0
    is_ally: bool = False
    relationships: Dict[str, Relationship] = None

@dataclass
class Region:
    name: str
    characters: List[Character]

class GameState:
    def __init__(self, regions: List[Region]):
        self.regions = regions
        self.region_index = -1
        self.current_region: Optional[Region] = None
        self.current_character: Optional[Character] = None
        self.chosen: List[Character] = []
        self.conv_counts: Dict[str, int] = {}
        self.region_conv_counts = 0
        self.allies: List[Character] = []
        self.current_round = 1
        self.max_rounds = 80
        self.conv_limit = 7
        self.affinity_threshold = 20
        self.ally_threshold = 11
        self.relationship_threshold = 10
        self.total_relationship = 15

    @classmethod
    def load_from_file(cls, path1: str, path2: str) -> 'GameState':
        with open(path1, encoding='utf-8') as f:
            data = json.load(f)
        with open(path2, encoding='utf-8') as ext_f:
            ext_data = json.load(ext_f)
        relations = {name: Relationship(info['friends'], info['enemies']) for name, info in ext_data.items()}
        regions = [Region(name, [Character(**c) for c in chars]) for name, chars in data.items()]
        for region in regions:
            for char in region.characters:
                if char.name in relations:
                    char.relationships = relations[char.name]
        # return cls(region)
        return cls(regions)


    def next_region(self) -> bool:
        self.region_index += 1
        if self.region_index >= len(self.regions):
            self.current_region = None
            return False
        self.current_region = self.regions[self.region_index]
        self.chosen = random.sample(self.current_region.characters, 2)
        self.conv_counts = {c.slug: 0 for c in self.chosen}
        self.region_conv_counts = 0
        self.current_character = self.chosen[0]
        return True

    def talk(self, slug: str, name: str, affinity_change: int = 0) -> None:
        if not self.current_region or slug not in self.conv_counts:
            return
        if self.conv_counts[slug] >= self.conv_limit:
            return
        self.conv_counts[slug] += 1
        if self.conv_counts[slug] >= self.conv_limit:
            self.region_conv_counts += 1
        char = next(c for c in self.chosen if c.slug == slug)
        char.affinity += affinity_change
        if char.affinity >= self.affinity_threshold and not char.is_ally:
            char.is_ally = True
            self.allies.append(char)
            for char in self.allies:
                if name in char.relationships['enemies']:
                    self.total_relationship -= 1
                if name in char.relationships['friends']:
                    self.total_relationship += 1
        self.current_round += 1

    def is_region_complete(self) -> bool:
        return self.region_conv_counts >= 2

    def is_game_over(self) -> bool:
        return self.current_round > self.max_rounds or self.current_region is None

    def result(self) -> str:
        return 'Game Clear' if len(self.allies) >= self.ally_threshold else 'Game Over'


# class Character:
#     def __init__(self, name: str, slug: str, subtitle: str, story: str):
#         self.name = name
#         self.slug = slug
#         self.subtitle = subtitle
#         self.story = story
#         self.affinity = 0       # 현재 호감도
#         self.is_ally = False    # 동료 여부

#     def __repr__(self):
#         return f"<Character {self.name} (affinity={self.affinity}, ally={self.is_ally})>"

# class Region:
#     def __init__(self, name: str, characters: List[Character]):
#         self.name = name
#         self.characters = characters

#     def __repr__(self):
#         return f"<Region {self.name}: {len(self.characters)} characters>"

# class GameState:
#     def __init__(self, regions: List[Region]):
#         self.regions = regions
#         self.region_index = -1
#         self.current_region: Optional[Region] = None
#         self.chosen: List[Character] = []         # 현재 지역에서 만날 캐릭터들
#         self.conv_counts: Dict[str, int] = {}     # slug -> 대화 횟수
#         self.allies: List[Character] = []          # 동료 목록
#         self.current_round = 1
#         self.max_rounds = 80                       # 최대 라운드
#         self.conv_limit = 7                        # 캐릭터당 최대 대화 횟수
#         self.affinity_threshold = 20               # 동료 전환 호감도
#         self.ally_threshold = 11                   # 클리어 조건 동료 수

#     @classmethod
#     def load_from_file(cls, path: str) -> "GameState":
#         with open(path, "r", encoding="utf-8") as f:
#             raw = json.load(f)
#         regions = [Region(name, [Character(**c) for c in chars]) for name, chars in raw.items()]
#         return cls(regions)

#     def next_region(self) -> bool:
#         """다음 지역으로 이동하고, 랜덤 캐릭터 2명 선택"""
#         self.region_index += 1
#         if self.region_index >= len(self.regions):
#             self.current_region = None
#             return False
#         self.current_region = self.regions[self.region_index]
#         # 캐릭터 2명 랜덤 선택
#         self.chosen = random.sample(self.current_region.characters, 2)
#         # 대화 횟수 초기화
#         for c in self.chosen:
#             self.conv_counts[c.slug] = 0
#         return True

#     def talk(self, slug: str, affinity_change: int = 0) -> Optional[Character]:
#         """
#         캐릭터와 대화 진행: 대화 횟수+, 호감도 변화, 라운드 진행.
#         conv_limit 초과 시 대화 불가.
#         호감도 threshold 달성 시 동료 추가.
#         """
#         if not self.current_region:
#             return None
#         # 선택된 캐릭터 중 확인
#         char = next((c for c in self.chosen if c.slug == slug), None)
#         if not char:
#             return None
#         count = self.conv_counts.get(slug, 0)
#         if count >= self.conv_limit:
#             return char
#         # 대화 횟수 및 호감도
#         self.conv_counts[slug] = count + 1
#         char.affinity += affinity_change
#         # 동료 전환
#         if char.affinity >= self.affinity_threshold and not char.is_ally:
#             char.is_ally = True
#             self.allies.append(char)
#         # 라운드 증가
#         self.current_round += 1
#         return char

#     def is_region_complete(self) -> bool:
#         """현재 지역의 두 캐릭터와 모두 conv_limit회 대화했는지"""
#         return all(self.conv_counts.get(c.slug, 0) >= self.conv_limit for c in self.chosen)

#     def is_game_over(self) -> bool:
#         """라운드 초과 or 모든 지역 탐색 완료"""
#         return self.current_round > self.max_rounds or self.region_index >= len(self.regions)

#     def result(self) -> str:
#         """게임 결과 반환: 동료 수로 클리어/패배"""
#         if len(self.allies) >= self.ally_threshold:
#             return "Game Clear"
#         return "Game Over"

#     def __repr__(self):
#         region = self.current_region.name if self.current_region else "None"
#         return (
#             f"<GameState round {self.current_round}/{self.max_rounds}, "
#             f"region={region}, allies={len(self.allies)}>"
#         )
