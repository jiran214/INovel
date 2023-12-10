from typing import Optional, Union

from src.modules.brain.chains import ChainSettings
from src.modules.brain.parsers import (
    UserInteraction,
    Dialog,
    Action, AIInteraction
)
from src.modules.memory import CharactorChatMemory, PlayMemoryRetriever
from src.modules.play import NovelSettings
from src.utils.enums import Event


class Engine:
    def __init__(self, play: NovelSettings,  brain: ChainSettings):
        self.play = play
        self.brain = brain
        self.play_retriever: PlayMemoryRetriever = PlayMemoryRetriever(play.title)

    def _next_step(self):
        if self.play.current_step < self.play.total_steps:
            if self.play.current_step % self.brain.dialog_trigger_steps == 0:
                # 触发对话
                user_interaction = self.brain.dialog_chain.invoke(self.play.get_inputs())
            else:
                # 触发动作选项
                user_interaction = self.brain.action_chain.invoke(self.play.get_inputs())
            # 保存剧情到retriever
            self.play.current_step += 1
            return user_interaction
        elif self.play.current_step < self.play.total_steps:
            self.play.current_step += 1
            return self.brain.novel_end_chain.invoke(self.play.get_inputs())
        else:
            StopIteration('大结局')

    def _save_context(self, user_interaction: UserInteraction):
        # 从retriever查询用户交互相关剧情，作为下次play_context
        play_context = self.play_retriever.search_context(user_interaction.prompt)
        # 更新Play的user_interaction
        self.play.update_play(play_context=play_context, user_interaction=user_interaction.prompt)
        # 用户交互处理后保存到retriever
        self.play_retriever.add_context(user_interaction.interaction_in.story)

    def next_step(self, user_interaction: Optional[UserInteraction] = None) -> Union[Dialog, Action]:
        if user_interaction: self._save_context(user_interaction)
        return self._next_step()


class ConsoleUI:

    def __init__(self, engine: Engine):
        self.engine = engine

    def dialog_display(self, interaction: Dialog):
        _input = {'character_name': interaction.character_name}
        memory = CharactorChatMemory(interaction.character_name)
        while 1:
            # 渲染对话
            _input['input'] = input('对话:')
            str_outputs = self.engine.brain.charactor_chat_chain.invoke(_input)
            print(str_outputs)
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

    def loop(self):
        user_interaction = None
        while 1:
            try:
                ai_interaction = self.engine.next_step(user_interaction)
            except StopIteration:
                break
            if ai_interaction.event is Event.dialog:
                user_interaction = self.dialog_display(ai_interaction)
            elif ai_interaction.event is Event.action:
                user_interaction = self.action_display(ai_interaction)


if __name__ == '__main__':
    engine = Engine(
        play=NovelSettings(),
        brain=ChainSettings(dialog_trigger_steps=3)
    )
    ui = ConsoleUI(engine)
    ui.loop()
