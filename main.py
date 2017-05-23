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

from random import random, randint
from functools import partial
from datetime import datetime

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import Color
from kivy.graphics.vertex_instructions import *
from kivy.properties import BooleanProperty, StringProperty, NumericProperty, ListProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from kivy.lang import Builder
from kivy.logger import Logger

from food import Food, Junk, FoodScoreFeedback
from fish import Fish
from ship import Ship


class FishLifeIntro(Image):
    help_on = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(FishLifeIntro, self).__init__(source="images/welcome.png", **kwargs)
        self.help_btn.bind(on_press=self.toggle_help)
        self.defaults = {"help_btn": self.help_btn.center, "go_btn": self.go_btn.center}
        
    def toggle_help(self, *largs):
        self.help_on = not self.help_on
        self.source = "images/howto.png" if self.help_on else "images/welcome.png"
        
        if self.help_on:
            self.help_btn.center = (180, 130)
            self.go_btn.center = (630, 130)
            self.help_btn.text = "Back"
        else:
            # Easiest way to reset widget position?
            parent = self.help_btn.parent
            parent.remove_widget(self.help_btn)
            parent.remove_widget(self.go_btn)
            parent.add_widget(self.help_btn)
            parent.add_widget(self.go_btn)
            self.help_btn.text = "HowToPlay?"
        
class FishLifeScore(Popup):
    def __init__(self):
        super(FishLifeScore, self).__init__()
        self.pos = (Window.width/2 - self.width/2, Window.height/2 - self.height/2)
        self.box_layout.pos = self.pos
        self.box_layout.size = self.size

class FishLifeGame(Widget):

    ships = ListProperty([])
    fish = ObjectProperty(None)
    
    start_time = ObjectProperty(None)
    
    def __init__(self, *args, **kwargs):
        self.size = (Window.width, Window.height)

        super(FishLifeGame, self).__init__(*args, **kwargs)
        
        self.victory_screen = FishLifeScore()
        
        self.manufacture_ships(3)
       
        self.fish = Fish(box=[self.game_area.x, self.game_area.y + 65, self.game_area.width, self.game_area.height - 175])
        self.fish.bind(pos=lambda instance, value: self.check_for_smthing_to_eat(value))
        self.fish.bind(calories=self.update_calories_bar)  
        self.fish.bind(on_death=self.the_end) 

    def play(self, *largs):
        for ship in self.ships:
            self.drop_ship_onto_sea(ship)
    
        self.game_area.add_widget(self.fish, index=1)
        self.fish.active = True
        
        # Tick tock, the food is dropped \o ooops
        Clock.schedule_interval(self.drop_food, 2)
        # SAIL AWAY!
        Clock.schedule_interval(self.sail_ships, 5)
        # Lets try and not overheat the CPU ;)
        Clock.schedule_interval(self.check_for_smthing_to_eat, 0.4)
        
        self.start_time = datetime.now() 
        
    def pause(self):
        Clock.unschedule(self.drop_food)
        Clock.unschedule(self.sail_ships)
        Clock.unschedule(self.check_for_smthing_to_eat) 
        
    def the_end(self, instance):
        self.pause()
        self.victory_screen.calories_score.text = str(self.fish.total_calories)
        self.victory_screen.junk_score.text = str(self.fish.junk_swallowed)
        self.victory_screen.total_score.text = "On %s a fish was caught, size of %s, which well fed the people of the world for %s days straight!" % (datetime.now().strftime("%B %d, %Y"), self.fish.rank[self.fish.obese_lvl - 1], (datetime.now() - self.start_time).seconds )
        self.victory_screen.open()

    def manufacture_ships(self, count = 1):
        """Next batch coming for Somalia"""
        
        for n in range(0, count):
            ship = Ship(horison=self.horison)
            self.ships.append(ship)
            
        # *cough*workaround*cough* bind on first ship
        self.ships[0].bind(on_start_sailing=lambda instance: Clock.schedule_interval(self.drop_junk, 0.4))
        self.ships[0].bind(on_stop_sailing=lambda instance: Clock.unschedule(self.drop_junk))      
        
    def drop_ship_onto_sea(self, ship):
        """Randomly throw away the dead meat! BUahaha"""
        try:
            if not ship:
                ship = self.ships.pop()
            self.game_area.add_widget(ship)

            ship.center_x = randint(0, Window.width - ship.width/4)
            ship.y = self.game_area.height
            ship.active = True
        except IndexError:
            Logger.debug("No ships left in dock.")   
            
    def check_for_smthing_to_eat(self, dt):
        """Collision detection: leFish vs Food'n'Junk"""
        to_eat = []
        for stuff in self.game_area.children:
            if stuff.collide_widget(self.fish):
                if isinstance(stuff, Food) or isinstance(stuff, Junk):
                    to_eat.append(stuff)
                
        for shit in to_eat:
            self.game_area.remove_widget(shit)
            self.game_area.add_widget(FoodScoreFeedback(calories=shit.calories, center=shit.center))
            
            self.fish.eat(shit)
        
    def drop_food(self, td):
        """Periodicaly drop food from the ships"""
        
        for ship in self.ships:
            food = Food(what="bottle", lvl=self.fish.obese_lvl, x = ship.center_x + randint(-50,50), y = ship.y + randint(-5,5))
            def really_drop_food(food, td):
                 self.game_area.add_widget(food)
                 food.active = True
            Clock.schedule_once(partial(really_drop_food, food), random() * 2)
    
    def drop_junk(self, *args):
        """Feels sooooOOo goood yeaaahhhh"""
        
        for ship in self.ships:
            junk = Junk(lvl=self.fish.obese_lvl, x = ship.center_x + randint(-50,50), y = ship.y + randint(-5,5))
            self.game_area.add_widget(junk)
            junk.active = True
        
    def sail_ships(self, timer):
        """I wonder, wheres the captain?"""
        for ship in self.ships:
            ship.sail()        

    def update_calories_bar(self, instance, new_value):
        self.calories_bar.value = new_value        


