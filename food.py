from random import randint, choice
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.properties import BooleanProperty
from kivy.clock import Clock

class Food(Image):
    active = BooleanProperty(False)
    storehouse = {"lightbulb": "dialog-information.png",
                  "cucumber": {"image":"images/cucumber.png", "calories": (5,15)},
                  "apple": {"image":"images/apple.png", "calories": (15,20)},
                  "banana": {"image":"images/banana.png", "calories": (5,35)},
                  "meat": {"image":"images/meat.png", "calories": (35,45)},
                  "bottle": {"image":"images/bottle.png", "calories": (0,40)}}
    
    # New obesity level unlocks new food! \o
    assorted = [["cucumber"],["apple"], ["banana", "bottle"], ["meat"]] 
                 
    def __init__(self, what=None, lvl=None, image = "dialog-information.png", **kwargs):
        if lvl:
            what = choice([item for items in self.assorted[:lvl] for item in items ])
            
        source = self.storehouse.get(what, "dialog-information.png")
        try:
            self.source = source["image"]
        except:
            self.source = source
            
        super(Food, self).__init__(**kwargs)
        self.size = (48, 48)
        self.calories = randint(*self.storehouse[what]["calories"])
        self.bind(active=self.sinking)
        
    def sinking(self, instance, value):
        anim = Animation(y=33, d=9)
        anim &= Animation(x=self.x + 10, t="in_out_back", d=2.25) + \
                Animation(x=self.x - 10, t="in_out_back", d=2.25) + \
                Animation(x=self.x + 10, t="in_out_back", d=2.25) + \
                Animation(x=self.x, t="in_out_back", d=2.25)
        anim.start(self)
        
class Junk(Image):
    active = BooleanProperty(False)
    storehouse = {"lightbulb": "dialog-information.png"}
    
    # New obesity level unlocks new junk! o/
    assorted = [["lightbulb"]] 
           
    def __init__(self, what=None, lvl=None, image="dialog-information.png", **kwargs):
        if lvl:
            what = choice([item for items in self.assorted[:lvl] for item in items ])
            
        self.source = self.storehouse.get(what, "dialog-information.png")
        
        super(Junk, self).__init__(**kwargs)
        self.size = (48, 48)
        self.calories = randint(-10, 10)
        self.bind(active=self.sinking)
        
    def sinking(self, instance, value):
        anim = Animation(y=33, d=6)
        anim &= Animation(x=self.x + 10, t="in_out_back", d=1) + \
                Animation(x=self.x - 10, t="in_out_back", d=1) + \
                Animation(x=self.x + 10, t="in_out_back", d=1) + \
                Animation(x=self.x, t="in_out_back", d=1)
        #anim.bind(on_complete=self.sunk)    
        anim.start(self)
        
    def sunk(self, instance, value):
        self.parent.remove_widget(self)
        
class FoodScoreFeedback(Label):
    def __init__(self, **kwargs):
        score = int(kwargs.get("calories", 0))
        if score > 0:
            self.color = (0,1,0,1)
        else:
            self.color = (1,0,0,1)
        self.text = str(score)
        self.bold = True    
        super(FoodScoreFeedback, self).__init__(**kwargs)
        
        anim = Animation(y=self.y + 45, d=0.33)
        Clock.schedule_once(self.dissapear, 1.3)
        anim.start(self)
        
    def dissapear(self, *args):
        self.parent.remove_widget(self)
