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

    NUM_OF_APPLES = 4
    NUM_OF_PITS_START = 0
    NUM_OF_PITS_PER_LEVEL = 8
    MAX_TURNS = 1000
    MAX_PONDS = 3
    MAX_POND_SIZE = 8

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
    BASE = chr(233)

    def __init__(self, random):
        self.random = random
        self.running = True
        self.in_pit = False


        self.player_start_x = 0
        self.player_start_y = 0
        self.max_energy = 200
        self.base_energy = 160
        self.energy = self.base_energy
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


        self.place_rocks(10)
        self.place_pits(self.NUM_OF_PITS_START)
        self.place_apples(self.NUM_OF_APPLES)
        self.place_ponds(self.MAX_POND_SIZE, self.MAX_PONDS)
        self.carve_river()
        
        # place robot and base randomly
        # robot and base cannot start in water
        has_safe_loc = False
        while not has_safe_loc:
            
            # pick a starting x y location that isn't water
            self.player_start_x = self.random.randint(0, self.MAP_WIDTH - 1)
            self.player_start_y = self.random.randint(0, self.MAP_HEIGHT - 1)

            if self.map[(self.player_start_x, self.player_start_y)] != self.WATER:
                has_safe_loc = True # found a safe spot

            self.player_pos = [self.player_start_x, self.player_start_y]
            self.underneath_robot = self.BASE # thing underneath the player

    def add_check_energy(self, amount):
        self.energy += amount
        if self.energy > 200:
            self.energy == 200

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

    def place_rocks(self, count):
        self.place_objects(self.ROCK, count)

    def place_pits(self, count):
        self.place_objects(self.PIT, count)

    def carve_river(self):
        # run a river across the map
        # the river starts on the left or top side of the screen
        # does a random-ish walk until it hits another map boundary
        # if on left, cannot move "west" and prefers "east"
        # if no top, cannot move "north" and prefers "south"

        starts = ["north", "east"]
        start = starts[self.random.randint(0,1)]
        direction = None
        river_x = 0
        river_y = 0

        if start == "north":
            river_x = self.random.randint(0, self.MAP_WIDTH)
            direction = "south"
        else:
            river_y = self.random.randint(0, self.MAP_HEIGHT)
            direction = "west"

        print("River will go %s, starting from (%d, %d)." % (direction, river_x, river_y))

        self.map[(river_x, river_y)] = self.WATER

        hit_edge = False
        while not hit_edge:
            if direction == "south":
                deck = [(0, 1), (0,1), (-1, 0), (1, 0)]
            else:
                deck = [(1, 0), (1,0), (0, -1), (0, 1)]

            self.random.shuffle(deck)
            river_x += deck[0][0]
            river_y += deck[0][1]

            if river_x == self.MAP_WIDTH or river_x < 0:
                hit_edge = True
            elif river_y == self.MAP_HEIGHT or river_y < 0:
                hit_edge = True
            else:
                self.map[(river_x, river_y)] = self.WATER


    def place_ponds(self, max_size, max_count):
        # pick a random location that is at least max_size from
        # right side of screen
        for i in range(self.MAX_PONDS):
            pond_width = self.random.randint(0, max_size) # this pond's width
            if pond_width:
                print("making a pond of width %d..." % (pond_width))
                pond_x = self.random.randint(0, self.MAP_WIDTH - pond_width) # pond x loc
                pond_y = self.random.randint(pond_width, self.MAP_HEIGHT - pond_width) # pond y loc

                # draw pond's initial line
                for j in range(pond_width):
                    self.map[(pond_x + j, pond_y)] = self.WATER

                # draw pond's upper and lower lines
                y_offset = 1 # above and below
                x_offset = 1
                linelen = pond_width - 2
                while linelen > 0:
                    for j in range(linelen):
                        self.map[(pond_x + x_offset + j, pond_y + y_offset)] = self.WATER
                        self.map[(pond_x + x_offset + j, pond_y - y_offset)] = self.WATER
                    linelen -= 2
                    y_offset += 1
                    x_offset += 1

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

        # when robot moves, we restore what was underneath robot
        self.map[(self.player_pos[0], self.player_pos[1])] = self.underneath_robot

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

        # check for collisions and reverse the movement if necessary
        if self.map[(self.player_pos[0], self.player_pos[1])] == self.ROCK:

            self.msg_panel.add("You bumped into a rock!")

            # if the new position is a rock, move robot back
            # but lose your turn

            if key == "w":
                self.player_pos[1] += 1
            elif key == "s":
                self.player_pos[1] -= 1
            elif key == "a":
                self.player_pos[0] += 1
            elif key == "d":
                self.player_pos[0] -= 1

        if key in "wasd":
            self.energy -= 1 # each move costs one E

        # robot can "warp" around the edges of the map
        # this may not be what we want...
        self.player_pos[0] %= self.MAP_WIDTH
        self.player_pos[1] %= self.MAP_HEIGHT


        # robot eats an apple
        if self.map[(self.player_pos[0], self.player_pos[1])] == self.APPLE:
            self.apples_eaten += 1
            self.apples_left -= 1
            self.msg_panel.add("You ate an apple and got 20 energy!")
            self.map[(self.player_pos[0], self.player_pos[1])] = self.EMPTY # apple eaten
            self.add_check_energy(20) # eating an apple gives some energy

        # robot falls into a pit
        elif self.map[(self.player_pos[0], self.player_pos[1])] == self.PIT:
            self.in_pit = True

        # check for collisions and reverse the movement if necessary
        if self.map[(self.player_pos[0], self.player_pos[1])] == self.BASE:

            self.msg_panel.add("You returned to base!")
            if self.energy < self.base_energy:
                self.msg_panel.add("Charging you up to 160!")
                self.energy = self.base_energy
            else:
                self.msg_panel.add("Already above 160.")

        # update new player position
        # save what robot is going to step on
        self.underneath_robot = self.map[(self.player_pos[0], self.player_pos[1])]

        # move robot onto that item
        self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER

        # End of the game
        if self.turns >= self.MAX_TURNS:
            self.running = False
            self.msg_panel.add("You are out of moves.")
        elif self.energy == 0:
            self.running = False
            self.msg_panel.add("You ran out of energy.")
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
        
        bot_vars = {}

        # look for closest apple -- disabled for now
        # x_dir, y_dir = self.find_closest_apple(*self.player_pos)
        #
        # x_dir_to_char = {-1: ord("a"), 1: ord("d"), 0: 0}
        # y_dir_to_char = {-1: ord("w"), 1: ord("s"), 0: 0}

        # bot_vars = {"x_dir": x_dir_to_char[x_dir], "y_dir": y_dir_to_char[y_dir],
        #            "pit_to_east": 0, "pit_to_west": 0, "pit_to_north": 0, "pit_to_south": 0}

        # bot_vars = {"x_dir": x_dir_to_char[x_dir], "y_dir": y_dir_to_char[y_dir],
        #            "pit_to_east": 0, "pit_to_west": 0, "pit_to_north": 0, "pit_to_south": 0}

        # if self.map[((self.player_pos[0]+1)%self.MAP_WIDTH, self.player_pos[1])] == self.PIT:
        #    bot_vars["pit_to_east"] = 1
        # if self.map[((self.player_pos[0]-1)%self.MAP_WIDTH, self.player_pos[1])] == self.PIT:
        #    bot_vars["pit_to_west"] = 1
        # if self.map[(self.player_pos[0], (self.player_pos[1]-1)%self.MAP_HEIGHT)] == self.PIT:
        #    bot_vars["pit_to_north"] = 1
        # if self.map[(self.player_pos[0], (self.player_pos[1]+1)%self.MAP_HEIGHT)] == self.PIT:
        #    bot_vars["pit_to_south"] = 1

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


        self.status_panel["Energy"] = self.energy
        self.status_panel["Apples"] = self.apples_eaten
        self.status_panel["Move"] = str(self.turns) + " of " + str(self.MAX_TURNS)

        for panel in self.panels:
            panel.redraw(frame_buffer)


if __name__ == '__main__':
    from CYLGame import run
    run(AppleFinder)
