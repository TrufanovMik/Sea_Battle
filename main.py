# x,y -  coordinate dot
# long - long of ship
# position vertically or horizontally ship on board
# health - how dot of ship don't shot
# first_coordinate - coordinate of bow of the ship
# list_ship - list ship
# counter - счетчик для записи всех точек которые занимает лодка
# hid - show board or not
# death_boat - how many ships death
# size - size board
# list_cell_states
# busy_dot -  busy dot ship, or it is shoten this dot
#
#


from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "You're trying to shoot the board"


class BoardUsedException(BoardException):
    def __str__(self):
        return "You already shot in this dot"


class BoardWrongShipException(BoardException):
    pass


class Ship:
    represent_ship = "■"

    def __init__(self, first_coordinate, long, position):
        self.long = long
        self.first_cord = first_coordinate
        self.position = position
        self.health = long

    @property
    def dots(self):
        ship_coordinate = []
        for i in range(self.long):
            coord_x = self.first_cord.x
            coord_y = self.first_cord.y

            if self.position == 0:
                coord_x += i

            elif self.position == 1:
                coord_y += i

            ship_coordinate.append(Dot(coord_x, coord_y))
        return ship_coordinate

    def shoten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.list_cell_states = [["-" for x in range(size)] for y in range(size)]
        self.list_ship = []
        self.hid = hid
        self.death_boat = 0
        self.size = size
        self.busy_dot = []

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy_dot:
                    if verb:
                        self.list_cell_states[cur.x][cur.y] = "."
                    self.busy_dot.append(cur)

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy_dot:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.list_cell_states[d.x][d.y] = ship.represent_ship
            self.busy_dot.append(d)

        self.list_ship.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy_dot:
            raise BoardUsedException()

        self.busy_dot.append(d)

        for ship in self.list_ship:
            if d in ship.dots:
                ship.health -= 1
                self.list_cell_states[d.x][d.y] = "X"
                if ship.health == 0:
                    self.death_boat += 1
                    self.contour(ship, verb=True)
                    print("Congratulations, ship was destroyed ")
                    return False
                else:
                    print("Congratulations, ship was hit!")
                    return True

        self.list_cell_states[d.x][d.y] = "."
        print("Sorry, you are missed!")
        return False

    def __str__(self):
        pic_table = ""
        pic_table += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.list_cell_states):
            pic_table += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            pic_table = pic_table.replace("■", "-")
        return pic_table

    def begin(self):
        self.busy_dot = []


class Player:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                goal = self.ask()
                repeat = self.enemy_board.shot(goal)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        dot_shot = Dot(randint(0, 5), randint(0, 5))
        print(f"PC move: {dot_shot.x + 1} {dot_shot.y + 1}")
        return dot_shot


class User(Player):
    def ask(self):
        while True:
            cord = input("Yours move, write x, y: ").split()
            if len(cord) != 2:
                print("You should write only to numbers!")
                continue

            x, y = cord

            if (int(x)) and (int(y)):
                x, y = int(x), int(y)
                return Dot(x - 1, y - 1)
            else:
                print(" Write number!")
                continue


class Game:
    def __init__(self, size=6):
        self.size = size
        player = self.board_search()
        pc = self.board_search()
        pc.hid = True

        self.ai = AI(pc, player)
        self.us = User(player, pc)

    def random_board(self):
        board = None
        while board is None:
            lens = [3, 2, 2, 1, 1, 1, 1]
            board = Board(size=self.size)
            counter = 0
            for len_boat in lens:
                while True:
                    counter += 1
                    if counter > 1000:
                        board = None
                        return board
                    ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), len_boat, randint(0, 1))
                    try:
                        board.add_ship(ship)
                        break
                    except BoardWrongShipException:
                        pass
            board.begin()
        return board

    def board_search(self):
        board = None
        while board is None:
            board = self.random_board()
        return board

    def greet(self):
        print("____________________________")
        print(" Welcome to sea battle game ")
        print("   input format: x y ")
        print(" x - line number  ")
        print(" y - row number ")

    def loop(self):
        num = 0
        while True:
            print("_" * 27)
            print("Players board:")
            print(self.us.board)
            print("_" * 27)
            print("PC board:")
            print(self.ai.board)
            if num % 2 == 0:
                print("_" * 27)
                print("Player move!")
                repeat = self.us.move()
            else:
                print("_" * 27)
                print("PC move!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.death_boat == 7:
                print("_" * 27)
                print("Congratulations, you are wins!")
                break

            if self.us.board.death_boat == 7:
                print("_" * 27)
                print("Sorry, PC wins!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


start_game = Game()
start_game.start()
