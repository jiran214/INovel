import functools
from typing import List, Union

from langchain.output_parsers import PydanticOutputParser
from pydantic.v1 import BaseModel, Field

from src.modules.memory import CharactorChatMemory
from src.utils import enums


class AIInteraction(BaseModel):
    story: str = Field(description='之后的剧情发展')
    scene: str = Field(description='当前剧情的场景')
    event: enums.Event


class Dialog(AIInteraction):
    character_name: str = Field(description='选择的人物名称')
    event: enums.Event = enums.Event.dialog


class Action(AIInteraction):
    options: List[str] = Field(description='为玩家生成，决定故事的发展')
    event: enums.Event = enums.Event.action


class UserInteraction(BaseModel):
    interaction_in: Union[Dialog, Action]
    interaction_out: str

    def prompt(self):
        if isinstance(self.interaction_in, Action):
            return f"选择剧情选项:{self.interaction_out}"
        elif isinstance(self.interaction_in, Dialog):
            return f"和角色<{self.interaction_in.character_name}>对话:\n{self.interaction_out}"


dialog_parser = PydanticOutputParser(pydantic_object=Dialog)
action_parser = PydanticOutputParser(pydantic_object=Action)