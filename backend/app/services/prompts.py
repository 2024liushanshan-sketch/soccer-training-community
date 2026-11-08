"""
AI提示词模板
定义各种场景下的系统提示词和用户提示词模板
"""
from typing import Optional

# ==================== 训练相关提示词 ====================

TRAINING_PLAN_SYSTEM_PROMPT = """你是一位专业的足球训练教练，擅长为青少年球员制定个性化的训练计划。
你的任务是：
1. 根据用户的目标、水平、训练历史数据，制定科学合理的训练计划
2. 训练计划要具体、可执行，包含训练内容、时间、强度、注意事项
3. 用专业但易懂的语言，让用户能够理解并执行
4. 考虑青少年的身体特点，避免过度训练
"""

def get_training_plan_prompt(goal: str, level: str = "初级", duration: str = "1周", 
                             training_history: Optional[dict] = None) -> str:
    """
    生成训练计划提示词
    
    Args:
        goal: 训练目标（如"提升射门精度"）
        level: 水平（初级/中级/高级）
        duration: 训练周期（1周/2周/1个月）
        training_history: 训练历史数据（可选）
    
    Returns:
        完整的用户提示词
    """
    prompt = f"""请为我制定一个{duration}的足球训练计划。

训练目标：{goal}
当前水平：{level}
"""
    
    if training_history:
        prompt += f"""
训练历史数据：
- 平均每周训练天数：{training_history.get('avg_days', 'N/A')}天
- 平均每周训练时长：{training_history.get('avg_hours', 'N/A')}小时
- 训练完成率：{training_history.get('completion_rate', 'N/A')}%
"""
    
    prompt += """
请提供：
1. 每日训练安排（具体训练内容、时间、强度）
2. 训练要点和注意事项
3. 预期效果
4. 训练建议

请用清晰、专业的语言，确保训练计划可执行。
"""
    
    return prompt


# ==================== 数据分析提示词 ====================

TRAINING_ANALYSIS_SYSTEM_PROMPT = """你是一位专业的足球数据分析师，擅长分析训练数据并提供改进建议。
你的任务是：
1. 分析用户的训练数据趋势
2. 找出训练中的问题和亮点
3. 提供具体的改进建议
4. 用数据说话，但语言要通俗易懂
"""

def get_training_analysis_prompt(training_data: dict, weeks: int = 7) -> str:
    """
    生成训练数据分析提示词
    
    Args:
        training_data: 训练数据字典
        weeks: 分析周期（周数）
    
    Returns:
        完整的用户提示词
    """
    prompt = f"""请分析我最近{weeks}周的训练数据，并生成一份分析报告。

训练数据：
- 训练天数：{training_data.get('total_days', 0)}天
- 训练时长：{training_data.get('total_hours', 0)}小时
- 完成率：{training_data.get('completion_rate', 0)}%
- 训练计划数：{training_data.get('total_plans', 0)}个
- 已完成计划数：{training_data.get('completed_plans', 0)}个
"""
    
    if training_data.get('weekly_stats'):
        prompt += "\n每周详细数据：\n"
        for week_stat in training_data['weekly_stats']:
            prompt += f"- 第{week_stat.get('week', 'N/A')}周：{week_stat.get('days', 0)}天，{week_stat.get('hours', 0)}小时，完成率{week_stat.get('rate', 0)}%\n"
    
    prompt += """
请提供：
1. 数据趋势分析（训练时长、完成率的变化趋势）
2. 问题诊断（找出训练中的问题）
3. 亮点总结（做得好的地方）
4. 改进建议（具体的改进措施）
5. 下阶段目标（建议的训练目标）

请用专业但易懂的语言，确保报告有价值且可执行。
"""
    
    return prompt


# ==================== 足球知识问答提示词 ====================

ACADEMY_QA_SYSTEM_PROMPT = """你是一位专业的足球教练和足球知识专家，擅长回答关于足球技巧、战术、训练方法的问题。
你的任务是：
1. 准确回答用户关于足球的问题
2. 提供专业、实用的建议
3. 用通俗易懂的语言解释专业概念
4. 如果涉及训练方法，要提供具体可执行的步骤
"""

def get_academy_qa_prompt(question: str, context: Optional[str] = None) -> str:
    """
    生成足球知识问答提示词
    
    Args:
        question: 用户问题
        context: 上下文信息（如视频内容，可选）
    
    Returns:
        完整的用户提示词
    """
    prompt = f"问题：{question}\n\n"
    
    if context:
        prompt += f"相关上下文：{context}\n\n"
    
    prompt += "请用专业但易懂的语言回答，如果涉及训练方法，请提供具体步骤。"
    
    return prompt


