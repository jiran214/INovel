import pathlib

from langchain import chains
from langchain.globals import set_debug

from src.modules.brain.chains import ChainSettings
from src.modules.brain.parsers import Dialog, Action
from src.modules.play import NovelSettings
from src.utils.utils import JsonImporter

chain_settings = ChainSettings(0)
# set_debug(True)
play = NovelSettings(**JsonImporter(data_dir=pathlib.Path(__file__).parent).load('test_play.json'))


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
    chains.ConversationChain
