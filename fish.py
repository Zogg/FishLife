from math import sin, cos, radians

from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.properties import BooleanProperty, NumericProperty

class DirectionalImage():
    pass

class Fish(Scatter):
    active = BooleanProperty(False)
    alive = BooleanProperty(True)
    calories = NumericProperty(1000)
    total_calories = NumericProperty(0)
    obese_lvl = NumericProperty(1)
    lvlup_on_calories = [150, 250, 400, 570, 700, 880, 980, 1060, 1140]
    calories_consumption = 7
    box = (0, 0, 100, 100)
    
    def __init__(self, image = "images/fish.png", box = (), **kwargs):
        self.direction = Vector(-1, 0)
        self.angle = 1
        self.speed = 0
        
        self.size = (48,48)
        self.box = box
        self.center = (Window.width / 2, Window.height)
        self.source = image
        self.image = Image(source=image, allow_stretch=True, size=self.size)
        
        # Can't be arsed to 'rotate' texture 'properly', this is so frikin more simple
        self.texture_left = self.image.texture.get_region(0, 0, 192, 188)
        self.texture_right = self.image.texture.get_region(207, 0, 192, 188)
        self.image.texture = self.texture_left
        
        self.target_pos = self.center
        
        super(Fish, self).__init__(**kwargs)
        self.add_widget(self.image)
        
        self.register_event_type('on_death')
        
        # Every living creature consumes own self
        self.bind(active=lambda instance, value: Clock.schedule_interval(instance.consume_calories, 0.5) if value else Clock.unschedule(instance.consume_calories))
        # Dynamic entry
        self.bind(active=lambda instance, value: Animation(y=Window.height - 400, t="out_back", d=1.2).start(instance))
        # Too many calories make you obese
        self.bind(total_calories=self.lvlup)
    
    def eat(self, calories):
        self.calories = self.calories + calories if self.calories + calories <= 1000 else 1000
        # Scrap food does not count into total calories
        if calories > 0:
            self.total_calories += calories
                
    def consume_calories(self, *kwargs):
        self.calories -= self.calories_consumption * self.obese_lvl
        if self.calories <= 0:
            self.calories = 0
            self.dispatch("on_death")
    
    def lvlup(self, instance, value):
        try:
            #TODO: will there be lvl limit?
            if self.total_calories >= self.lvlup_on_calories[self.obese_lvl]:
                self.obese_lvl += 1
                self.image.size = (self.image.width + self.image.width * (1.0 / self.obese_lvl), self.image.height + self.image.height * (1.0 / self.obese_lvl))
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
        Clock.schedule_interval(self.swim, 0.1)
        
    def on_touch_move(self, touch):
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
        Clock.unschedule(self.swim)
        
        self.speed = Vector((0,0)).distance((touch.dsx, touch.dsy)) * 5000
        
        angle = self.direction.angle((touch.dsx, touch.dsy))
        if angle < 0:
            angle = 360 + angle
        angle = 270 - angle

        anim = Animation(center=(self.target_pos[0] + sin(radians(angle)) * self.speed,self.target_pos[1] - cos(radians(angle)) * self.speed), t="out_cubic", d=0.6)
        anim.start(self)
        
