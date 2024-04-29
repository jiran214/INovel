#!/usr/bin/env python
# -*- coding: utf-8 -*-
from langchain.agents.types import AGENT_TYPE

from src.core import events
from src.core.chains import ChainFlow
from src.modules.memory import PlayContext, characterMemoryHistory
from src.modules.play import NovelSettings
from src.schemas import ContextMessage, DialogChat
from src.utils.enums import EventName
from src.utils.utils import JsonImporter


play = NovelSettings.load_json('test')
flow = ChainFlow()
context = PlayContext('test', 2000)


class TestDialogEvent:
    def test_process(self):
        event = events.DialogEvent(play, flow, context)
        play.play_context_window = ContextMessage(event='剧情', content='刘备死了').format_line()
        i = event.process(play.get_inputs())
        assert i.story
        assert i.character
        assert i.generator_func
        for msg in ('你好啊', '你叫什么名字', '拜拜'):
            res: DialogChat = i.generator_func(msg)
            print(res.msg)
            assert res.msg
            assert res.stop == (msg == '拜拜')
        m = characterMemoryHistory('test', i.character)
        history = m.history
        for msg in ('你好啊', '你叫什么名字', '拜拜'):
            assert msg in history


class TestActionEvent:
    def test_process(self):
        event = events.ActionEvent(play, flow, context)
        _inputs = play.get_inputs()
        i = event.process(_inputs)
        # assert i.relate_characters
        assert i.story
        assert len(i.options) > 1
        i.generator_func(0)
        assert i.options[0] in context.play_context_window


class TestCommon:
    def test_start(self):
        event = events.Common(play, flow, context)
        _inputs = play.get_inputs()
        print(_inputs)
        i = event.start(_inputs)
        print(i)
        assert i.story
        assert i.scene

    def test_end(self):
        event = events.Common(play, flow, context)
        _inputs = play.get_inputs()
        print(_inputs)
        i = event.end(_inputs)
        print(i)
        assert i.story