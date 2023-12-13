import os

from src.modules.memory import CharactorMemoryHistory, NovelMemoryRetriever, TokenBufferMemory, PlayContext
from src.schemas import ContextMessage


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
        context = memory1.buffer
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
        vst = NovelMemoryRetriever('test')
        contexts = [
            ContextMessage(event='event1', content='开心'),
            ContextMessage(event='event1', content='高兴'),
            ContextMessage(event='event1', content='难过')
        ]
        for context in contexts:
            vst.add_context(context)
        assert vst.store.client.count('test').count >= 3

    def test_search_context(self):
        vst = NovelMemoryRetriever('test')
        contexts = vst.search_context('开心', 9)
        print(contexts)
        assert contexts.index('开心') < contexts.index('高兴') < contexts.index('难过')
