from typing import Optional, Union, List, Generator
from src.core import events
from src.core.chains import ChainFlow
from src.core.events import InteractionLike, IAction
from src.modules.parsers import (
    Dialog,
    Action,
    Result,
)
from src.modules.memory import CharactorMemoryHistory, NovelMemoryRetriever, PlayContext
from src.modules.play import NovelSettings
from src.utils.enums import EventName, EventLife


class Engine:
    def __init__(
            self,
            play_namespace: str,
            trigger_dialog_step: int = 3,

    ):
        self.play = NovelSettings.load_json(play_namespace)
        self.context = PlayContext(play_namespace)
        self.flow = ChainFlow()
        self.generated_end_step = 1
        self.trigger_save_step = trigger_dialog_step

        _inputs = [self.play, self.flow, self.context]
        self.event_map = {
            EventName.ACTION: events.ActionEvent(*_inputs),
            EventName.DIALOG: events.DialogEvent(*_inputs)
        }
        self.event_flow = self.generate_event_flow(trigger_dialog_step, self.play.total_steps)
        self.step_iter = self._next_step()

    def generate_event_flow(self, trigger_dialog_step, total_steps) -> List[EventName]:
        return []

    def _next_step(self) -> Generator[InteractionLike]:
        for event_name in self.event_flow:
            event = self.event_map[event_name]
            # 自动保存进度
            if self.play.current_step % self.trigger_save_step == 0:
                self.play.export_json()
            for life in EventLife:
                interaction = event.cycle(self.play.get_inputs(), life)
                self.play.current_step += 1
                yield interaction
        self.play.reset()
        StopIteration('大结局')

    def next_step(self) -> InteractionLike:
        return next(self.step_iter)

