from enum import Enum


class Event(Enum):
    action = 'action'
    dialog = 'dialog'


class EventName(Enum):
    dialog = '对话'
    play = '剧情'
    action = '行动'
    result = '结果'


class EventLife(Enum):
    starts = 'start'
    process = 'process'
    ends = 'end'
