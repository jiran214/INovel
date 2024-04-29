from typing import Union

from src import schemas
from src.core.base import Event
from src.modules.memory import characterMemoryHistory
from src.schemas import Dialog, Action, Result, PlayParagraph, DialogChat
from src.utils import enums


class IAction:
    Result = Result
    Dialog = Dialog
    Action = Action
    PlayParagraph = PlayParagraph


class Common(Event):

    def start(self, play_inputs: dict) -> PlayParagraph:
        interaction: schemas.PlayParagraph = self.flow.play_chain.invoke(play_inputs)
        self.context.sliding_data(enums.EventName.PLAY, interaction.story)
        # 开始阶段的剧情推进作为本章节的主要剧情
        self.play.scene = interaction.scene
        return interaction

    def end(self, play_inputs: dict) -> Result:
        interaction: schemas.Result = self.flow.novel_end_chain.invoke(play_inputs)
        self.context.sliding_data(enums.EventName.RESULT, interaction.story)
        return interaction


class DialogEvent(Event):

    def process(self, play_inputs: dict):
        interaction: Dialog = self.flow.dialog_chain.invoke(play_inputs)
        print('interaction', interaction)
        assert interaction.character
        # self.play.relate_characters = interaction.character
        self.context.sliding_data(enums.EventName.PLAY, interaction.story)
        _input = {
            'character': interaction.character,
            **play_inputs
        }
        memory = characterMemoryHistory(self.play.namespace, _input['character'])

        def dialog_interaction(chat_input: str) -> DialogChat:
            _input['input'] = chat_input
            _input['history'] = memory.history
            chat_output = self.flow.character_chat_chain.invoke(_input)
            print('chat_output', chat_output)
            stop = False
            if '/stop' in chat_output:
                chat_output = chat_output.replace('/stop', '')
                # 自动结束对话，摘要对话内容
                stop = True
                return DialogChat(chat_output, stop)
            memory.save_context(chat_input, chat_output)
            return DialogChat(chat_output, stop)

        interaction.generator_func = dialog_interaction
        return interaction


class ActionEvent(Event):

    def process(self, play_inputs) -> Action:
        interaction: schemas.Action = self.flow.action_chain.invoke(play_inputs)
        self.context.sliding_data(enums.EventName.PLAY, interaction.story)

        def action_callback(user_option: Union[int, str], is_index=True):
            if is_index:
                user_action = interaction.options[user_option]
            else:
                user_action = user_option
            self.context.sliding_data(enums.EventName.ACTION, user_action)
        interaction.generator_func = action_callback
        return interaction
