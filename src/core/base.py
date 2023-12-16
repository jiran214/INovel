import abc
import typing
from abc import ABC
from typing import Dict

from pydantic import BaseModel

from src.core.chains import ChainFlow
from src.modules import parsers, memory
from src.modules.play import NovelSettings
from src.utils import enums
from src.utils.enums import EventLife


if typing.TYPE_CHECKING:
    from src.schemas import InteractionLike


class Event(ABC):
    share_data: Dict[enums.EventLife, InteractionLike] = {}

    def __init__(self, play: NovelSettings, flow: ChainFlow, context_window: memory.PlayContext):
        self.context_window = context_window
        self.flow = flow
        self.play = play

    def start(self, *args, **kwargs): raise NotImplementedError
    def process(self, *args, **kwargs): raise NotImplementedError
    def end(self, *args, **kwargs): raise NotImplementedError

    def cycle(self, play_inputs: dict, life: EventLife):
        # 每次循环开始召回关联剧情
        play_inputs.update(
            play_context_memory=self.context_window.play_context_memory,
            play_context_window=self.context_window.play_context_window,
        )
        life_response = getattr(self, life.value)(play_inputs)
        return life_response


class FlowNode(BaseModel):
    event: Event
    life: EventLife

    def run(self, play_inputs: dict) -> InteractionLike:
        return self.event.cycle(play_inputs, self.life)