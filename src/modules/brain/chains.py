import os
from operator import itemgetter

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import get_buffer_string
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from src import prompts
from src.modules.brain import parsers
from src.modules.brain.llm import chat_model
from src.modules.memory import CharactorChatHistory


class ChainSettings:

    def __init__(self, dialog_trigger_steps: int):
        """

        Args:
            dialog_trigger_steps: 每n step触发一次对话，默认触发action
        """
        self.dialog_trigger_steps = dialog_trigger_steps
        # 交互：生成动作选项chain
        self.action_chain = (
            prompts.INovelPrompt.action_driven_prompt
            | chat_model
            | parsers.action_parser
        )
        # 交互：生成角色对话事件chain
        self.dialog_chain = (
            prompts.INovelPrompt.dialog_driven_prompt
            | chat_model
            | parsers.dialog_parser
        )
        # 结局生成chain
        self.novel_end_chain = (
            prompts.INovelPrompt.novel_end_prompt
            | chat_model
            | StrOutputParser()
        )
        # 角色对话chain todo 增加剧情retriever召回
        self.charactor_chat_chain = (
            RunnablePassthrough.assign(
                history=itemgetter('charactor_name') | RunnableLambda(CharactorChatHistory.load_charactor_memory)
            )
            | prompts.INovelPrompt.charactor_chat_prompt
            | chat_model
            | StrOutputParser()
        )