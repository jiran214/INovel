from typing import List, Optional
from pydantic import BaseModel, Field

from src.utils.utils import JsonImporter


class Character(BaseModel):
    name: str
    description: str


class NovelSettings(BaseModel):
    title: str = Field(description="故事标题")
    background: str = Field(description="故事背景")
    characters: List[Character] = Field(description="人物角色")
    goal: str = Field(description="主角目标")
    total_steps: int = Field(default=10, description="故事时长")
    option_num: int = Field(default=3, description="交互式剧情选项数量")
    language: str = Field(default='中文')

    """动态"""
    current_step: int = Field(default=1, description="当前进度")
    relate_characters: List[str] = Field(default=[], description="涉及人物")
    scene: Optional[str] = Field(default=None, description="场景")
    play_context_window: str = Field(default='暂无', description="剧情")
    play_context_memory: str = Field(default='暂无', description="关联剧情")

    def get_inputs(self):
        return self.model_dump()

    def update_play(self, play_context: str, user_interaction: str):
        self.play_context = play_context
        self.user_interaction = user_interaction

    @classmethod
    def load_json(cls, title):
        data_dict = JsonImporter().load(f"{title}.json")
        return cls(**data_dict)

    def export(self):
        JsonImporter().export(f"{self.title}.json", self.model_dump())