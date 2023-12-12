import os

from src.modules.memory import CharactorChatMemory, NovelMemoryRetriever


class TestPlayMemoryRetriever:
    pass


class TestCharactorChatMemory:
    def test_get_charactor_memory(self):
        memory1 = CharactorChatMemory('test')
        assert 'test' in memory1.charactor_memory_map
        memory2 = CharactorChatMemory('test')
        memory3 = CharactorChatMemory('test1')
        assert 'test1' in memory1.charactor_memory_map
        assert id(memory1.chat_memory) == id(memory2.chat_memory)
        assert id(memory1.chat_memory) != id(memory3.chat_memory)

        assert memory1.file_path.exists()
        assert memory3.file_path.exists()

        os.remove(memory1.file_path)
        os.remove(memory3.file_path)

    def test_save_context(self):
        memory1 = CharactorChatMemory('test')

        for _ in range(memory1.k + 2):
            memory1.save_context('test_input', 'test_output')

        context = CharactorChatMemory.load_charactor_memory('test')
        assert 'test_input' in context and 'test_output' in context
        os.remove(memory1.file_path)

    def test_buffer_window(self):

        memory1 = CharactorChatMemory('test')
        for index in range(memory1.k + 2):
            memory1.save_context(f'test_input{index}', f'test_output{index}')
        assert len(memory1.chat_memory.chat_memory.messages) == (memory1.k + 2) * 2
        assert len(memory1.chat_memory.buffer_as_messages) == memory1.k * 2
        os.remove(memory1.file_path)
