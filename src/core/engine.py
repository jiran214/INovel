from typing import Optional, Union

from src.core.chains import ChainFlow
from src.modules.parsers import (
    UserInteraction,
    Dialog,
    Action, Result, AIInteraction
)
from src.modules.memory import CharactorMemoryHistory, NovelMemoryRetriever
from src.modules.play import NovelSettings
from src.utils.enums import Event


class Engine:
    def __init__(self, play: NovelSettings, brain: ChainFlow):
        self.play = play
        self.brain = brain
        self.play_retriever: NovelMemoryRetriever = NovelMemoryRetriever(play.title)
        self.generated_end_step = 1

    def _next_step(self):
        # 互动结局
        if self.generated_end_step < self.play.current_step:
            result = self.brain.novel_end_chain.invoke(self.play.get_inputs())
            self.play.result = result
            self.play_retriever.add_context(result)
            return
        # 互动事件
        if self.play.current_step <= self.play.total_steps:
            user_interaction = self.brain.event_branch_chain.invoke(self.play.get_inputs())
            self.play.current_step += 1
            # 保存剧情到retriever
            self.play_retriever.add_context(user_interaction.story)
            return user_interaction
        else:
            StopIteration('大结局')

    def next_step(self, user_interaction: Optional[UserInteraction] = None) -> Union[Result, Dialog, Action]:
        if user_interaction:
            # 从retriever查询用户交互相关剧情，作为下次play_context
            play_context = self.play_retriever.search_context(user_interaction.prompt)
            # 更新Play的user_interaction
            self.play.update_play(
                play_context=play_context,
                user_interaction=user_interaction.prompt
            )
        return self._next_step()


class ConsoleUI:

    def __init__(self, engine: Engine):
        self.engine = engine

    def dialog_display(self, interaction: Dialog):
        _input = {
            'character_name': interaction.character_name,
            'story': interaction.story,
            'scene': interaction.scene,
        }
        memory = CharactorMemoryHistory(interaction.character_name)
        while 1:
            # 渲染对话
            _input['input'] = input('[你]:')
            str_outputs = self.engine.brain.charactor_chat_chain.invoke(_input)
            print(f'[{memory.chat_memory.ai_prefix}]:', str_outputs)
            # 对话中止条件
            if not str_outputs:
                break
            memory.save_context(_input['input'], str_outputs)
        return UserInteraction(
            interaction_in=interaction,
            interaction_out=memory.chat_memory.buffer_as_str
        )

    def action_display(self, interaction: Action):
        # 渲染动作
        print(f"选项:\n" + '\n'.join([f"{index+1}. option" for index, option in enumerate(interaction.options)]))
        user_input = input('你的选择:')
        return UserInteraction(
            interaction_in=interaction,
            interaction_out=interaction.options[int(user_input)-1]
        )

    def result_display(self, result: str):
        print('结局:')

    def loop(self):
        user_interaction = None
        while 1:
            try:
                ai_interaction = self.engine.next_step(user_interaction)
            except StopIteration:
                break
            if isinstance(ai_interaction, Dialog):
                user_interaction = self.dialog_display(ai_interaction)
            elif isinstance(ai_interaction, Action):
                user_interaction = self.action_display(ai_interaction)
            elif isinstance(ai_interaction, Result):
                self.result_display(ai_interaction)


if __name__ == '__main__':
    engine = Engine(
        play=NovelSettings(),
        brain=ChainFlow(dialog_trigger_steps=3)
    )
    ui = ConsoleUI(engine)
    ui.loop()
