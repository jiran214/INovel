from typing import List

from langchain_core.messages import BaseMessage
from pydantic.v1 import BaseModel, Field
from typing_extensions import Literal


class ContextMessage(BaseMessage):
    event: str
    """The speaker / role of the Message."""
    type: Literal["event"] = "event"

    @property
    def metadata(self):
        self.additional_kwargs.update(event=self.event)
        return self.additional_kwargs


class Interaction(BaseModel):
    story: str = Field(description='之后的剧情发展')


class PlayParagraph(Interaction):
    scene: str = Field(description='当前剧情的场景')


class Dialog(Interaction):
    relate_characters: List[str] = Field(description='关联角色名称')


class Action(Interaction):
    relate_characters: List[str] = Field(description='关联角色名称')
    options: List[str] = Field(description='为玩家生成，决定故事的发展')


class Result(Interaction):
    pass
