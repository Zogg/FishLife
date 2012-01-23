from random import randint
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.properties import BooleanProperty, OptionProperty

class Ship(Image):
    
    active = BooleanProperty(False)
    state = OptionProperty("fishing", options=["fishing", "sailing"])
    
    def __init__(self, image = "images/ship.png", horison = 200, **kwargs):
        self.source = image
        self.horison = horison # Pixels from the top of parent container
        self.size = (292, 190)
        super(Ship, self).__init__(**kwargs)
        self.register_event_type('on_start_sailing')
        self.register_event_type('on_stop_sailing')
                
        self.bind(active=lambda instance, value: Animation(y=Window.height - self.horison, t="out_back", d=1.2).start(instance))
        
    def sail(self):
        self.dispatch("on_start_sailing")
        
        # TODO: more intresting/smooth placing and transition
        new_fishing_place = randint(0, self.parent.width - 40)
        anim = Animation(center_x=new_fishing_place, t="in_out_quad", d=2)
        
        anim.bind(on_complete= lambda instance, value: self.dispatch("on_stop_sailing"))    
        anim.start(self)
        
    #    
    # Events    
    #
    
    def on_start_sailing(self):
        self.state = "sailing"
        
    def on_stop_sailing(self):
        self.state = "fishing"

