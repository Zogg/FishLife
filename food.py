from random import randint, choice
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.properties import BooleanProperty

class Food(Image):
    active = BooleanProperty(False)
    storehouse = {"lightbulb": "dialog-information.png",
                  "banana": "images/banana.png",
                  "cucumber": "images/cucumber.png",
                  "apple": "images/apple.png",
                  "meat": "images/meat.png",
                  "bottle": "images/bottle.png"}
    
    # New obesity level unlocks new food! \o
    assorted = [["cucumber"],["apple"], ["banana", "bottle"], ["meat"]] 
                 
    def __init__(self, what=None, lvl=None, image = "dialog-information.png", **kwargs):
        if lvl:
            what = choice([item for items in self.assorted[:lvl] for item in items ])
            
        self.source = self.storehouse.get(what, "dialog-information.png")
        
        super(Food, self).__init__(**kwargs)
        self.size = (48, 48)
        self.calories = randint(5, 20)
        self.bind(active=self.sinking)
        
    def sinking(self, instance, value):
        anim = Animation(y=100, d=7)
        anim &= Animation(x=self.x + 10, t="in_out_back", d=2) + \
                Animation(x=self.x - 10, t="in_out_back", d=2) + \
                Animation(x=self.x + 10, t="in_out_back", d=2) + \
                Animation(x=self.x, t="in_out_back", d=1)
        anim.start(self)
        
class Junk(Image):
    pass
