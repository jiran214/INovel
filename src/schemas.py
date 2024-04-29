import collections
import time
from typing import List, Callable, Optional, Generator, Union, Tuple

from langchain_core.messages import BaseMessage
from pydantic.v1 import BaseModel, Field
from typing_extensions import Literal

ActionCallback = Callable[[Union[int, str], Optional[bool]], None]
DialogChat = collections.namedtuple('DialogChat', ['msg', 'stop'])
DialogCallback = Callable[[str], Callable[[str], DialogChat]]


class ContextMessage(BaseMessage):
    event: str
    """The speaker / role of the Message."""
    type: Literal["event"] = "event"

    @classmethod
    def from_docs(cls, docs):
        return [cls.from_doc(doc) for doc in docs]

    @classmethod
    def from_doc(cls, doc):
        return cls(event=doc.metadata.get('event'), content=doc.page_content, additional_kwargs=doc.metadata)

    @property
    def metadata(self):
        self.additional_kwargs.update(event=self.event, created=time.time())
        return self.additional_kwargs

    def format_line(self):
        return f"[{self.event}]-{self.content}"


class Interaction(BaseModel):
    story: str = Field(description='小说后续的剧情发展故事')


class PlayParagraph(Interaction):
    scene: str = Field(description='当前剧情的场景')


class Dialog(Interaction):
    character: str = Field(description='角色名字:决定玩家和哪个角色对话')
    generator_func: Optional[DialogCallback] = Field(default=None, exclude_in_schema=True)


class Action(Interaction):
    options: List[str] = Field(description='为玩家生成行动选项，决定故事的发展')
    generator_func: Optional[ActionCallback] = Field(default=None, exclude_in_schema=True)


class Result(Interaction):
    pass


InteractionLike = Union[Result, Dialog, Action, ActionCallback, DialogCallback]
