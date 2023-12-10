import os
from typing import List, Optional

from langchain.memory import ConversationBufferMemory, ConversationTokenBufferMemory, FileChatMessageHistory, \
    ConversationBufferWindowMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma

from src import settings
from src.modules.brain import llm
from src.utils.utils import FileHistory


# 角色name和内容召回
# chat_retriever = None


# 保存剧情，任何内容都能召回
class PlayMemoryRetriever:
    def __init__(self, collection="novel_play"):
        self.store = Chroma(collection, llm.embeddings, persist_directory=settings.DATA_DIR)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=0,
            separators=["\n\n", "\n", "。", "！", "？", ""],
            length_function=len
        )

    def add_context(self, text: str, meta_data: Optional[dict]=None, need_spilt=True):
        if need_spilt:
            texts = self.text_splitter.split_text(text)
        else:
            texts = [text]
        metadatas = meta_data and [meta_data] * len(texts)
        self.store.add_texts(texts, metadatas)

    def search_context(self, query, k: int = 8):
        docs = self.store.similarity_search(query, k=k)
        return '\n'.join([doc.page_content for doc in docs]) or "暂无"


class CharactorChatMemory:
    charactor_memory_map = {}

    def __init__(self, charactor_name: str):
        # 保存角色对话，通过角色name召回
        self.file_path = settings.DATA_DIR / 'chat_history' / f"{charactor_name}.json"
        self.k = 6
        if not self.file_path.parent.exists():
            os.mkdir(self.file_path.parent)
        self.chat_memory: ConversationBufferWindowMemory = self.get_charactor_memory(charactor_name)

    def get_charactor_memory(self, charactor_name):
        if charactor_name not in self.charactor_memory_map:
            self.charactor_memory_map[charactor_name] = ConversationBufferWindowMemory(
                human_prefix='me',
                ai_prefix=charactor_name,
                chat_memory=FileHistory(self.file_path),
                k=self.k,
                # llm=llm.chat_model,
                # max_token_limit=2000,
            )
        return self.charactor_memory_map[charactor_name]

    def save_context(self, inputs: str, outputs: str):
        return self.chat_memory.save_context({'input': inputs}, {'output': outputs})

    @classmethod
    def load_charactor_memory(cls, charactor_name: str):
        return cls(charactor_name).chat_memory.buffer

