"""
    FishLife - a game of Zen
    Copyright (C) 2012 Rokas Aleksiunas

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from random import randint, choice
from functools import partial

from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.clock import Clock

class Food(Image):
    active = BooleanProperty(False)
    storehouse = {"cucumber": {"image":"images/cucumber.png", "calories": (5,15)},
                  "apple": {"image":"images/apple.png", "calories": (15,20)},
                  "banana": {"image":"images/banana.png", "calories": (10,35)},
                  "meat": {"image":"images/meat.png", "calories": (35,55)},
                  "bottle": {"image":"images/bottle.png", "calories": (0,60)}}

    # New obesity level unlocks new food! \o
    assorted = [["cucumber"],["apple"], ["banana"], ["meat"], ["bottle"]] 

    def __init__(self, what=None, lvl=1, image = "dialog-information.png", **kwargs):
        if lvl:
            what = choice([item for items in self.assorted[:lvl] for item in items ])
            
        source = self.storehouse[what]
        self.source = source["image"]
            
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
    animation = ObjectProperty(None, allow_none = True)
    
    storehouse = {"lightbulb": {"image":"dialog-information.png", "calories": (-40,-30)},
                  "oil_drop": {"image":"images/oil_drop.png", "calories": (-500,-500), "speed_mod": 2.5},
                  "death_fork": {"image":"images/death_fork.png", "calories": (-150,-80)},
                  "simple_fork": {"image":"images/plain_fork.png", "calories": (-50,-25)},
                  "salad_fork": {"image":"images/salad_fork.png", "calories": (25,50), "speed_mod": 1.7},
                  "simple_boot": {"image":"images/simple_boot.png", "calories": (-60,-30)},
                  "black_boot": {"image":"images/black_boot.png", "calories": (-80,-40)},
                  "mech_screw": {"image":"images/mech_screw.png", "calories": (-40,-30)},
                  "oily_mech_screw": {"image":"images/oily_mech_screw.png", "calories": (-160,-100)},
                  "candy_mech_screw": {"image":"images/candy_mech_screw.png", "calories": (50,100), "speed_mod": 1.7},
                 }
    
    # New obesity level unlocks new junk! o/
    assorted = [["mech_screw", "simple_fork"], 
                ["simple_boot"], 
                ["black_boot", "salad_fork"], 
                ["oily_mech_screw", "salad_fork"], 
                ["death_fork", "salad_fork"],
                ["candy_mech_screw", "oily_mech_screw"],
                ["oil_drop", "candy_mech_screw"],
                ["oil_drop"]] 
           
    def __init__(self, what=None, lvl=1, image="dialog-information.png", **kwargs):
        if lvl:
            what = choice([item for items in self.assorted[:lvl] for item in items ])
            
        source = self.storehouse[what]                        
        self.source = source["image"]
            
        super(Junk, self).__init__(**kwargs)
        self.size = (48, 48)
        self.calories = randint(*self.storehouse[what]["calories"])
        self.speed_mod = self.storehouse[what].get("speed_mod", 1)
        self.bind(active=self.sinking)
        self.bind(parent=lambda instance, value: instance.animation.unbind(on_complete=self.sunk) if not value else False)
        
    def sinking(self, instance, value):
        self.animation = Animation(y=33, d=6 * self.speed_mod)
        self.animation &= Animation(x=self.x + 10, t="in_out_back", d=1) + \
                Animation(x=self.x - 10, t="in_out_back", d=1) + \
                Animation(x=self.x + 10, t="in_out_back", d=1) + \
                Animation(x=self.x, t="in_out_back", d=1)
        self.animation.bind(on_complete=self.sunk)   # Because trash stay on the floor for some time 
        self.animation.start(self)
        
    def sunk(self, *args):
        Clock.schedule_once(self._remove_myself, 5)
            
    def _remove_myself(self, *args):
        try:
            self.parent.remove_widget(self)
        except:
            pass
            
class FoodScoreFeedback(Label):
    def __init__(self, **kwargs):
        score = int(kwargs.get("calories", 0))
        if score > 0:
            self.color = (0,1,0,1)
        else:
            self.color = (1,0,0,1)
        self.text = str(score)
        self.bold = True    
        # super(FoodScoreFeedback, self).__init__(**kwargs)
        super(FoodScoreFeedback, self).__init__()
        
        anim = Animation(y=self.y + 45, d=0.33)
        Clock.schedule_once(self.dissapear, 1.3)
        anim.start(self)
        
    def dissapear(self, *args):
        self.parent.remove_widget(self)
