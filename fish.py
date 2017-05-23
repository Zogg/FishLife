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

from __future__ import print_function

from math import sin, cos, radians

from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.properties import BooleanProperty, NumericProperty, ListProperty, BoundedNumericProperty

from food import Junk

class Fish(Scatter):
    active = BooleanProperty(False)
    alive = BooleanProperty(True)
    navigating = BooleanProperty(False)
    box = ListProperty([])
    
    calories = BoundedNumericProperty(1000, min=0, max=1000)
    total_calories = NumericProperty(0)
    junk_swallowed = NumericProperty(0)
    
    # Max level 8
    obese_lvl = BoundedNumericProperty(1, min=0, max=8)
    
    # Immutable properties
    #
    # How many calories will be consumed per second each level
    calories_consumption = [7, 16, 20, 29, 32, 35, 42, 50]
    # Eat that much calories (in total) and you level up!
    lvlup_on_calories = [150, 350, 550, 900, 1400, 2100, 3000, 4100]
    # Relative size increase upon each lvlup
    size_increment = [1, 1.2, 1.2, 1.2, 1.4, 1.1, 1.1, 1.1]
    # Every level has a rank!
    rank = ["a fry", "a cat", "a car", "a whale", "a candy store", "an oil tanker", "the Iceland", "the Pacific Ocean itself!", 'the "MAFIAA"']

    def __init__(self, image = "images/fish.png", box = [0, 0, 100, 100], **kwargs):
        self.direction = Vector(-1, 0)
        self.angle = 1
        
        self.size = (48,48)
        self.box = box
        self.center = (Window.width / 2, Window.height)
        self.image = Image(source=image, allow_stretch=True, size=self.size)
        
        # Can't be arsed to 'rotate' texture 'properly', this is so frikin more simple
        self.texture_left = self.image.texture.get_region(0, 0, 194, 192)
        self.texture_right = self.image.texture.get_region(205, 0, 194, 192)
        self.image.texture = self.texture_left
        
        self.target_pos = self.center
        
        super(Fish, self).__init__(**kwargs)
        self.add_widget(self.image)
        
        self.register_event_type('on_death')
        
        # Every living creature consumes own self
        self.bind(active=lambda instance, value: Clock.schedule_interval(instance.consume_calories, 0.5) if value else Clock.unschedule(instance.consume_calories))
        # Dynamic entry
        self.bind(active=lambda instance, value: Animation(y=Window.height - 400, t="out_back", d=1.2).start(instance) if value else True)
        # Too many calories make you obese
        self.bind(total_calories=self.lvlup)
    
    def eat(self, stuff):
        try:
            self.calories = self.calories + stuff.calories if self.calories + stuff.calories <= 1000 else 1000
        except:
            self.calories = 0
            self.dispatch("on_death")
            
        # Scrap food does not count into total calories
        if stuff.calories > 0:
            self.total_calories += stuff.calories
        
        if isinstance(stuff, Junk):
            self.junk_swallowed += 1
                
    def consume_calories(self, *args):
        try:
            self.calories -= self.calories_consumption[self.obese_lvl-1]
        except:
            self.calories = 0
            self.dispatch("on_death")
    
    def lvlup(self, instance, value):
        try:
            #TODO: will there be lvl limit?
            if self.total_calories >= self.lvlup_on_calories[self.obese_lvl]:
                self.obese_lvl += 1
                print(self.obese_lvl)
                self.image.size = (self.image.width * self.size_increment[self.obese_lvl-1], self.image.height * self.size_increment[self.obese_lvl-1])
                self.size = self.image.size
        except:
            pass
            
    def swim(self, dt):
        if self.angle > 0:
            self.image.texture = self.texture_left
        else:
            self.image.texture = self.texture_right
  
        anim = Animation(center=self.target_pos, d=0.1)
        anim.start(self)
        
    def on_death(self):
        self.alive = False
        self.active = False
            
    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return False
            
        if self.active and self.alive:
            Clock.schedule_interval(self.swim, 0.1)  
            self.navigating = True      
        
    def on_touch_move(self, touch):
        if not self.alive:
            return False
            
        # Facing to the left will be positive, to right - negative deg values
        angle = self.direction.angle((touch.dsx, touch.dsy))
        self.angle = cos(radians(angle)) * 180
        
        # TODO: solve facing glitch problem with Clock, which sets facing_change cooldown timer for half a sec
        
        # Bounding box
        x = touch.x
        if touch.x >= self.box[2]:
            x = self.box[2]
        elif touch.x <= self.box[0]:
            x = self.box[0]
            
        y = touch.y
        if touch.y >= self.box[3]:
            y = self.box[3]
        elif touch.y <= self.box[1]:
            y = self.box[1]
            
        self.target_pos = (x, y)
        
    def on_touch_up(self, touch):
        if not self.navigating:
            return False
        
        self.navigating = False
        
        Clock.unschedule(self.swim)
        
        speed = Vector((0,0)).distance((touch.dsx, touch.dsy)) * 5000
        
        angle = self.direction.angle((touch.dsx, touch.dsy))
        if angle < 0:
            angle = 360 + angle
        angle = 270 - angle

        anim = Animation(center=(self.target_pos[0] + sin(radians(angle)) * speed,self.target_pos[1] - cos(radians(angle)) * speed), t="out_cubic", d=0.6)
        anim.start(self)
        
