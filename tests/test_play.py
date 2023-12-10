from src import settings
from src.modules.play import NovelSettings
from src.utils.utils import JsonImporter

test_play = {
    "title": "三国风云",
    "background": "三国时期的政治斗争与战争",
    "characters": [
        {
            "name": "刘备",
            "description": "汉室宗亲，宁死不屈"
        },
        {
            "name": "曹操",
            "description": "魏国权臣，权谋老手"
        },
        {
            "name": "孙权",
            "description": "东吴君主，智勇双全"
        }
    ],
    "goal": "统一中国，结束乱世",
    "total_steps": 10,
    "option_num": 3,
    "language": "中文",
    "current_step": 1,
    "play_context": "暂无",
    "user_interaction": "暂无"
}


def test_play_import():
    play = NovelSettings.load_json(test_play['title'])
    assert play.get_inputs() == test_play


def test_play_export():
    play = NovelSettings(**test_play)
    play.export()
    file_obj = settings.DATA_DIR / 'plays' / f'{play.title}.json'
    assert file_obj.exists()


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

