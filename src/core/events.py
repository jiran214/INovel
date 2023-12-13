from typing import Union, Callable, Generator

from src.core.base import Event
from src.modules import parsers
from src.modules.memory import CharactorMemoryHistory
from src.modules.parsers import Result, Dialog, Action
from src.utils import enums
from src.utils.enums import EventLife

ActionCallback = Callable[[str], str]
DialogCallback = Callable[[str], Generator[str]]
InteractionLike = Union[Result, Dialog, Action, ActionCallback, DialogCallback]


class IAction:
    Result = Result
    Dialog = Dialog
    Action = Action
    ActionCallback = ActionCallback
    DialogCallback = DialogCallback


class DialogEvent(Event):
    name = enums.EventName.DIALOG

    def start(self, play_inputs: dict):
        interaction: parsers.Dialog = self.flow.dialog_chain.invoke(play_inputs)
        self.context_window.sliding_data(self.name.value, interaction.story)
        return interaction

    def process(self, play_inputs: dict):
        _input = {
            'character_name': play_inputs['character_names'][0],
            'story': play_inputs['story'],
            'scene': play_inputs['scene'],
        }
        memory = CharactorMemoryHistory(_input['character_name'])

        def dialog_interaction(chat_input: str):
            _input['input'] = chat_input
            chat_output = self.flow.charactor_chat_chain.invoke(_input)
            if not chat_output:
                # todo 自动结束对话，摘要对话内容
                # self.context_window.sliding_data(enums.EventName.dialog, f"{event.character_names}", long_memory=False)
                yield None
            yield chat_output
            # todo 添加角色对话记录
            # memory.save_context()
        return dialog_interaction


class ActionEvent(Event):
    name = enums.EventName.ACTION

    def start(self, play_inputs: dict):
        interaction: parsers.Action = self.flow.action_chain.invoke(play_inputs)
        self.context_window.sliding_data(self.name.value, interaction.story)
        self.share_data[EventLife.STARTS] = interaction
        return interaction

    def process(self):
        def action_callback(user_option: Union[int, str], is_index=True):
            if is_index:
                user_action = self.share_data[EventLife.STARTS].options.index(user_option)
            else:
                user_action = user_option
            self.context_window.sliding_data(enums.EventName.ACTION, user_action)
        return action_callback
