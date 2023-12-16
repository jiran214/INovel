from typing import Union

import src.schemas
from src.core.base import Event
from src.modules.memory import CharactorMemoryHistory
from src.schemas import Dialog, Action, Result, PlayParagraph
from src.utils import enums


class IAction:
    Result = Result
    Dialog = Dialog
    Action = Action
    PlayParagraph = PlayParagraph


class Common(Event):

    def start(self, play_inputs: dict):
        interaction: src.schemas.PlayParagraph = self.flow.play_chain.invoke(play_inputs)
        self.context_window.sliding_data(enums.EventName.PLAY, interaction.story)
        # 开始阶段的剧情推进作为本章节的主要剧情
        self.play.scene = interaction.scene
        return interaction

    def end(self, play_inputs: dict):
        interaction: src.schemas.Result = self.flow.novel_end_chain.invoke(play_inputs)
        self.context_window.sliding_data(enums.EventName.RESULT, interaction.story)
        return interaction


class DialogEvent(Event):

    def process(self, play_inputs: dict):
        interaction: src.schemas.Dialog = self.flow.dialog_chain.invoke(play_inputs)
        self.play.relate_characters = interaction.relate_characters
        self.context_window.sliding_data(enums.EventName.DIALOG, interaction.story)
        _input = {
            'character_name': play_inputs['character_names'][0],
            'story': play_inputs['story'],
            'scene': play_inputs['scene'],
        }
        memory = CharactorMemoryHistory(_input['character_name'])

        def dialog_interaction(chat_input: str):
            _input['input'] = chat_input
            _input['history'] = memory.history
            chat_output = self.flow.charactor_chat_chain.invoke(_input)
            if not chat_output:
                # todo 自动结束对话，摘要对话内容
                # self.context_window.sliding_data(enums.EventName.dialog, f"{event.character_names}", long_memory=False)
                yield None
            yield chat_output
            # todo 添加角色对话记录
            # memory.save_context()

        interaction.generator_func = dialog_interaction
        return interaction


class ActionEvent(Event):

    def process(self, play_inputs):
        interaction: src.schemas.Action = self.flow.action_chain.invoke(play_inputs)
        self.context_window.sliding_data(enums.EventName.ACTION, interaction.story)

        def action_callback(user_option: Union[int, str], is_index=True):
            if is_index:
                user_action = interaction.options.index(user_option)
            else:
                user_action = user_option
            self.context_window.sliding_data(enums.EventName.ACTION, user_action)
        interaction.generator_func = action_callback
        return interaction
