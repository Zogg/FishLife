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

from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.properties import BooleanProperty, OptionProperty, NumericProperty

class Ship(Image):
    
    active = BooleanProperty(False)
    horison = NumericProperty(0)
    state = OptionProperty("fishing", options=["fishing", "sailing"])
    
    def __init__(self, image = "images/ship.png", horison = 200, **kwargs):
        self.source = image
        self.horison = horison # Pixels from the top of parent container
        
        self.size = (292, 190)
        super(Ship, self).__init__(**kwargs)
        
        self.texture_left = self.texture.get_region(0, 0, 292, 190)
        self.texture_right = self.texture.get_region(292, 0, 292, 190)
        self.texture = choice([self.texture_left, self.texture_right])
        
        self.register_event_type('on_start_sailing')
        self.register_event_type('on_stop_sailing')
                
        self.bind(active=lambda instance, value: Animation(y=Window.height/self.horison - 25, t="out_back", d=1.2).start(instance))
        
    def sail(self):
        self.dispatch("on_start_sailing")
        
        # TODO: more intresting/smooth placing and transition
        new_fishing_place = randint(0, self.parent.width - 40)
        anim = Animation(center_x=new_fishing_place, t="in_out_quad", d=2)
        anim.bind(on_complete= lambda instance, value: self.dispatch("on_stop_sailing"))    
        self.texture = self.texture_left if new_fishing_place < self.center_x else self.texture_right
        anim.start(self)
        
    #    
    # Events    
    #
    
    def on_start_sailing(self):
        self.state = "sailing"
        
    def on_stop_sailing(self):
        self.state = "fishing"

