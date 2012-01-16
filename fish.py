from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.properties import BooleanProperty, NumericProperty

class Fish(Scatter):
    active = BooleanProperty(False)
    alive = BooleanProperty(True)
    calories = NumericProperty(1000)
    total_calories = NumericProperty(0)
    obese_lvl = NumericProperty(1)
    lvlup_on_calories = [150, 250, 400, 570, 700, 880, 980, 1060, 1140]
    calories_consumption = 7
    
    def __init__(self, image = "images/fish.png", **kwargs):
        self.direction = Vector(-1, -1)
        self.speed = 0
        
        self.size = (48,48)
        self.source = image
        self.image = Image(source=image, allow_stretch=True, size=self.size)
        
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
        if self.total_calories >= self.lvlup_on_calories[self.obese_lvl]:
            self.obese_lvl += 1
            self.image.size = (self.image.width + self.image.width * (1.0 / self.obese_lvl), self.image.height + self.image.height * (1.0 / self.obese_lvl))
            self.size = self.image.size
    
    def on_death(self):
        self.alive = False
        self.active = False
        print "dead"
            
    def on_touch_move(self, touch):
        self.center = (touch.x, touch.y)
        #self.direction = (touch.dsx, touch.dsy)
        #self.rotation = self.direction.angle((touch.dsx, touch.dsy))
        angle = self.direction.angle((touch.dsx, touch.dsy))
        self.speed += Vector((0,0)).distance(touch.dsx, touch.dsy)
        if angle < 0:
            angle = 180 + angle
        anim = Animation(rotation=angle, d=0.1)
        anim.start(self)
        print touch.dsx
        #self.rotation = angle
    

