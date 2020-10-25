import imutils
import numpy as np
import cv2
import sys
from copy import deepcopy

FOOD_COLOR = (0, 185, 50)
PLAYER_COLOR = (120, 50, 0)
BACKGROUND = (50, 40, 40)


class Unit:
    id_counter = 0

    def __init__(self, lifespan=60, on_food_add=10, aggressive=False):
        Unit.id_counter += 1
        self.id = Unit.id_counter
        self.initial_lifespan = lifespan
        self.lifespan = lifespan
        self.on_food_add = on_food_add
        self.aggressive = aggressive
        self.is_dead = False
        self.age = 0
        self.color = self.random_color()

    def random_color(self):
        red = np.random.randint(50, 200)
        green = np.random.randint(0, 155)
        blue = np.random.randint(50, 255)
        color = (blue, green, red)
        return color

    def generate_move(self):
        random = np.random.randint(-1, 2)
        if np.random.random() > 0.5:
            "Horizontal"
            move = (random, 0)
        else:
            "Vertical"
            move = (0, random)
        return move

    # def make_move(self):
    #     if self.lifespan <= 0:
    #         self.is_dead = True
    #     else:
    #         self.lifespan -= 1

    def make_older(self):
        self.lifespan -= 1
        self.age += 1

    def check_age(self):
        if self.lifespan <= 0:
            self.is_dead = True
            return True

    def eat(self):
        if not self.is_dead:
            self.lifespan += self.on_food_add
            self.is_dead = False

    def meet(self, other):
        print("Hey you.")


class BasePool:
    def __init__(self, initial: int = 10, maximum=10):
        self.initial = initial
        self.maximum = maximum
        self.hash_pos = set()
        self.refs = dict()

    def spawn(self, x, y):
        self.hash_pos.add((x, y))

    def items(self):
        return self.refs.items()

    def __iter__(self):
        return iter(self.hash_pos)

    def __len__(self):
        return len(self.hash_pos)

    def __contains__(self, item):
        is_in = item in self.hash_pos
        # print(item, self.hash_pos, is_in)
        return is_in

    def remove(self, pos):
        self.hash_pos.remove(pos)

    def move_unit(self, pos: tuple, newpos: tuple):
        if newpos != pos:
            unit = self.refs.pop(pos)
            self.refs[newpos] = unit
            self.hash_pos.remove(pos)
            self.hash_pos.add(newpos)


class PlayersPool(BasePool):
    def spawn(self, x, y):
        self.hash_pos.add((x, y))
        self.refs[(x, y)] = Unit()

    def __iter__(self):
        return iter(self.refs.items())

    def remove(self, pos):
        pl = self.refs[pos]
        print(f"Player died at age: {pl.age}")

        self.hash_pos.remove(pos)
        self.refs.pop(pos)


class FoodPool(BasePool):
    pass


