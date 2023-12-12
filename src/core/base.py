import abc
from abc import ABC

from src.core.chains import ChainFlow
from src.modules import parsers, memory
from src.modules.play import NovelSettings
from src.utils import enums
from src.utils.enums import EventLife


class Event(ABC):
    name = None
    share_data = {}

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
        self.context_window.sliding_data(enums.EventName.result, result.story)
        return result

    def cycle(self, play_inputs: dict, life: EventLife):
        play_inputs.update(
            play_context_memory=self.play.play_context_memory,
            play_context_window=self.play.play_context_window,
        )
        life_response = getattr(self, life.value)(play_inputs)
        if life is EventLife.starts:
            # 每个回合开始，场景和关联角色不变
            self.play.relate_characters = life_response.relate_characters
            self.play.scene = life_response.scene


class DialogEvent(Event):
    name = enums.EventName.dialog

    def start(self, play_inputs: dict):
        event: parsers.Dialog = self.flow.dialog_chain.invoke(play_inputs)
        self.context_window.sliding_data(self.name.value, event.story)
        self.share_data[EventLife.starts] = event
        return event

    def process(self, user_dialog: str):
        event = self.share_data[EventLife.starts]
        _input = {
            'character_name': event.character_names,
            'story': event.story,
            'scene': event.scene,
        }

        def dialog_event(chat_input: str):
            _input['input'] = chat_input
            chat_output = self.flow.charactor_chat_chain.invoke(_input)
            if not chat_output:
                yield None
                # todo 自动结束对话，摘要对话内容
                # self.context_window.sliding_data(enums.EventName.dialog, f"{event.character_names}", long_memory=False)
            yield chat_output
        return dialog_event


class ActionEvent(Event):
    name = enums.EventName.action

    def start(self, play_inputs: dict):
        event: parsers.Action = self.flow.action_chain.invoke(play_inputs)
        self.context_window.sliding_data(self.name.value, event.story)
        return event

    def process(self, user_action: str):
        self.context_window.sliding_data(enums.EventName.action, user_action)
