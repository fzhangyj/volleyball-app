"""
AI提示词模板
"""

# ========== 系统角色提示词 ==========

VOLLEYBALL_COACH_SYSTEM = """你是一位专业的排球教练，拥有10年以上的执教经验。
你的特点：
- 专业：精通排球技术、战术、规则
- 耐心：善于用简单易懂的语言解释复杂概念
- 鼓励：总是给予学员积极的反馈和建设性建议
- 实用：注重实战技巧，提供可操作的训练方法

请用友好、专业的语气回答学员的问题。"""


AI_ASSISTANT_SYSTEM = """你是一个专业的排球学习助手。
你的职责是：
- 回答排球相关的技术、战术、规则问题
- 提供训练建议和计划
- 分析动作要领
- 解释比赛规则

请保持回答简洁、专业、实用。"""


# ========== 功能模板 ==========

def get_action_analysis_prompt(action_type: str, user_description: str) -> str:
    """
    动作分析提示词
    
    Args:
        action_type: 动作类型（如：发球、扣球、垫球等）
        user_description: 用户描述的动作细节
    
    Returns:
        完整的提示词
    """
    return f"""请分析以下排球{action_type}动作，并提供专业建议：

用户描述：{user_description}

请从以下几个方面进行分析：
1. **动作要点**：这个动作的关键技术要领是什么？
2. **常见错误**：初学者容易犯哪些错误？
3. **改进建议**：针对用户描述，提供3-5条具体的改进建议
4. **训练方法**：推荐2-3个针对性的训练方法

请用清晰的结构化格式回答，使用Markdown格式。"""


def get_training_plan_prompt(
    skill_level: str,
    focus_area: str,
    training_time: str,
    goal: str
) -> str:
    """
    训练计划生成提示词
    
    Args:
        skill_level: 技能水平（初级/中级/高级）
        focus_area: 重点提升领域（如：发球、扣球、防守等）
        training_time: 训练时间（如：每周3次，每次1小时）
        goal: 训练目标
    
    Returns:
        完整的提示词
    """
    return f"""请为我制定一个个性化的排球训练计划：

**基本信息**：
- 技能水平：{skill_level}
- 重点提升：{focus_area}
- 训练时间：{training_time}
- 训练目标：{goal}

请提供：
1. **训练周期**：建议的训练周期（如4周、8周）
2. **每周计划**：详细的每周训练安排
3. **训练内容**：具体的训练项目和方法
4. **强度建议**：训练强度和休息安排
5. **评估标准**：如何判断训练效果

请用清晰的结构化格式回答，使用Markdown格式。"""


def get_rule_explanation_prompt(rule_question: str) -> str:
    """
    规则解释提示词
    
    Args:
        rule_question: 用户的规则问题
    
    Returns:
        完整的提示词
    """
    return f"""请解释以下排球规则问题：

问题：{rule_question}

请提供：
1. **规则说明**：清晰解释相关规则
2. **实例说明**：举2-3个实际比赛中的例子
3. **裁判判罚**：这种情况下裁判会如何判罚
4. **注意事项**：球员需要注意的要点

请用通俗易懂的语言解释，使用Markdown格式。"""


def get_tactics_analysis_prompt(
    situation: str,
    opponent_info: str
) -> str:
    """
    战术分析提示词
    
    Args:
        situation: 比赛情况描述
        opponent_info: 对手信息
    
    Returns:
        完整的提示词
    """
    return f"""请分析以下排球比赛战术：

**比赛情况**：{situation}

**对手信息**：{opponent_info}

请提供：
1. **局势分析**：当前局势的优劣势分析
2. **战术建议**：推荐3-5种可行的战术打法
3. **阵型调整**：建议的阵型和人员配置
4. **注意事项**：需要特别注意的要点
5. **应变策略**：如果战术不奏效，如何调整

请用专业且实用的方式回答，使用Markdown格式。"""


def get_video_commentary_prompt(
    video_info: str,
    key_moments: str
) -> str:
    """
    视频解说生成提示词
    
    Args:
        video_info: 视频基本信息
        key_moments: 关键时刻描述
    
    Returns:
        完整的提示词
    """
    return f"""请为以下排球比赛视频生成专业解说词：

**视频信息**：{video_info}

**关键时刻**：
{key_moments}

请提供：
1. **整体概述**：比赛的整体情况和亮点
2. **技术解析**：关键时刻的技术动作解析
3. **战术分析**：双方的战术运用
4. **精彩点评**：对精彩瞬间的专业点评
5. **学习要点**：观众可以学习的技术和战术要点

解说风格：专业但不失趣味，适合不同水平的观众。使用Markdown格式。"""


def get_training_diary_analysis_prompt(
    diary_content: str,
    training_date: str
) -> str:
    """
    训练日记分析提示词
    
    Args:
        diary_content: 训练日记内容
        training_date: 训练日期
    
    Returns:
        完整的提示词
    """
    return f"""请分析以下训练日记，并提供反馈：

**训练日期**：{training_date}

**日记内容**：
{diary_content}

请提供：
1. **训练总结**：总结本次训练的重点和收获
2. **亮点分析**：指出做得好的地方
3. **改进建议**：提出2-3条具体的改进建议
4. **下次重点**：下次训练应该重点关注什么
5. **鼓励话语**：给予积极的鼓励

语气要友好、专业、鼓励。使用Markdown格式。"""


def get_qa_prompt(question: str) -> str:
    """
    通用问答提示词
    
    Args:
        question: 用户问题
    
    Returns:
        完整的提示词
    """
    return f"""请回答以下排球相关问题：

{question}

请提供清晰、专业、实用的回答。如果问题涉及技术动作，请说明要点；如果涉及规则，请准确解释；如果涉及训练，请给出可操作的建议。

使用Markdown格式组织答案。"""


# ========== 快速提示词构建 ==========

class PromptBuilder:
    """提示词构建器"""
    
    @staticmethod
    def build_with_context(
        user_message: str,
        context_type: str,
        context_data: dict
    ) -> list:
        """
        构建带上下文的消息列表
        
        Args:
            user_message: 用户消息
            context_type: 上下文类型（coach/assistant）
            context_data: 上下文数据
        
        Returns:
            消息列表
        """
        messages = []
        
        # 添加系统提示词
        if context_type == "coach":
            messages.append({
                "role": "system",
                "content": VOLLEYBALL_COACH_SYSTEM
            })
        else:
            messages.append({
                "role": "system",
                "content": AI_ASSISTANT_SYSTEM
            })
        
        # 添加上下文信息
        if context_data:
            context_str = "\n".join([f"{k}: {v}" for k, v in context_data.items()])
            messages.append({
                "role": "system",
                "content": f"用户背景信息：\n{context_str}"
            })
        
        # 添加用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    @staticmethod
    def build_conversation(
        history: list,
        new_message: str,
        system_prompt: str = None
    ) -> list:
        """
        构建对话历史消息列表
        
        Args:
            history: 历史对话 [{"role": "user/assistant", "content": "..."}]
            new_message: 新消息
            system_prompt: 系统提示词
        
        Returns:
            消息列表
        """
        messages = []
        
        # 添加系统提示词
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        else:
            messages.append({
                "role": "system",
                "content": VOLLEYBALL_COACH_SYSTEM
            })
        
        # 添加历史对话（最多保留最近5轮）
        if history:
            messages.extend(history[-10:])  # 最多保留10条消息（5轮对话）
        
        # 添加新消息
        messages.append({
            "role": "user",
            "content": new_message
        })
        
        return messages

