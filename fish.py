from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.properties import BooleanProperty, NumericProperty

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
        self.size = (48,48)
        
        super(Fish, self).__init__(allow_stretch=True, **kwargs)
        
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
            self.size = (self.width + self.width * (1.0 / self.obese_lvl), self.height + self.height * (1.0 / self.obese_lvl))
    
    def on_death(self):
        self.alive = False
        self.active = False
        print "dead"
            
    def on_touch_move(self, touch):
        self.pos = (touch.x, touch.y)
    

