from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableBranch

from src import prompts
from src.modules import parsers
from src.modules.llm import chat_model
from src.modules.memory import characterMemoryHistory
from src.modules.utils import FileCallbackHandler


class ChainFlow:

    def __init__(self):
        """交互事件生成"""
        handler = FileCallbackHandler()
        # 剧情推进
        self.play_chain = (
                prompts.INovelPrompt.novel_start_prompt
                | chat_model
                | parsers.play_parser
        ).with_config(config={'callbacks': [handler]})
        # 动作选项chain
        self.action_chain = (
                prompts.INovelPrompt.action_driven_prompt
                | chat_model
                | parsers.action_parser
        ).with_config(config={'callbacks': [handler]})
        # 角色对话事件chain
        self.dialog_chain = (
                prompts.INovelPrompt.dialog_driven_prompt
                | chat_model
                | parsers.dialog_parser
        ).with_config(config={'callbacks': [handler]})
        # 结局生成chain
        self.novel_end_chain = (
            prompts.INovelPrompt.novel_end_prompt
            | chat_model
            | parsers.result_parser
        ).with_config(config={'callbacks': [handler]})
        # 角色对话chain todo 增加剧情retriever召回
        self.character_chat_chain = (
            prompts.INovelPrompt.character_chat_prompt
            | chat_model
            | StrOutputParser()
        ).with_config(config={'callbacks': [handler]})