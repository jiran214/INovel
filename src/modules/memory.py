import os
from typing import Optional, Any, List, Dict

from langchain.memory import ConversationBufferWindowMemory
from langchain.memory.chat_memory import BaseChatMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import get_buffer_string, BaseMessage, ChatMessage
from overrides import override
from typing_extensions import Literal

from src import settings
from src.modules import llm
from src.utils.utils import FileHistory, FileHistoryProxy, get_event_buffer_string


class ContextMessage(BaseMessage):
    event: str
    """The speaker / role of the Message."""
    type: Literal["event"] = "event"

    @property
    def metadata(self):
        self.additional_kwargs.update(event=self.event)
        return self.additional_kwargs


# 保存剧情，任何内容都能召回
class NovelMemoryRetriever:
    def __init__(self, collection="novel_play"):
        # todo 单例 共享连接
        self.store = Chroma(collection, llm.embeddings, persist_directory=settings.DATA_DIR)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=0,
            separators=["\n\n", "\n", "。", "！", "？", "，"],
            length_function=len
        )

    def add_context(self, context: ContextMessage, need_spilt=True):
        if need_spilt:
            texts = self.text_splitter.split_text(context.content)
        else:
            texts = [context.content]
        metadata = context.metadata
        metadatas = [metadata] * len(texts)
        self.store.add_texts(texts, metadatas)

    def search_context(self, query, k: int = 8):
        docs = self.store.similarity_search(query, k=k)
        return '\n'.join([doc.page_content for doc in docs])


class CharactorMemoryHistory:
    charactor_memory_map = {}

    def __init__(self, namespace: str, charactor_name: str):
        # 保存角色对话，通过角色name召回
        self.file_path = settings.DATA_DIR / namespace / 'chat_history' / f"{charactor_name}.json"
        self.namespace = namespace
        self.charactor_name = charactor_name
        self.k = 6
        if not self.file_path.parent.exists():
            os.makedirs(self.file_path.parent, exist_ok=True)
        self.chat_memory: ConversationBufferWindowMemory = self.get_charactor_memory()

    def get_charactor_memory(self):
        key = (self.namespace, self.charactor_name)
        if key not in self.charactor_memory_map:
            self.charactor_memory_map[key] = ConversationBufferWindowMemory(
                human_prefix='主角',
                ai_prefix=self.charactor_name,
                chat_memory=FileHistory(self.file_path),
                k=self.k,
                # llm=llm.chat_model,
                # max_token_limit=2000,
            )
        return self.charactor_memory_map[key]

    def save_context(self, inputs: str, outputs: str):
        return self.chat_memory.save_context({'input': inputs}, {'output': outputs})

    @property
    def buffer(self):
        return self.chat_memory.buffer


class TokenBufferMemory(BaseChatMemory):
    """token"""
    chat_memory: FileHistoryProxy
    llm: BaseLanguageModel
    memory_key: str = "history"
    max_token_limit: int = 2000

    @property
    def buffer(self) -> Any:
        """String buffer of memory."""
        return self.buffer_as_messages if self.return_messages else self.buffer_as_str

    @property
    def buffer_as_str(self) -> str:
        """Exposes the buffer as a string in case return_messages is False."""
        return get_event_buffer_string(self.chat_memory.messages)

    @property
    def buffer_as_messages(self) -> List[ContextMessage]:
        """Exposes the buffer as a list of messages in case return_messages is True."""
        return self.chat_memory.messages

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.

        :meta private:
        """
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Return history buffer."""
        return {self.memory_key: self.buffer}

    @override
    def save_context(self, messages: List[ContextMessage]) -> List[ContextMessage]:
        # Prune buffer if it exceeds max token limit
        self.chat_memory.messages.extend(messages)
        buffer = self.chat_memory.messages
        curr_buffer_length = self.llm.get_num_tokens_from_messages(buffer)
        pruned_memory = []
        if curr_buffer_length > self.max_token_limit:
            while curr_buffer_length > self.max_token_limit:
                pruned_memory.append(buffer.pop(0))
                curr_buffer_length = self.llm.get_num_tokens_from_messages(buffer)
        if pruned_memory:
            self.chat_memory.add_messages(pruned_memory)
        return pruned_memory


class PlayContext:
    def __init__(self, namespace: str):
        # 保存角色对话，通过角色name召回
        self.file_path = settings.DATA_DIR / namespace / 'memory' / "play_history.jsonl"
        self.retriever = NovelMemoryRetriever()
        self.k = 12
        if not self.file_path.parent.exists():
            os.mkdir(self.file_path.parent)
        self.memory: TokenBufferMemory = TokenBufferMemory(
            chat_memory=FileHistoryProxy(self.file_path),
            k=self.k,
            llm=llm.chat_model,
            max_token_limit=2000,
        )

    def sliding_data(self, event_name, content):
        message = ContextMessage(event=event_name, content=content)
        pruned_memory = self.memory.save_context([message])
        for message in pruned_memory:
            # 聊天记录不存入
            if isinstance(message, ContextMessage):
                self.retriever.add_context(message)

    @property
    def play_context_window(self):
        return self.memory.buffer_as_str

    @property
    def play_context_memory(self):
        """用来召回关联剧情"""
        messages = self.memory.buffer_as_messages
        if not messages:
            return '暂无'
        standard_query = get_event_buffer_string(messages[-1:])
        context = self.retriever.search_context(standard_query) or "暂无"
        return context
