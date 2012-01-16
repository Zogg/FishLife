from random import randint
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.properties import BooleanProperty

class Food(Image):
    active = BooleanProperty(False)

    def __init__(self, image = "dialog-information.png", **kwargs):
        self.source = image        
        super(Food, self).__init__(**kwargs)
        self.size = (48, 48)
        self.calories = randint(5, 20)
        self.bind(active=self.sinking)
        
    def sinking(self, instance, value):
        anim = Animation(y=100, d=7)
        anim &= Animation(x=food.x + 10, t="in_out_back", d=2) + \
                Animation(x=food.x - 10, t="in_out_back", d=2) + \
                Animation(x=food.x + 10, t="in_out_back", d=2) + \
                Animation(x=food.x, t="in_out_back", d=1)
        anim.start(food)
        
class Junk(Image):
    pass
