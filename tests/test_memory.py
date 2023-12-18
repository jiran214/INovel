import os

from langchain_core.documents import Document

from src.modules.memory import CharactorMemoryHistory, NovelMemoryRetriever, PlayContext, TokenBufferMemory
from src.schemas import ContextMessage
from src.utils import enums


class TestPlayMemoryRetriever:
    pass


class TestCharactorMemoryHistory:
    def test_get_charactor_memory(self):
        memory1 = CharactorMemoryHistory('namespace', 'test')
        assert ('namespace', 'test') in memory1.charactor_memory_map
        memory2 = CharactorMemoryHistory('namespace', 'test')
        memory3 = CharactorMemoryHistory('namespace', 'test1')
        assert ('namespace', 'test') in memory1.charactor_memory_map
        assert id(memory1.chat_memory) == id(memory2.chat_memory)
        assert id(memory1.chat_memory) != id(memory3.chat_memory)
        assert memory1.file_path.exists()
        assert memory3.file_path.exists()

        os.remove(memory1.file_path)
        os.remove(memory3.file_path)

    def test_save_context(self):
        memory1 = CharactorMemoryHistory('namespace', 'test')

        for _ in range(memory1.k + 2):
            memory1.save_context('test_input', 'test_output')
        context = memory1.history
        assert 'test_input' in context and 'test_output' in context
        os.remove(memory1.file_path)

    def test_buffer_window(self):
        memory1 = CharactorMemoryHistory('namespace', 'test')
        memory1.chat_memory.clear()
        for index in range(memory1.k + 2):
            memory1.save_context(f'test_input{index}', f'test_output{index}')
        assert len(memory1.chat_memory.chat_memory.messages) == (memory1.k + 2) * 2
        assert len(memory1.chat_memory.buffer_as_messages) == memory1.k * 2
        os.remove(memory1.file_path)


class TestNovelMemoryRetriever:
    def test_add_context(self):
        NovelMemoryRetriever('test').store.client.delete_collection('test')
        vst = NovelMemoryRetriever('test')
        count1 = vst.store.client.count(vst.collection)
        contexts = [
            ContextMessage(event='event1', content='开心'),
            ContextMessage(event='event1', content='高兴'),
            ContextMessage(event='event1', content='难过')
        ]
        for context in contexts:
            vst.add_context(context)
        count2 = vst.store.client.count(vst.collection)
        assert count2.count == count1.count + len(contexts)
        assert vst.store.client.count('test').count >= 3
        del vst

    def test_search_context(self):
        vst = NovelMemoryRetriever('test')
        contexts = vst.search_context('开心', 9, order_by='similarity')
        print(contexts)
        assert contexts.index('开心') < contexts.index('高兴') < contexts.index('难过')
        contexts = vst.search_context('开心', 2, as_str=False)[0]
        assert isinstance(contexts, ContextMessage)
        del vst

    def test_sort(self):
        vst = NovelMemoryRetriever('test')
        contexts = vst.search_context('难过', 9, order_by='time')
        print(contexts)
        assert contexts.index('开心') < contexts.index('高兴') < contexts.index('难过')
        contexts = vst.search_context('开心', 2, as_str=False, order_by='time')[0]
        assert isinstance(contexts, ContextMessage)
        del vst


class TestPlayContext:

    def test_init(self):
        context = PlayContext('test', 2000)
        assert context.file_path.exists()

    def test_sliding_data_and_play_context_window(self):
        NovelMemoryRetriever('test').store.client.delete_collection('test')

        context = PlayContext('test', 50)
        count1 = self.get_count(context)
        assert count1 == 0
        assert context.play_context_window == "暂无"

        context.sliding_data(enums.EventName.PLAY, '哈哈')
        count2 = self.get_count(context)
        assert count1 == count2
        assert context.play_context_window == f"[剧情]-哈哈"

        context.sliding_data(enums.EventName.PLAY, '哈哈' * 10)
        count3 = self.get_count(context)
        assert count3 == count2
        assert context.play_context_window == f"[剧情]-哈哈\n[剧情]-{'哈哈' * 10}"

        context.sliding_data(enums.EventName.PLAY, '哈哈' * 100)
        count4 = self.get_count(context)
        assert count4 == 3
        assert context.play_context_window == "暂无"

    def test_sliding_data_and_play_context_memory(self):
        NovelMemoryRetriever('test').store.client.delete_collection('test')

        context = PlayContext('test', 10)

        count1 = self.get_count(context)
        assert count1 == 0
        assert context.play_context_memory == "暂无"

        context.sliding_data(enums.EventName.PLAY, '哈哈')
        assert context.play_context_memory == "暂无"

        context.sliding_data(enums.EventName.PLAY, '哈哈' * 400)
        messages = context.memory.chat_memory.messages
        assert messages == []
        assert self.get_count(context) == 2
        # assert len(context.retriever.search_context(query='haha', as_str=False)) == 2
        play = context.play_context_memory
        assert play != "暂无"
        assert context.memory.chat_memory.last_message
        assert play == f"[剧情]-哈哈\n[剧情]-{'哈哈' * 400}"

    @staticmethod
    def get_count(context):
        return context.retriever.store.client.count(context.retriever.collection).count