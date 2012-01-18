from random import random, randint
from functools import partial

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color
from kivy.graphics.vertex_instructions import *
from kivy.properties import BooleanProperty, StringProperty, NumericProperty

from food import Food, Junk
from fish import Fish
from ship import Ship


class FishLifeBones(App):
    def __init__(self, **kwargs):
        super(FishLifeBones, self).__init__(**kwargs)
        self.ships = []       
        
    def build_config(self, config):
        config.setdefaults('aquarium', {"waterline":200})
        
    def build(self):
        self.welcome_screen = Widget(width=Window.width, height=Window.height)
        begin = Button(text="Feed the Fish!")
        begin.bind(on_release=self.scene_gameplay)
        self.welcome_screen.add_widget(begin)
        
        self.game_screen = Widget(width=Window.width, height=Window.height)
        self.menu = GridLayout(cols=2, row_force_default=True, row_default_height=100, width=Window.width, height=100, pos=(0,0))
        self.menu.add_widget(Label(text="Starvation Meter", width=100))
        self.calories_bar = ProgressBar(max=1000, value=1000)
        self.menu.add_widget(self.calories_bar)
        self.game_area = Widget(width=Window.width, height=Window.height)
        with self.game_area.canvas:
            Color(1,1,1)
            Rectangle(source="images/bg.png", pos=self.game_area.pos, size=self.game_area.size)
        self.waves = Image(source="images/waves.png", pos=(0, self.game_screen.top - 178), size=(self.game_screen.width, 22))
        self.waves.texture = self.waves.texture.get_region(0,0, self.game_screen.width, self.waves.height)
        self.game_screen.add_widget(self.game_area)
        self.game_screen.add_widget(self.waves)
        self.game_screen.add_widget(self.menu)
        
        self.manufacture_ships(3)
                
        self.fish = Fish(box=(self.game_area.x, self.game_area.y + 100, self.game_area.width, self.game_area.height - 175))
        self.fish.bind(pos=lambda instance, value: self.check_for_smthing_to_eat(value))
        self.fish.bind(calories=self.update_calories_bar)
        
        return self.welcome_screen
        
    def update_calories_bar(self, instance, value):
        self.calories_bar.value = value
        
    def check_for_smthing_to_eat(self, dt):
        to_eat = []
        for stuff in self.game_area.children:
            if stuff.collide_widget(self.fish):
                if isinstance(stuff, Food):
                    to_eat.append(stuff)
                
        for shit in to_eat:
            self.game_area.remove_widget(shit)
            self.fish.eat(shit.calories)
            print "eaten! ", self.fish.calories
            del(shit)
        
    def drop_food(self, td):
        """Periodicaly drop food from the ships"""
        
        for ship in self.ships:
            food = Food(what="bottle", lvl=self.fish.obese_lvl, x = ship.center_x + randint(-50,50), y = ship.y + randint(-5,5))
            def really_drop_food(food, td):
                 self.game_area.add_widget(food)
                 food.active = True
            Clock.schedule_once(partial(really_drop_food, food), random() * 2)
    
    def sail_ships(self, timer):
        for ship in self.ships:
            ship.sail()
            
    def manufacture_ships(self, count = 1):
        for n in range(0, count):
            ship = Ship()
            self.ships.append(ship)
        
    def drop_onto_sea(self, ship):
        try:
            if not ship:
                ship = self.ships.pop()
            self.game_area.add_widget(ship)
            ship.pos = (randint(20, Window.width - 20), ship.parent.height)
            ship.active = True
        except IndexError:
            obj.text = "No more ships left!"


class FishLifeFlesh(FishLifeBones):
    def __init__(self):
        super(FishLifeFlesh, self).__init__()
    
    def scene_intro(self, *kwargs):
        self.root.clear_widgets()
        self.root.add_widget(self.welcome_screen)
        
    def scene_gameplay(self, *kwargs):
        self.root.clear_widgets()
        self.root.add_widget(self.game_screen)
        
        for ship in self.ships:
            self.drop_onto_sea(ship)
        
        self.game_area.add_widget(self.fish)
        self.fish.active = True
        
        Clock.schedule_interval(self.drop_food, 2)
        Clock.schedule_interval(self.sail_ships, 5)
        Clock.schedule_interval(self.check_for_smthing_to_eat, 0.4)  
           
if __name__ == '__main__':
    FishLifeFlesh().run()
