import importlib
import os
from typing import Any, List, Dict, Union

from langchain.memory import ConversationBufferWindowMemory
from langchain.memory.chat_memory import BaseChatMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from overrides import override

from src import settings
from src.modules import llm
from src.schemas import ContextMessage
from src.utils import enums
from src.utils.utils import FileHistory, FileHistoryProxy, get_event_buffer_string


# 保存剧情，任何内容都能召回
class NovelMemoryRetriever:
    def __init__(self, namespace: str):
        # todo 单例 共享连接
        self.path = settings.DATA_DIR / namespace / 'db'
        self.collection = namespace
        self.store = self.get_or_create_vst()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=0,
            separators=["\n\n", "\n", "。", "！", "？", "，"],
            length_function=len
        )

    def get_or_create_vst(self):
        from langchain.vectorstores.qdrant import Qdrant
        from qdrant_client import QdrantClient
        from qdrant_client.http.models import VectorParams, Distance

        client = QdrantClient(path=self.path)
        collections = client._client.collections.keys()
        if not (self.collection in collections):
            client.create_collection(
                **{'collection_name': self.collection,
                   'vectors_config': VectorParams(
                       size=1536, distance=Distance.COSINE, hnsw_config=None, quantization_config=None, on_disk=True
                   )
               }
            )
        return Qdrant(client, self.collection, llm.embeddings)

    def add_context(self, context: ContextMessage, need_spilt=True):
        if need_spilt:
            texts = self.text_splitter.split_text(context.content)
        else:
            texts = [context.content]
        metadata = context.metadata
        metadatas = [metadata] * len(texts)
        self.store.add_texts(texts, metadatas)

    def search_context(self, query, k: int = 8, as_str=True) -> Union[str, List[ContextMessage]]:
        docs = self.store.similarity_search(query, k=k)
        contexts = ContextMessage.from_docs(docs)
        if as_str:
            return '\n'.join([context.format_line() for context in contexts])
        else:
            return contexts


# 保存角色对话
class CharactorMemoryHistory:
    charactor_memory_map = {}

    def __init__(self, namespace: str, charactor_name: str):
        # 保存角色对话，通过角色name召回
        self.file_path = settings.DATA_DIR / namespace / 'chat_history' / f"{charactor_name}.jsonl"
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
    def history(self):
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
        if not self.chat_memory.messages:
            return "暂无"
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

    @override(check_signature=False)
    def save_context(self, messages: List[ContextMessage]) -> List[ContextMessage]:
        # Prune buffer if it exceeds max token limit
        self.chat_memory.messages.extend(messages)
        buffer = self.chat_memory.messages
        curr_buffer_length = self.llm.get_num_tokens(get_event_buffer_string(buffer))
        pruned_memory = []
        if curr_buffer_length > self.max_token_limit:
            while curr_buffer_length > self.max_token_limit:
                pruned_memory.append(buffer.pop(0))
                curr_buffer_length = self.llm.get_num_tokens(get_event_buffer_string(buffer))
        if pruned_memory:
            self.chat_memory.add_messages(pruned_memory)
        return pruned_memory


# 保存剧情历史
class PlayContext:
    def __init__(self, namespace: str, max_token_limit: int):
        self.file_path = settings.DATA_DIR / namespace / "play_history.jsonl"
        self.retriever = NovelMemoryRetriever(namespace)
        # self.k = k
        if not self.file_path.parent.exists():
            os.mkdir(self.file_path.parent)
        self.memory: TokenBufferMemory = TokenBufferMemory(
            chat_memory=FileHistoryProxy(self.file_path),
            llm=llm.chat_model,
            max_token_limit=max_token_limit,
        )

    def sliding_data(self, event_name: enums.EventName, content):
        message = ContextMessage(event=event_name.value, content=content)
        pruned_memory = self.memory.save_context([message])
        for message in pruned_memory:
            # 聊天记录不存入
            if event_name != enums.EventName.DIALOG:
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
