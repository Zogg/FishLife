from random import random, randint
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.vector import Vector
from kivy.graphics import Color, Ellipse, Line
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import BooleanProperty, StringProperty, NumericProperty

class FishLifeBones(App):
    
    scene = StringProperty("intro")
    
    def __init__(self, **kwargs):
        super(FishLifeBones, self).__init__(**kwargs)
        self.ships = []
        self.scenes = {"intro": self.scene_intro, "gameplay": self.scene_gameplay}        
        
    def build_config(self, config):
        config.setdefaults('aquarium', {"waterline": 250})
        
    def build(self):
        self.animations = {"ship": {"drop_in": Animation(y=Window.height - self.config.getint('aquarium', 'waterline'), t="out_back", d=1.2),
                                    "sail": Animation(x=Window.width)
                                   },
                           "fish": {"drop_in": Animation(y=Window.height - 400, t="out_back", d=1.2)},
                           "food": {"sinking": Animation(y=100, t="in_out_back", d=7) &
                                               Animation(x=10, t="in_out_back", d=3)
                                   }
                          }
                          
        self.welcome_screen = Widget(width=Window.width, height=Window.height)
        begin = Button(text="Feed the Fish!")        
        begin.bind(on_release=self.scenes["gameplay"])
        self.welcome_screen.add_widget(begin)
        
        
        self.game_screen = Widget(width=Window.width, height=Window.height)
        self.menu = GridLayout(cols=2, row_force_default=True, row_default_height=100, width=Window.width, height=200, pos=(0,0))
        self.menu.add_widget(Label(text="Calories stockpiled", width=100))
        self.calories = ProgressBar(max=1000, value=1000)
        self.menu.add_widget(self.calories)
        self.game_area = Image(width=Window.width, height=Window.height, source="images/bg.png")
        self.game_screen.add_widget(self.menu)
        self.game_screen.add_widget(self.game_area)
        
        self.bind(scene=self.on_scene_change)
        
        self.manufacture_ships(3)
                
        self.fish = Fish(size=(48,48))
        self.fish.bind(active=lambda instance, value: self.animations['fish']['drop_in'].start(instance))
        self.fish.bind(pos=lambda instance, value: self.check_for_smthing_to_eat(value))
        self.fish.bind(calories=self.on_calories_change)
        
        return self.welcome_screen
        
    def on_calories_change(self, instance, value):
        self.calories.value = value
        
    def on_scene_change(self, instance, value):
        self.scenes[value]()
        
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
        
        Clock.schedule_interval(self.drop_food, 1)
        Clock.schedule_interval(self.sail_ships, 5)
        Clock.schedule_interval(self.check_for_smthing_to_eat, 0.4)
        

    def check_for_smthing_to_eat(self, dt):
        to_eat = []
        for stuff in self.game_area.children:
            if stuff.collide_widget(self.fish):
                if isinstance(stuff, Food):
                    to_eat.append(stuff)
                
        for shit in to_eat:
            shit.parent.remove_widget(shit)
            self.fish.calories = self.fish.calories + shit.calories if self.fish.calories + shit.calories <= 1000 else 1000
            # Scrap food does not count into total calories
            if shit.calories > 0:
                self.fish.total_calories += shit.calories
            print "eaten! ", self.fish.calories
            del(shit)
        
    def drop_food(self, smthing):
        for ship in self.ships:
            food = Food(x = ship.x + randint(0,30), y = ship.y + randint(0,30))
            self.game_area.add_widget(food)
            anim = Animation(y=100, d=7)
            anim &= Animation(x=food.x + 10, t="in_out_back", d=2) + \
                    Animation(x=food.x - 10, t="in_out_back", d=2) + \
                    Animation(x=food.x + 10, t="in_out_back", d=2) + \
                    Animation(x=food.x, t="in_out_back", d=1)
            anim.start(food)
    
    def sail_ships(self, timer):
        for ship in self.ships:
            new_fishing_place = randint(40, ship.parent.width - 40)
            anim = Animation(x=new_fishing_place, t="in_out_quad", d=2)
            anim.start(ship)
            
    def manufacture_ships(self, count = 1):
        for n in range(0, count):
            ship = Ship()
            ship.bind(active=lambda instance, value: self.animations['ship']['drop_in'].start(instance))
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
        
class Fish(Image):
    active = BooleanProperty(False)
    alive = BooleanProperty(True)
    calories = NumericProperty(1000)
    total_calories = NumericProperty(0)
    obese_lvl = NumericProperty(1)
    lvlup_on_calories = [150, 250, 400, 570, 700, 880, 980, 1060, 1140]
    calories_consumption = 7
    
    def __init__(self, image = "images/fish.png", **kwargs):
        self.direction = Vector(0, 0)
        self.source = image
        super(Fish, self).__init__(allow_stretch=True, **kwargs)
        self.register_event_type('on_death')
        # Every living creature consumes own self
        self.bind(active=lambda instance, value: Clock.schedule_interval(instance.consume_calories, 0.5) if value else Clock.unschedule(instance.consume_calories) )
        # Too many calories make you obese
        self.bind(total_calories=self.lvlup)
    
    def consume_calories(self, *kwargs):
        self.calories -= self.calories_consumption * self.obese_lvl
        if self.calories <= 0:
            self.calories = 0
            self.dispatch("on_death")
    
    def lvlup(self, instance, value):
        if self.total_calories >= self.lvlup_on_calories[self.obese_lvl]:
            self.obese_lvl += 1
            self.size = (self.width + self.width * (1.0 / self.obese_lvl), self.height + self.height * (1.0 / self.obese_lvl))
    
    def on_death(self):
        self.alive = False
        self.active = False
        print "dead"
            
    def on_touch_move(self, touch):
        self.pos = (touch.x, touch.y)
    
class Ship(Image):
    
    active = BooleanProperty(False)
    sailing = BooleanProperty(False)
    throwing_trash = BooleanProperty(False)
    
    def __init__(self, image = "gnome-dev-media-sdmmc.png", **kwargs):
        self.source = image
        super(Ship, self).__init__(**kwargs)
        
        
    def sail(self):
        if Window.width/2 < self.x < Window.width:
            anim = Animation(x=Window.width-40)
        else:
            anim = Animation(x=40)
            
        anim.play(self)
        
    def throw_trash(self):
        pass
    
class Food(Image):
    def __init__(self, image = "dialog-information.png", **kwargs):
        self.source = image        
        super(Food, self).__init__(**kwargs)
        self.size = (48, 48)
        self.calories = randint(5, 20)
 
if __name__ == '__main__':
    FishLifeBones().run()
