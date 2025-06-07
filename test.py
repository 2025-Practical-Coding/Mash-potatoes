from json import load

from dotenv import load_dotenv
import chat_interaction

class GameState:
    def __init__(self):
        self.allies = [1, 2, 3, 4, 5, 6, 7, 8]
        self.current_round = 1
        self.max_rounds = 80
        self.conv_limit = 7
        self.affinity_threshold = 20
        self.ally_threshold = 11
        self.relationship_threshold = 10
        self.relationship = 11


load_dotenv()

gs = GameState()

print(chat_interaction.ending(gs))