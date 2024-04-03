"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
import random
import time
import math


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple([int, int]), size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )


# TODO
# * Define your enemy classes
# * Implement all methods required by the GameElement abstract class
# * Define enemy's update logic in the update() method
# * Check whether the player hits this enemy, then call the
#   self.game.game_over_lose() method in the TurtleAdventureGame class.
# 4 subclasses of enemy class
# Random walking Enemy walk randomly
# Chasing Enemy pursuit the turtle
# Fencing Enemy blocking around the home in a square movement
# ??? Enemy design on my own
class ShakingEnemy(Enemy):
    """
    Random movement and has acceleration
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.speed = 2.5

    def create(self):
        self.__id = self.canvas.create_oval(0,0,0,0, fill = self.color)

    def update(self):
        self.speed += 0.01
        if self.x >= 0 and self.x <= 800:
            if self.y>= 0 and self.y<=500:
                self.x = random.randint(math.floor(self.x - self.speed), math.ceil(self.x + self.speed))
                self.y = random.randint(math.floor(self.y - self.speed),math.ceil(self.y + self.speed))
            elif self.y<=0:
                self.x = random.randint(math.floor(self.x - self.speed), math.ceil(self.x + self.speed))
                self.y = random.randint(math.floor(self.y),math.ceil(self.y + self.speed))       
            else:
                self.x = random.randint(math.floor(self.x - self.speed), math.ceil(self.x + self.speed))
                self.y = random.randint(math.floor(self.y-self.speed),math.ceil(self.y))
        elif self.x <=0:
            if self.y>= 0 and self.y<=500:
                self.x = random.randint(math.floor(self.x), math.ceil(self.x + self.speed))
                self.y = random.randint(math.floor(self.y - self.speed),math.ceil(self.y + self.speed))
            elif self.y<=0:
                self.x = random.randint(math.floor(self.x), math.ceil(self.x + self.speed))
                self.y = random.randint(math.floor(self.y),math.ceil(self.y + self.speed))       
            else:
                self.x = random.randint(math.floor(self.x), math.ceil(self.x + self.speed))
                self.y = random.randint(math.floor(self.y-self.speed),math.ceil(self.y))
        else:
            if self.y>= 0 and self.y<=500:
                self.x = random.randint(math.floor(self.x - self.speed), math.ceil(self.x))
                self.y = random.randint(math.floor(self.y - self.speed),math.ceil(self.y + self.speed))
            elif self.y<=0:
                self.x = random.randint(math.floor(self.x - self.speed), math.ceil(self.x))
                self.y = random.randint(math.floor(self.y),math.ceil(self.y + self.speed))       
            else:
                self.x = random.randint(math.floor(self.x - self.speed), math.ceil(self.x))
                self.y = random.randint(math.floor(self.y-self.speed),math.ceil(self.y))
        if self.hits_player():
            self.game.game_over_lose()

    def render(self):
        self.canvas.coords(self.__id, self.x-self.size/2, self.y-self.size/2, self.x+self.size/2, self.y+self.size/2)

    def delete(self):
        pass

class PursuitEnemy(Enemy):
    """
    Chasing player
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.speed = 1

    def create(self):
        self.__id = self.canvas.create_oval(0,0,0,0, fill = self.color)

    def update(self):
        self.speed += 0.01
        if self.x > self.game.player.x:
            self.x -= math.floor(self.speed)
        elif self.x == self.game.player.x:
            pass
        else:
            self.x += math.floor(self.speed)
        if self.y > self.game.player.y:
            self.y -= math.floor(self.speed)
        elif self.y == self.game.player.y:
            pass
        else:
            self.y += math.floor(self.speed)
        if self.hits_player():
            self.game.game_over_lose()

    def render(self):
        self.canvas.coords(self.__id, self.x-self.size/2, self.y-self.size/2, self.x+self.size/2, self.y+self.size/2)

    def delete(self):
        pass

class AroundHomeEnemy(Enemy):
    """
    Camp around the home
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.x = self.game.home.x - 50
        self.y = self.game.home.y - 50
        self.move_x = 0
        self.move_y = 0
        self.moving_x = True
        self.moving_y = False
        self.move_left = True
        self.move_up = True

    def create(self):
        self.__id = self.canvas.create_rectangle(self.x,self.y,self.x+self.size,self.y+self.size, fill = self.color)

    def update(self):
        if self.moving_x:
            if self.move_left == False:
                self.x += 3
                self.move_x += 3
                if self.move_x >= 100:
                    self.moving_x = False
                    self.moving_y = True
                    self.move_left = True
            else:
                self.x -= 3
                self.move_x -= 3
                if self.move_x <= 0:
                    self.moving_x = False
                    self.moving_y = True
                    self.move_left = False
        else:
            if self.move_up == False:
                self.y += 3
                self.move_y += 3
                if self.move_y >= 100:
                    self.moving_y = False
                    self.moving_x = True
                    self.move_up = True
            else:
                self.y -= 3
                self.move_y -= 3
                if self.move_y <= 0:
                    self.moving_y = False
                    self.moving_x = True    
                    self.move_up = False        
        if self.hits_player():
            self.game.game_over_lose()

    def render(self):
        self.canvas.coords(self.__id, self.x-self.size/2, self.y-self.size/2, self.x+self.size/2, self.y+self.size/2)

    def delete(self):
        pass

class SummonEnemy(Enemy):
    """
    Create a summoner that create scatter shot of minions around it
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.speed = 1

    def create(self):
        self.__id = self.canvas.create_rectangle(0,0,0,0, fill = self.color)

    def update(self):
        if self.x >= self.game.player.x:
            self.x -= math.floor(self.speed)
        elif self.x == self.game.player.x:
            pass
        else:
            self.x += math.floor(self.speed)
        if self.y >= self.game.player.y:
            self.y -= math.floor(self.speed)
        elif self.y == self.game.player.y:
            pass
        else:
            self.y += math.floor(self.speed)
        if self.hits_player():
            self.game.game_over_lose()

    def render(self):
        self.canvas.coords(self.__id, self.x-self.size/2, self.y-self.size/2, self.x+self.size/2, self.y+self.size/2)

    def delete(self):
        pass

