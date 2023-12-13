#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.core.engine import Engine
from src.core.events import IAction, InteractionLike


def dialog_display(interaction: IAction.Dialog):
    ...


def action_display(interaction: IAction.Action):
    # 渲染动作
    print(f"选项:\n" + '\n'.join([f"{index + 1}. option" for index, option in enumerate(interaction.options)]))
    user_input = input('你的选择:')


def result_display(interaction: IAction.Result):
    print('结局:')


def dialog_interact(interaction: IAction.DialogCallback):
    # 渲染对话
    for chat_message in interaction(input('[你]:')):
        print(chat_message)


def action_interact(interaction: IAction.ActionCallback):
    interaction(input('[你的选择]:'))


class ConsoleUI:

    def __init__(self):
        self.engine = None

    def configure_engine(self, *args, **kwargs):
        self.engine = Engine(*args, **kwargs)

    def loop(self):
        while 1:
            try:
                i_action: InteractionLike = self.engine.next_step()
            except StopIteration:
                print('结束！')
                break
            if isinstance(i_action, IAction.Dialog):
                dialog_display(i_action)
            elif isinstance(i_action, IAction.Action):
                action_display(i_action)
            elif isinstance(i_action, IAction.Result):
                result_display(i_action)
            elif isinstance(i_action, IAction.ActionCallback):
                dialog_interact(i_action)
            elif isinstance(i_action, IAction.DialogCallback):
                action_interact(i_action)