# ==================== 健康营养提示词 ====================

HEALTH_NUTRITION_SYSTEM_PROMPT = """你是一位专业的运动营养师，擅长为青少年运动员提供营养建议。
你的任务是：
1. 根据用户的训练情况提供个性化的营养建议
2. 考虑青少年的身体发育特点
3. 提供具体、可执行的饮食建议
4. 用专业但易懂的语言
"""

def get_nutrition_advice_prompt(question: str, training_data: Optional[dict] = None) -> str:
    """
    生成营养建议提示词
    
    Args:
        question: 用户问题（如"我明天有比赛，应该吃什么？"）
        training_data: 训练数据（可选）
    
    Returns:
        完整的用户提示词
    """
    prompt = f"问题：{question}\n\n"
    
    if training_data:
        prompt += f"""
训练情况：
- 训练强度：{training_data.get('intensity', 'N/A')}
- 训练时间：{training_data.get('time', 'N/A')}
- 训练内容：{training_data.get('content', 'N/A')}
"""
    
    prompt += "\n请提供专业、具体的营养建议，考虑青少年运动员的特点。"
    
    return prompt


# ==================== 内容生成提示词 ====================

COMMUNITY_CONTENT_SYSTEM_PROMPT = """你是一位擅长写作的足球社区内容创作者，擅长帮助用户生成高质量的社区帖子。
你的任务是：
1. 根据用户的想法或关键词，生成完整的帖子内容
2. 内容要真实、有感染力、符合社区氛围
3. 根据用户选择的风格（专业/轻松/励志）调整语言风格
4. 确保内容积极正面，符合社区规范
"""

def get_content_generation_prompt(topic: str, keywords: str, style: str = "轻松") -> str:
    """
    生成内容生成提示词
    
    Args:
        topic: 话题（如"训练心得"）
        keywords: 关键词或想法
        style: 风格（专业/轻松/励志）
    
    Returns:
        完整的用户提示词
    """
    prompt = f"""请帮我生成一篇关于"{topic}"的社区帖子。

我的想法/关键词：{keywords}
风格要求：{style}

请生成：
1. 一段完整的帖子内容（100-200字）
2. 内容要真实、有感染力
3. 符合{style}的语言风格
4. 积极正面，符合社区规范

直接输出帖子内容即可，不需要其他说明。
"""
    
    return prompt


# ==================== 个人报告生成提示词 ====================

PROFILE_REPORT_SYSTEM_PROMPT = """你是一位专业的足球数据分析师，擅长生成个性化的球员成长报告。
你的任务是：
1. 分析用户的成长数据（训练、比赛、技能等）
2. 生成一份专业、有价值的成长报告
3. 包含成就总结、进步分析、未来建议
4. 用鼓励性的语言，激发用户继续努力
"""

def get_profile_report_prompt(user_data: dict, period: str = "month") -> str:
    """
    生成个人报告提示词
    
    Args:
        user_data: 用户数据字典
        period: 报告周期（week/month/year）
    
    Returns:
        完整的用户提示词
    """
    prompt = f"""请为我生成一份{period}的成长报告。

用户数据：
- 比赛场次：{user_data.get('matches', 0)}场
- 进球数：{user_data.get('goals', 0)}个
- 助攻数：{user_data.get('assists', 0)}个
- 训练天数：{user_data.get('training_days', 0)}天
- 训练时长：{user_data.get('training_hours', 0)}小时
"""
    
    if user_data.get('skills'):
        prompt += "\n技能评分：\n"
        for skill in user_data['skills']:
            prompt += f"- {skill.get('name', 'N/A')}：{skill.get('score', 0)}分\n"
    
    if user_data.get('growth_records'):
        prompt += "\n成长记录：\n"
        for record in user_data['growth_records'][:5]:  # 只取最近5条
            prompt += f"- {record.get('date', 'N/A')}：{record.get('event', 'N/A')}\n"
    
    prompt += """
请生成一份包含以下内容的成长报告：
1. 成就总结（这段时间的亮点和成就）
2. 进步分析（各方面的进步情况）
3. 数据解读（关键数据的含义）
4. 未来建议（下阶段的训练建议和目标）

请用鼓励性的语言，让报告既专业又有温度。
"""
    
    return prompt


# ==================== 辅助函数 ====================

def format_messages(system_prompt: str, user_prompt: str) -> list:
    """
    格式化消息列表
    
    Args:
        system_prompt: 系统提示词
        user_prompt: 用户提示词
    
    Returns:
        格式化的消息列表
    """
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

