import json
import pathlib

from src import settings
from src.modules.play import NovelSettings
from src.utils.utils import JsonImporter

test_play = JsonImporter(data_dir=pathlib.Path(__file__).parent).load('test_play.json')


def test_play_export():
    play = NovelSettings(**test_play)
    play.export()
    file_obj = settings.DATA_DIR / 'plays' / f'{play.title}.json'
    assert file_obj.exists()


def test_play_import():
    play = NovelSettings.load_json(test_play['title'])
    assert play.get_inputs() == test_play


def test_delete():
    JsonImporter().delete(f'{test_play["title"]}.json')
    file_obj = settings.DATA_DIR / 'plays' / f'{test_play["title"]}.json'
    assert not file_obj.exists()


def test_play_init():
    play = NovelSettings(**test_play)
    assert play.get_inputs() == test_play
    play.update_play('测试play_context', '测试user_interaction')
    assert play.play_context == '测试play_context'
    assert play.user_interaction == '测试user_interaction'

