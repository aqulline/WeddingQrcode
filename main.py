from kivy.base import EventLoop
from kivy.properties import NumericProperty, StringProperty, DictProperty, ListProperty, BooleanProperty
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy import utils
from kivymd.toast import toast
from kivymd.uix.card import MDCard
from kivymd.uix.list import IRightBodyTouch, TwoLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox

from database import FireBase as FB

Window.keyboard_anim_args = {"d": .2, "t": "linear"}
Window.softinput_mode = "below_target"
Clock.max_iteration = 250