class DiagonalMinionEnemy(Enemy):
    """
    Minion of the summoner
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 summoner: SummonEnemy
                 ):
        super().__init__(game, size, color)
        self.__id = None
        self.speed = 2
        self.summoner = summoner
        self.choosing1 = random.choice(["Up","Down"])
        self.choosing2 = random.choice(["Right","Left"])

    def create(self):
        self.__id = self.canvas.create_rectangle(self.x-self.size/2,self.y-self.size/2,self.x+self.size/2,self.y+self.size/2, fill = self.color)

    def update(self):
        self.speed += 0.4
        if self.choosing1 == "Up":
            self.y += self.speed
        else:
            self.y -= self.speed
        if self.choosing2 == "Right":
            self.x += self.speed
        else:
            self.x -= self.speed
        if self.hits_player():
            self.game.game_over_lose()
        if self.x >= 800:
            self.speed = self.speed*-1
        elif self.x <= 0:
            self.speed = self.speed*-1
        if self.y >= 500:
            self.speed = self.speed*-1
        elif self.y <= 0:
            self.speed = self.speed*-1

    def render(self):
        self.canvas.coords(self.__id, self.x-self.size/2, self.y-self.size/2, self.x+self.size/2, self.y+self.size/2)

    def delete(self):
        pass

class StraightMinionEnemy(Enemy):
    """
    Minion of the summoner
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 summoner: SummonEnemy
                 ):
        super().__init__(game, size, color)
        self.__id = None
        self.speed = 2
        self.summoner = summoner
        self.choosing = random.choice(["Up","Down","Right","Left"])

    def create(self):
        self.__id = self.canvas.create_rectangle(self.x-self.size/2,self.y-self.size/2,self.x+self.size/2,self.y+self.size/2, fill = self.color)

    def update(self):
        self.speed += 0.4
        if self.choosing == "Right":
            self.x += math.floor(self.speed)
        elif self.choosing == "Left":
            self.x -= math.floor(self.speed)
        elif self.choosing == "Up":
            self.y += math.floor(self.speed)
        else:
            self.y -= math.floor(self.speed)
        if self.hits_player():
            self.game.game_over_lose()
        if self.x >= 800:
            self.speed = self.speed*-1
        elif self.x <= 0:
            self.speed = self.speed*-1
        if self.y >= 500:
            self.speed = self.speed*-1
        elif self.y <= 0:
            self.speed = self.speed*-1

    def render(self):
        self.canvas.coords(self.__id, self.x-self.size/2, self.y-self.size/2, self.x+self.size/2, self.y+self.size/2)

    def delete(self):
        pass
# TODO
# Complete the EnemyGenerator class by inserting code to generate enemies
# based on the given game level; call TurtleAdventureGame's add_enemy() method
# to add enemies to the game at certain points in time.
#
# Hint: the 'game' parameter is a tkinter's frame, so it's after()
# method can be used to schedule some future events.

class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level

        # example
        self.__game.after(100, self.create_enemy)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_enemy(self):
        """
        Create a new enemy, possibly based on the game level
        """
        new_enemy_r = ShakingEnemy(self.__game, 20, "red")
        new_enemy_r.x = random.randint(200,800)
        new_enemy_r.y = random.randint(0,400)
        self.game.add_element(new_enemy_r)
        new_enemy_p = PursuitEnemy(self.__game, 10, "yellow")
        new_enemy_p.x = random.randint(200,800)
        new_enemy_p.y = random.randint(0,400)
        self.game.add_element(new_enemy_p)
        new_enemy_a = AroundHomeEnemy(self.__game, 25, "blue")
        new_enemy_a.x = self.__game.home.x - 50
        new_enemy_a.y = self.__game.home.y - 50
        self.game.add_element(new_enemy_a)            
        new_enemy_s = SummonEnemy(self.__game, 35, "green")
        new_enemy_s.x = random.randint(200,800)
        new_enemy_s.y = random.randint(0,400)
        self.game.add_element(new_enemy_s)
        for i in range(6):
            self.create_summon(new_enemy_s.x, new_enemy_s.y, new_enemy_s)        
        self.__game.after(3000, self.create_enemy)

    def create_summon(self,x,y, summoner):
        new_enemy_dm = DiagonalMinionEnemy(self.__game, 10, "pink", summoner)
        new_enemy_dm.x = random.randint(x-10,x+10)
        new_enemy_dm.y = random.randint(y-10,y+10)
        self.game.add_element(new_enemy_dm)
        new_enemy_sm = StraightMinionEnemy(self.__game, 10, "pink", summoner)
        new_enemy_sm.x = random.randint(x-10,x+10)
        new_enemy_sm.y = random.randint(y-10,y+10)
        self.game.add_element(new_enemy_sm)

class TurtleAdventureGame(Game): # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
