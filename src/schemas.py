from typing import List, Callable, Optional, Generator, Union

from langchain_core.messages import BaseMessage
from pydantic.v1 import BaseModel, Field
from typing_extensions import Literal

ActionCallback = Callable[[Union[int, str], bool], None]
DialogCallback = Callable[[str], Generator[str, None, None]]


class ContextMessage(BaseMessage):
    event: str
    """The speaker / role of the Message."""
    type: Literal["event"] = "event"

    @classmethod
    def from_docs(cls, docs):
        return [cls.from_doc(doc) for doc in docs]

    @classmethod
    def from_doc(cls, doc):
        return cls(event=doc.metadata.get('event'), content=doc.page_content)

    @property
    def metadata(self):
        self.additional_kwargs.update(event=self.event)
        return self.additional_kwargs

    def format_line(self):
        return f"[{self.event}]-{self.content}"


class Interaction(BaseModel):
    story: str = Field(description='之后的剧情发展')


class PlayParagraph(Interaction):
    scene: str = Field(description='当前剧情的场景')


class Dialog(Interaction):
    relate_characters: List[str] = Field(description='关联角色名称')
    generator_func: Optional[DialogCallback] = Field(default=None, exclude_in_schema=True)


class Action(Interaction):
    relate_characters: List[str] = Field(description='关联角色名称')
    options: List[str] = Field(description='为玩家生成，决定故事的发展')
    generator_func: Optional[ActionCallback] = Field(default=None, exclude_in_schema=True)


class Result(Interaction):
    pass


InteractionLike = Union[Result, Dialog, Action, ActionCallback, DialogCallback]
