import os
from enum import Enum, auto

from common.config import config

APP_PATH = os.path.dirname(os.path.dirname(__file__))

RESOURCES_PATH = os.path.join(APP_PATH, 'resources')

MENUS = config['menus']


class PeriodEnum(Enum):
    F1 = auto()
    F5 = auto()
    F15 = auto()
    F30 = auto()
    D = auto()
