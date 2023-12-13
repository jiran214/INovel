from enum import Enum


class Event(Enum):
    action = 'action'
    dialog = 'dialog'


class EventName(Enum):
    DIALOG = '对话'
    PLAY = '剧情'
    ACTION = '行动'
    RESULT = '结果'


class EventLife(Enum):
    STARTS = 'start'
    PROCESS = 'process'
    ENDS = 'end'


