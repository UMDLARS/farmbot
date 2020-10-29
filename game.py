from __future__ import print_function, division
import math
from CYLGame import GameLanguage
from CYLGame import GridGame
from CYLGame import MessagePanel
from CYLGame import MapPanel
from CYLGame import StatusPanel
from CYLGame import PanelBorder
from CYLGame.Player import DefaultGridPlayer


class AppleFinder(GridGame):
    MAP_WIDTH = 60
    MAP_HEIGHT = 25
    SCREEN_WIDTH = 60
    SCREEN_HEIGHT = MAP_HEIGHT + 6
    MSG_START = 20
    MAX_MSG_LEN = SCREEN_WIDTH - MSG_START - 1
    CHAR_WIDTH = 16
    CHAR_HEIGHT = 16
    GAME_TITLE = "FarmBot 5000"
    CHAR_SET = "resources/farmbot-terminal16x16_gs_ro.png"

    APPLE_EATING_RESPONSES = ["Yummy!", "That hit the spot!", "Wow!", "Amazing!", "So good!",
                              "An apple a day keeps the robots away.", "Yummy in the tummy!", #"Oh my, that was good!",
                              "Bon appetit", "Ewwww, I think that one had a worm."]

    NUM_OF_APPLES = 4
    NUM_OF_PITS_START = 0
    NUM_OF_PITS_PER_LEVEL = 8
    MAX_TURNS = 300

    # will start from the base tile set

    PLAYER = chr(255)
    WATER = chr(247)
    MOUNTAIN = chr(30)
    GROUND = chr(176)
    HOLE = ' '
    BASE = '#'
    # will start by using numbers for plant growth stages
    ROCK = chr(239)
    BEAST = chr(2)
    TREE1 = chr(5)
    TREE2 = chr(6)
    EMPTY = GROUND
    PIT = HOLE
    APPLE = chr(15)
    APPLE = 'O'

    def __init__(self, random):
        self.random = random
        self.running = True
        self.in_pit = False
        centerx = self.MAP_WIDTH // 2
        centery = self.MAP_HEIGHT // 2
        self.player_pos = [centerx, centery]
        self.apples_eaten = 0
        self.apples_left = 0
        self.apple_pos = []
        self.objects = []
        self.turns = 0
        self.level = 0
        self.msg_panel = MessagePanel(self.MSG_START, self.MAP_HEIGHT+1, self.SCREEN_WIDTH - self.MSG_START, 5)
        self.status_panel = StatusPanel(0, self.MAP_HEIGHT+1, self.MSG_START, 5)
        self.panels = [self.msg_panel, self.status_panel]
        self.msg_panel.add("Welcome to " + self.GAME_TITLE + "!!!")
        self.msg_panel.add("Try to grow plants and collect seeds!")

    def init_board(self):
        self.map = MapPanel(0, 0, self.MAP_WIDTH, self.MAP_HEIGHT, self.EMPTY,
                            border=PanelBorder.create(bottom="-"))
        self.panels += [self.map]

        self.place_apples(self.NUM_OF_APPLES)
        self.place_pits(self.NUM_OF_PITS_START)

    def create_new_player(self, prog):
        self.player = DefaultGridPlayer(prog, self.get_move_consts())
        self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER

        self.update_vars_for_player()
        return self.player

    def start_game(self):
        pass

    def place_apples(self, count):
        self.place_objects(self.APPLE, count)
        self.apples_left = self.apples_left + count

    def place_pits(self, count):
        self.place_objects(self.PIT, count)

    def place_objects(self, char, count):
        placed_objects = 0
        while placed_objects < count:
            x = self.random.randint(0, self.MAP_WIDTH - 1)
            y = self.random.randint(0, self.MAP_HEIGHT - 1)

            if self.map[(x, y)] == self.EMPTY:
                self.map[(x, y)] = char
                placed_objects += 1

    def do_turn(self):
        self.handle_key(self.player.move)
        self.update_vars_for_player()

    def handle_key(self, key):
        self.turns += 1

        self.map[(self.player_pos[0], self.player_pos[1])] = self.EMPTY
        if key == "w":
            self.player_pos[1] -= 1
        if key == "s":
            self.player_pos[1] += 1
        if key == "a":
            self.player_pos[0] -= 1
        if key == "d":
            self.player_pos[0] += 1
        if key == "Q":
            self.running = False
            return

        self.player_pos[0] %= self.MAP_WIDTH
        self.player_pos[1] %= self.MAP_HEIGHT
        if self.map[(self.player_pos[0], self.player_pos[1])] == self.APPLE:
            self.apples_eaten += 1
            self.apples_left -= 1
            self.msg_panel.add(self.random.choice(list(set(self.APPLE_EATING_RESPONSES) - set(self.msg_panel.get_current_messages()))))
        elif self.map[(self.player_pos[0], self.player_pos[1])] == self.PIT:
            self.in_pit = True
        self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER

        if self.apples_left == 0:
            self.level += 1
            self.place_apples(self.NUM_OF_APPLES)
            self.place_pits(self.NUM_OF_PITS_PER_LEVEL)

        # End of the game
        if self.turns >= self.MAX_TURNS:
            self.running = False
            self.msg_panel.add("You are out of moves.")
        elif self.in_pit:
            self.running = False
            self.msg_panel.add("You fell into a pit :(")

    def is_running(self):
        return self.running

    def find_closest_apple(self, x, y):
        apple_pos_dist = []
        for pos in self.map.get_all_pos(self.APPLE):
            for i in range(-1, 2):
                for j in range(-1, 2):
                    a_x, a_y = pos[0]+(self.MAP_WIDTH*i), pos[1]+(self.MAP_HEIGHT*j)
                    dist = math.sqrt((a_x-x)**2 + (a_y-y)**2)
                    direction = [a_x-x, a_y-y]
                    if direction[0] > 0:
                        direction[0] = 1
                    elif direction[0] < 0:
                        direction[0] = -1
                    if direction[1] > 0:
                        direction[1] = 1
                    elif direction[1] < 0:
                        direction[1] = -1
                    apple_pos_dist += [(dist, direction)]

        apple_pos_dist.sort()
        if len(apple_pos_dist) > 0:
            return apple_pos_dist[0][1]
        else:
            raise Exception("We didn't find an apple")

    def update_vars_for_player(self):
        x_dir, y_dir = self.find_closest_apple(*self.player_pos)

        x_dir_to_char = {-1: ord("a"), 1: ord("d"), 0: 0}
        y_dir_to_char = {-1: ord("w"), 1: ord("s"), 0: 0}

        bot_vars = {"x_dir": x_dir_to_char[x_dir], "y_dir": y_dir_to_char[y_dir],
                    "pit_to_east": 0, "pit_to_west": 0, "pit_to_north": 0, "pit_to_south": 0}

        if self.map[((self.player_pos[0]+1)%self.MAP_WIDTH, self.player_pos[1])] == self.PIT:
            bot_vars["pit_to_east"] = 1
        if self.map[((self.player_pos[0]-1)%self.MAP_WIDTH, self.player_pos[1])] == self.PIT:
            bot_vars["pit_to_west"] = 1
        if self.map[(self.player_pos[0], (self.player_pos[1]-1)%self.MAP_HEIGHT)] == self.PIT:
            bot_vars["pit_to_north"] = 1
        if self.map[(self.player_pos[0], (self.player_pos[1]+1)%self.MAP_HEIGHT)] == self.PIT:
            bot_vars["pit_to_south"] = 1

        self.player.bot_vars = bot_vars

    @staticmethod
    def default_prog_for_bot(language):
        if language == GameLanguage.LITTLEPY:
            return open("resources/apple_bot.lp", "r").read()

    @staticmethod
    def get_intro():
        return open("resources/intro.md", "r").read()

    def get_score(self):
        return self.apples_eaten

    def draw_screen(self, frame_buffer):
        if not self.running:
            if self.apples_eaten == 0:
                self.msg_panel.add("You ate " + str(self.apples_eaten) + " apples. Better luck next time :(")
            else:
                self.msg_panel.add("You ate " + str(self.apples_eaten) + " apples. Good job!")

        # Update Status
        self.status_panel["Apples"] = self.apples_eaten
        self.status_panel["Move"] = str(self.turns) + " of " + str(self.MAX_TURNS)

        for panel in self.panels:
            panel.redraw(frame_buffer)


if __name__ == '__main__':
    from CYLGame import run
    run(AppleFinder)