class FishLifeBones(App):
    def __init__(self, *args, **kwargs):
        super(FishLifeBones, self).__init__(*args, **kwargs)

    def build_config(self, config):
        """Leaving this here for future reference"""
        
        config.setdefaults('aquarium', {"waterline":200})
        #config.setdefaults('graphics', {"width":1280, "height": 726})
        
    def build(self):
        Builder.load_file("intro.kv")
        self.intro = FishLifeIntro()
        self.intro.go_btn.bind(on_release=self._transition_outof_intro)
        return self.intro
        
    def begin_game(self, *largs, **kwargs):
        Builder.load_file("main.kv")
        self.root = self.fishlife = FishLifeGame()
        self.fishlife.victory_screen.restart_btn.bind(on_press=self.restart_game)
        
        try:
            Window.remove_widget(self.intro)
        except:
            pass
            
        Window.add_widget(self.root)
        
        # Fade in
        Window.remove_widget(self.fader)
        Window.add_widget(self.fader)
        anim = Animation(alpha = 0.0, d=0.8)
        anim.bind(on_complete=lambda instance, value: Window.remove_widget(self.fader))
        anim.start(self.fader)
        
        # Timing game start with fade in
        if not kwargs.get("restart", False):
            Clock.schedule_once(self.root.play, 0.85)
        else:
            self.root.play()
              
    def restart_game(self, *args):
        self.fishlife.victory_screen.restart_btn.unbind(on_press=self.restart_game)
        Window.remove_widget(self.fishlife)
        
        # Because widgets later on disappear. Why? Dunno, maybe garbage
        # collector does it's work?
        # Thus, unload and then load the rules again, and now widgets do not
        # disappear.
        Builder.unload_file("main.kv")
        self.begin_game(restart=True)
        
    def _transition_outof_intro(self, *args):
        # Fade out
        self.fader = ScreenFader(size=Window.size)
        Window.add_widget(self.fader)
        anim = Animation(alpha = 1.0, d=0.6)
        anim.bind(on_complete=self.begin_game)
        anim.start(self.fader)

class ScreenFader(Widget):

    alpha = NumericProperty(0.0)
    
    def __init__(self, alpha=0, **kwargs):
        super(ScreenFader, self).__init__(**kwargs)
        self.bind(alpha=self.on_alpha)
        self.alpha = alpha
            
    def on_alpha(self, instance, value):
        # Probably there is more efficient approach. Tried other ways, 
        # didnt work. Stuck with this.
        self.canvas.clear()
        with self.canvas:
            Color(0,0,0, value)
            Rectangle(pos=self.pos, size=self.size)
            
            
if __name__ == '__main__':
    FishLifeBones().run()
    
