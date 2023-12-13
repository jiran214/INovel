import abc
import typing
from abc import ABC
from typing import Dict

from src.core.chains import ChainFlow
from src.modules import parsers, memory
from src.modules.play import NovelSettings
from src.utils import enums
from src.utils.enums import EventLife


if typing.TYPE_CHECKING:
    from src.core.events import InteractionLike


class Event(ABC):
    name = None
    share_data: Dict[enums.EventLife, InteractionLike] = {}

    def __init__(self, play: NovelSettings, flow: ChainFlow, context_window: memory.PlayContext):
        self.context_window = context_window
        self.flow = flow
        self.play = play

    @abc.abstractmethod
    def start(self, *args, **kwargs): ...

    @abc.abstractmethod
    def process(self, *args, **kwargs): ...

    def end(self, play_inputs: dict):
        result: parsers.Result = self.flow.novel_end_chain.invoke(play_inputs)
        self.context_window.sliding_data(enums.EventName.RESULT, result.story)
        return result

    def cycle(self, play_inputs: dict, life: EventLife):
        play_inputs.update(
            play_context_memory=self.play.play_context_memory,
            play_context_window=self.play.play_context_window,
        )
        life_response = getattr(self, life.value)(play_inputs)
        if life is EventLife.STARTS:
            # 每个回合开始，场景和关联角色不变
            self.play.relate_characters = life_response.relate_characters
            self.play.scene = life_response.scene