from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableBranch

from src import prompts
from src.modules import parsers
from src.modules.llm import chat_model
from src.modules.memory import CharactorMemoryHistory


class ChainFlow:

    def __init__(
            self
    ):
        """
        event:              user:
            action_chain -> charactor_chat_chain ->
        ->                                         novel_end_chain -> loop
            dialog_chain ->                      ->

        Args:
            dialog_trigger_steps: 每n step触发一次对话，默认触发action
        """
        # self.dialog_trigger_steps = dialog_trigger_steps

        """交互事件生成"""
        # 动作选项chain
        self.action_chain = (
                prompts.INovelPrompt.action_driven_prompt
                | chat_model
                | parsers.action_parser
        )
        # 角色对话事件chain
        self.dialog_chain = (
                prompts.INovelPrompt.dialog_driven_prompt
                | chat_model
                | parsers.dialog_parser
        )
        # self.event_branch_chain = RunnableBranch(
        #     (
        #         lambda x: x["current_step"] % self.dialog_trigger_steps == 0,
        #         action_chain
        #     ),
        #     dialog_chain,
        # )

        # 结局生成chain
        self.novel_end_chain = (
            prompts.INovelPrompt.novel_end_prompt
            | chat_model
            | StrOutputParser()
        )
        # 角色对话chain todo 增加剧情retriever召回
        self.charactor_chat_chain = (
            RunnablePassthrough.assign(
                history=itemgetter('charactor_name') | RunnableLambda(CharactorMemoryHistory.load_charactor_memory)
            )
            | prompts.INovelPrompt.charactor_chat_prompt
            | chat_model
            | StrOutputParser()
        )