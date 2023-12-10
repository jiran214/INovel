ACTION_PROMPT = """# 指令
为玩家提供{option_num}个交互式选项，并续写剧情，请使用{language}语言
"""


DIALOG_PROMPT = """# 指令
选择一个人物，该人物将会与玩家对话，推进剧情，请使用{language}语言
"""


CHAT_PROMPT = """剧情:{story}
场景:{scene}

{history}
主角: {input}
{charactor_name}:"""