from typing import Optional, Union, List, Generator, Dict, Callable
from src.core import events
from src.core.base import FlowNode
from src.core.chains import ChainFlow
from src.core.events import InteractionLike, IAction
from src.modules.parsers import (
    Dialog,
    Action,
    Result,
)
from src.modules.memory import CharactorMemoryHistory, NovelMemoryRetriever, PlayContext
from src.modules.play import NovelSettings
from src.utils import enums
from src.utils.enums import EventName, EventLife
from src.utils.utils import event_choice


class Engine:
    def __init__(
            self,
            play_namespace: str,
            event_trigger_dict: Dict[EventName: Union[float, int]],
            total_paragraph: int = 6
    ):
        self.play = NovelSettings.load_json(play_namespace)
        self.context = PlayContext(play_namespace)
        self.flow = ChainFlow()

        self.trigger_save_chapter = 1
        self.current_paragraph = None
        self.total_paragraph = total_paragraph
        self.event_trigger_dict = event_trigger_dict

        _inputs = [self.play, self.flow, self.context]
        self.event_map = {
            EventName.ACTION: events.ActionEvent(*_inputs),
            EventName.DIALOG: events.DialogEvent(*_inputs)
        }
        self.event_flow = self.generate_event_flow()
        self.chapter_iter = self._next_paragraph()

    def generate_event_flow(self) -> List[FlowNode]:
        flow = []
        cur_chapter = 1
        while cur_chapter <= self.play.total_chapters:
            flow.append(FlowNode(event=events.Common, life=EventLife.STARTS))
            for _ in range(self.total_paragraph - 2):
                event_name = event_choice(self.event_trigger_dict)
                flow.append(FlowNode(event=self.event_map[event_name], life=EventLife.PROCESS))
            flow.append(FlowNode(event=events.Common, life=EventLife.ENDS))
        return flow

    def _next_paragraph(self) -> Generator[InteractionLike]:
        for index, node in enumerate(self.event_flow):
            # 自动保存进度
            if self.play.current_chapter % self.trigger_save_chapter == 0:
                self.play.export_json()
            interaction = node.run(self.play.get_inputs())
            self.play.current_paragraph += 1
            if node.life is EventLife.ENDS:
                self.play.current_chapter += 1
                self.play.current_paragraph = 0
            yield interaction
        self.play.reset()
        StopIteration('大结局')

    def next_paragraph(self) -> InteractionLike:
        return next(self.chapter_iter)

