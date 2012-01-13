from random import random, randint
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import BooleanProperty, StringProperty

class MyPaintWidget(Widget):

    def on_touch_down(self, touch):
        userdata = touch.ud
        userdata['color'] = c = (random(), 1, 1)
        with self.canvas:
            Color(*c, mode='hsv')
            d = 30
            Ellipse(pos=(touch.x - d/2, touch.y - d/2), size=(d, d))
            userdata['line'] = Line(points=(touch.x, touch.y))

    def on_touch_move(self, touch):
        touch.ud['line'].points += [touch.x, touch.y]


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
        self.menu = Widget(width=Window.width, height=200, pos=(0,0))
        self.menu.add_widget(Label(text="Calories stockpiled", pos_hint={'top':0.5, 'right': 0.3}))
        self.menu.add_widget(ProgressBar(max=1000, pos_hint={'top':0.5, 'right': 0.5}))
        self.game_area = Widget(width=Window.width, height=Window.height)
        self.game_screen.add_widget(self.menu)
        self.game_screen.add_widget(self.game_area)
        
        self.bind(scene=self.on_scene_change)
        
        self.manufacture_ships(3)
                
        self.fish = Fish(size=(48,48))
        self.fish.bind(active=lambda instance, value: self.animations['fish']['drop_in'].start(instance))
        self.fish.bind(pos=self.check_for_collisions)
        
        return self.welcome_screen
    
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
        Clock.schedule_interval(self.sail_ships, 8)

    def check_for_collisions(self, instance, value):
        to_eat = []
        for stuff in instance.parent.children:
            if stuff.collide_widget(instance):
                if isinstance(stuff, Food):
                    to_eat.append(stuff)
                
        for shit in to_eat:
            shit.parent.remove_widget(shit)
            print "eaten! ", str(id(shit))
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
    
    def __init__(self, image = "preferences-desktop-accessibility.png", **kwargs):
        self.source = image
        super(Fish, self).__init__(**kwargs)
        
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
        self.calories = 30
 
if __name__ == '__main__':
    FishLifeBones().run()
