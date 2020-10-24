import numpy as np
import cv2


class Unit:
    def __init__(self, lifespan=60, on_food_add=10, aggressive=False):
        self.lifespan = lifespan
        self.on_food_add = on_food_add
        self.aggressive = aggressive

    def move(self):
        pass

    def eat(self):
        pass

    def die(self):
        pass

    def meet(self):
        pass


class Game:
    def __init__(self, board_size: tuple, initial_players: int = 10,
                 initial_food: int = 10, food_max: int = 50, food_fill_to_max=False, ):
        self.board_size = board_size
        self.initial_players = initial_players
        self.initial_food = initial_food
        self.players = 0
        self.food_max = food_max
        self.food_fill_to_max = food_fill_to_max

    def new_game(self):
        pass

    def new_board(self):
        pass

    def spawn_food(self):
        pass

    def spawn_units(self):
        pass

    def show_board(self):
        pass

    def tick_game(self):
        pass
