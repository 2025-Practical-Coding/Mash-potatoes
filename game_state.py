import json
from typing import List

class Character:
    def __init__(self, name: str, slug: str, subtitle: str, story: str):
        self.name = name
        self.slug = slug
        self.subtitle = subtitle
        self.story = story
        self.affinity = 0
        self.is_ally = False

    def __repr__(self):
        return f"<Character {self.name} (affinity={self.affinity})>"

class Region:
    def __init__(self, name: str, characters: List[Character]):
        self.name = name
        self.characters = characters

    def __repr__(self):
        return f"<Region {self.name}: {len(self.characters)} characters>"

class GameState:
    def __init__(self, regions: List[Region]):
        self.regions = regions
        self.current_round = 1
        self.max_rounds = 40
        self.allies: List[Character] = []

    @classmethod
    def load_from_file(cls, path: str) -> "GameState":
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        regions = []
        for region_name, char_list in raw.items():
            chars = [Character(**c) for c in char_list]
            regions.append(Region(region_name, chars))
        return cls(regions)

    def __repr__(self):
        return (f"<GameState round {self.current_round}/{self.max_rounds}, "
                f"allies={len(self.allies)}>")
