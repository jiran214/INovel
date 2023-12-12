SETTINGS_PROMPT = """# 故事:{title}
## 故事背景
{background}

## 人物角色
{characters}

## 其它
- 故事进度:{current_step}/{total_steps}

## 目标
{goal}

## 剧情发展
{play_context}

## 玩家上一轮行为
{user_interaction}

## 玩家上一轮结果
{result}
"""

END_PROMPT = """# 指令
根据剧情发展和故事进度，请为该故事生成一个结局，如果进度还没到最后，则生成一个阶段性的结局"""

