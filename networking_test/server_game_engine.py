import math
import time
import random

from bullet import Bullet
from characters import NPC


def colliderect(rect1, rect2):
    return rect1[0] < rect2[2] and rect1[2] > rect2[0] and rect1[1] < rect2[3] and rect1[3] > rect2[1]


class ServerGameEngine:
    def __init__(self, game_field, players, npcs, *, fps=60):

        self.game_field = game_field
        self.players = players
        self.npcs = npcs
        self.fps = fps
        self.bullets = []
        self.actions_for_players = {}

    def get_game_state_data(self):
        result = {}
        for p in self.players:
            result[p.id] = (p.x, p.y)

        return result

    def set_player_actions(self, player_id, actions):
        self.actions_for_players[player_id] = actions

    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, player_id):
        for idx, p in enumerate(self.players):
            if p.id == player_id:
                self.players.pop(idx)
                return

    def collide(self):
        for idx, npc in enumerate(self.npcs):
            if colliderect(self.player.get_bounding_box(), npc.get_bounding_box()):
                return idx
        return None

    def update_state(self, actions_for_players):
        for npc in self.npcs:
            npc.move(self.game_field)

        for p in self.players:
            player_actions = actions_for_players[p.id] if p.id in actions_for_players else {}

            p.move("left" in player_actions,
                   "right" in player_actions,
                   "up" in player_actions,
                   "down" in player_actions,
                   False, self.game_field)

    def run_game(self):
        self.running = True

        while self.running:
            self.update_state(self.actions_for_players)

            for p in self.players:
                print(p.x, p.y)

            if len(self.players) == 0:
                print("no players")

            time.sleep(1 / self.fps)