class Game:
    def __init__(self, board_size: int, initial_players: int = 10,
                 initial_food: int = 10, max_food: int = 50, food_fill_to_max=False,
                 gridsize=20, frame_delay=100):
        self.board_size = board_size
        self.grid_size = gridsize
        self.output_image_size = (900, 900)

        self.initial_players = initial_players

        self.initial_food = initial_food
        self.max_food = max_food
        self.food_fill_to_max = food_fill_to_max

        self.board = None
        self.players = None
        self.food = None
        self.delay = frame_delay
        self.reset()

    def reset(self, *args, **kwargs):
        self.new_game(*args, **kwargs)

    def new_game(self):
        self.board = self.new_board()
        self.players = PlayersPool(self.initial_players, None)
        self.food = FoodPool(self.initial_food, self.max_food)

        self.spawn_players(fill_to=self.initial_players)
        self.spawn_food(fill_to=self.initial_food)

    def new_board(self):
        board = np.ones((self.board_size, self.board_size, 3))
        board[:, :] = BACKGROUND
        return board

    def spawn_food(self, ammount=0, fill_to=0):
        if ammount:
            N = int(ammount)
        elif fill_to:
            N = fill_to - len(self.food)
        else:
            N = 0
        N = N if N > 0 else 0

        for n in range(N):
            _n = 0
            while True and _n < 10:
                _n += 1
                pos = tuple(np.random.randint(0, self.board_size, 2))
                x, y = pos
                if (not self.check_collision(pos)) and (not self.check_food_collision(pos)):
                    # print(f"Spawned food at: {x, y}")
                    self.food.spawn(x, y)
                    break

    def spawn_players(self, ammount=0, fill_to=0):
        if ammount:
            N = int(ammount)
        elif fill_to:
            N = fill_to - len([p for p in self.players if not p.is_dead])
        else:
            N = 0
        N = N if N > 0 else 0

        for n in range(N):
            _n = 0
            while True and _n < 100:
                _n += 1
                pos = tuple(np.random.randint(0, self.board_size, 2))
                x, y = pos
                if (not self.check_collision(pos)) and (not self.check_food_collision(pos)):
                    # print(f"Spawned player at: {x, y}")
                    self.players.spawn(x, y)
                    break

    def check_collision(self, pos):
        return pos in self.players

    def check_food_collision(self, pos):
        return pos in self.food

    def show_board(self):
        board = self.board.copy()

        for (x, y), player in self.players:
            board[y, x] = player.color

        for (x, y) in self.food:
            # print(f"Food at: {x, y}")
            board[y, x] = FOOD_COLOR

        board = np.array(board, dtype=np.uint8)
        width, height, _ = board.shape
        width *= self.grid_size
        board = imutils.resize(board, width)

        self.draw_grid(board, self.grid_size)

        cv2.imshow("Board", board)
        return board

    @staticmethod
    def draw_grid(image: np.ndarray, cell_size):
        """

        Args:
            image:
            cell_size
        Returns:

        """
        width, height, _ = image.shape
        for x in range(0, width, cell_size):
            for y in range(0, height, cell_size):
                start = (x, y)
                stop = (x + cell_size, y + cell_size)
                cv2.rectangle(image, start, stop, (0, 0, 0), 1)

    def tick_game(self):
        all_pos = list(self.players.hash_pos)
        for cur_pos in all_pos:
            pl = self.players.refs[cur_pos]
            pl.make_older()

            move = pl.generate_move()
            curx, cury = cur_pos
            movex, movey = move
            newx = curx + movex
            newy = cury + movey

            "Validating boundaries"
            if newx < 0:
                newx = 0
            if newx >= self.board_size:
                newx = self.board_size - 1
            if newy < 0:
                newy = 0
            if newy >= self.board_size:
                newy = self.board_size - 1
            new_pos = (newx, newy)

            collision = self.check_collision(new_pos)
            if not collision:
                "Checking if food was in target position"
                was_food_here = self.check_food_collision(new_pos)
                self.players.move_unit(cur_pos, new_pos)
                # pl.make_move()

                if was_food_here:
                    # try:
                    self.food.remove(new_pos)
                    # except KeyError:
                    #     print(self.food.items(), new_pos)
                    #     cv2.waitKey()
                    pl.eat()

            pl.check_age()
            if pl.is_dead and collision:
                self.players.remove(cur_pos)
            elif pl.is_dead:
                self.players.remove(new_pos)

        self.spawn_food(fill_to=self.initial_food)

    def play(self, duration=100):
        self.show_board()
        cv2.waitKey(self.delay)
        for i in range(duration):
            if not i % 100:
                print(i, len(self.players))

            self.tick_game()
            image = self.show_board()
            # cv2.imwrite(f"frames/{i:>03}.png", image)
            key = cv2.waitKey(self.delay)
            if key == ord("q"):
                sys.exit(0)
                
            elif key == ord("-"):
                self.delay += 25
                print(f"New delay: {self.delay}")
            elif key == ord("+"):
                self.delay -= 25
                print(f"New delay: {self.delay}")

            if len(self.players) <= 0:
                break


if __name__ == "__main__":
    game = Game(10, initial_players=20, frame_delay=150, initial_food=10)
    game.play(100)
    print(f"End of game")
    print(f"Players left: {len(game.players)}")
    cv2.waitKey(10_000)
    cv2.destroyAllWindows()
