import imutils
import numpy as np
import cv2

FOOD_COLOR = (0, 185, 50)
PLAYER_COLOR = (120, 50, 0)
BACKGROUND = (30, 20, 10)


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
        # self.position = None

    #
    # def move(self):
    #     pass

    def eat(self):
        if not self.is_dead:
            self.lifespan += self.on_food_add
            self.is_dead = False

    def die(self):
        self.is_dead = True

    def meet(self, other):
        print("Hey you.")


class Pool:
    def __init__(self, initial: int = 10, maximum=10):
        self.initial = initial
        self.maximum = maximum
        self.hash_pos = set()
        self.refs = dict()

    def spawn(self, x, y):
        self.hash_pos.add((x, y))

    def __iter__(self):
        return iter(self.hash_pos)

    def __len__(self):
        return len(self.hash_pos)

    def __contains__(self, item):
        return item in self.hash_pos


class PlayersPool(Pool):
    def spawn(self, x, y):
        self.hash_pos.add((x, y))
        self.refs[(x, y)] = Unit()

    def __iter__(self):
        return iter(self.refs.items())


class FoodPool(Pool):
    pass


class Game:
    def __init__(self, board_size: tuple, initial_players: int = 10,
                 initial_food: int = 10, max_food: int = 50, food_fill_to_max=False, ):
        self.board_size = board_size

        self.initial_players = initial_players

        self.initial_food = initial_food
        self.max_food = max_food
        self.food_fill_to_max = food_fill_to_max

        self.board = None
        self.players = None
        self.food = None

        self.reset()

    def reset(self, *args, **kwargs):
        self.new_game(*args, **kwargs)

    def new_game(self):
        self.board = self.new_board()
        self.players = PlayersPool(self.initial_players, None)
        self.food = Pool(self.initial_food, self.max_food)

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
                x, y = np.random.randint(0, self.board_size, 2)
                if (x, y) not in self.players and (x, y) not in self.food:
                    self.food.spawn(x, y)
                    print(f"Spawned food at: {x, y}")
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
            while True and _n < 10:
                _n += 1
                x, y = np.random.randint(0, self.board_size, 2)
                if (x, y) not in self.players and (x, y) not in self.food:
                    self.players.spawn(x, y)
                    print(f"Spawned player at: {x, y}")
                    break

    def show_board(self):
        board = self.board.copy()

        for (x, y), player in self.players:
            board[y, x] = PLAYER_COLOR

        for (x, y) in self.food:
            print(f"Food at: {x, y}")
            board[y, x] = FOOD_COLOR

        board = np.array(board, dtype=np.uint8)
        board = imutils.resize(board, 500, 500)

        cv2.imshow("Board", board)
        cv2.waitKey(5000)

    def tick_game(self):
        pass


if __name__ == "__main__":
    game = Game(30)
    game.show_board()
    cv2.destroyAllWindows()
