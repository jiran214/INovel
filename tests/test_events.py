import pathlib

from langchain import chains

from src.core.chains import ChainFlow
from src.schemas import Dialog, Action
from src.modules.play import NovelSettings
from src.utils.utils import JsonImporter

chain_settings = ChainFlow()
play = NovelSettings(**JsonImporter('test').load())


def test_action_chain():
    res = chain_settings.action_chain.invoke(play.get_inputs())
    print('\n', res)
    assert isinstance(res, Action)


def test_dialog_chain():
    res = chain_settings.dialog_chain.invoke(play.get_inputs())
    print('\n', res)
    assert isinstance(res, Dialog)


def test_novel_end_chain():
    res = chain_settings.novel_end_chain.invoke(play.get_inputs())
    print('\n', res)
    assert res


def test_charactor_chat_chain():
    _input = {
        'charactor_name': '孙策',
        'story': '孙权死了',
        'scene': '皇宫',
        'input': '孙权最近可好',
        'history': ''
    }
    res = chain_settings.charactor_chat_chain.invoke(_input)
    print('\n', res)
    assert res