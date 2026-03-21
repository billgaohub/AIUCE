"""
L3 推理层：张良/军机处
Multi-Path Reasoning Engine

职责：
1. 多路径推演决策后果
2. 运筹帷幄之中，决胜千里之外
3. 利用心智模型执行多路径 Consequence 坍缩
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import random


@dataclass
class ReasoningPath:
    """推理路径"""
    path_id: str
    description: str
    likelihood: float  # 可能性 0-1
    consequences: List[str]  # 后果列表
    pros: List[str]
    cons: List[str]
    final_score: float = 0.0


@dataclass
class MindModel:
    """心智模型（25个视角）"""
    model_id: str
    name: str
    description: str
    perspective: str              # 视角描述
    questions: List[str] = field(default_factory=list)  # 该模型会问的问题
    enabled: bool = True


class ReasoningLayer:
    """
    推理层 - 张良/军机处
    
    "运筹帷幄之中，决胜千里之外"
    
    25 个心智模型在此昼夜不停推演决策后果。
    执行多路径 Consequence 坍缩，为决策提供依据。
    """

    # ── 25 个心智模型 ───────────────────────────────────────────
    # 军机处昼夜不停，25个视角全维度推演
    MIND_MODELS = [
        # ── 核心决策模型 ──────────────────────────────────────────
        MindModel(
            model_id="optimist",
            name="乐观派",
            description="评估最佳情景",
            perspective="最好会发生什么？",
            questions=["最佳结果是什么？", "如何最大化收益？"]
        ),
        MindModel(
            model_id="pessimist",
            name="悲观派",
            description="评估最坏情景",
            perspective="最坏会发生什么？",
            questions=["最坏结果是什么？", "如何避免灾难？"]
        ),
        MindModel(
            model_id="risk_analyst",
            name="风险评估师",
            description="量化风险",
            perspective="失败的概率有多大？",
            questions=["有哪些已知风险？", "概率分布如何？", "风险敞口多大？"]
        ),
        # ── 合规与约束模型 ─────────────────────────────────────────
        MindModel(
            model_id="lawyer",
            name="律师",
            description="合规性检查",
            perspective="这合法吗？合规吗？",
            questions=["合法吗？", "合规吗？", "有哪些法律风险？"]
        ),
        MindModel(
            model_id="ethicist",
            name="伦理学家",
            description="道德审视",
            perspective="这是对的事吗？",
            questions=["道德吗？", "对各方公平吗？", "符合价值观吗？"]
        ),
        MindModel(
            model_id="constitution_guard",
            name="宪法守护者",
            description="主权边界检查",
            perspective="是否违反最高意志？",
            questions=["是否越权？", "是否违反宪法？", "用户主权是否被尊重？"]
        ),
        # ── 价值与利益模型 ─────────────────────────────────────────
        MindModel(
            model_id="economist",
            name="经济学家",
            description="成本收益分析",
            perspective="投入产出比如何？",
            questions=["成本多少？", "收益多大？", "机会成本是什么？"]
        ),
        MindModel(
            model_id="investor",
            name="投资者",
            description="ROI视角",
            perspective="这笔投资值得吗？",
            questions=["回报周期多长？", "风险调整后收益？", "IRR多少？"]
        ),
        MindModel(
            model_id="marketer",
            name="营销专家",
            description="用户价值视角",
            perspective="这能帮到用户吗？",
            questions=["用户真正需要吗？", "使用体验如何？", "会有什么反馈？"]
        ),
        # ── 心理与动机模型 ─────────────────────────────────────────
        MindModel(
            model_id="psychologist",
            name="心理学家",
            description="动机分析",
            perspective="背后的动机是什么？",
            questions=["用户真正想要什么？", "表面需求还是深层需求？", "情绪状态如何？"]
        ),
        MindModel(
            model_id="negotiator",
            name="谈判专家",
            description="多方博弈",
            perspective="各方利益如何平衡？",
            questions=["各方诉求是什么？", "如何达成共赢？", "有没有双赢方案？"]
        ),
        MindModel(
            model_id="storyteller",
            name="故事家",
            description="叙事框架",
            perspective="这背后的故事是什么？",
            questions=["如何向用户解释？", "如何让方案更有说服力？"]
        ),
        # ── 历史与经验模型 ─────────────────────────────────────────
        MindModel(
            model_id="historian",
            name="历史学家",
            description="历史类比",
            perspective="历史上类似情况如何收场？",
            questions=["有先例吗？", "前人怎么做的？", "有哪些教训？"]
        ),
        MindModel(
            model_id="scientist",
            name="科学家",
            description="假设检验",
            perspective="这可以被验证吗？",
            questions=["假设是什么？", "如何验证？", "实验设计？"]
        ),
        MindModel(
            model_id="statistician",
            name="统计学家",
            description="数据分析",
            perspective="数据说明了什么？",
            questions=["样本量够吗？", "统计显著性？", "因果还是相关？"]
        ),
        # ── 技术与可行性模型 ───────────────────────────────────────
        MindModel(
            model_id="engineer",
            name="工程师",
            description="可行性分析",
            perspective="技术上能做到吗？",
            questions=["技术方案可行吗？", "扩展性如何？", "有哪些技术债务？"]
        ),
        MindModel(
            model_id="architect",
            name="架构师",
            description="系统设计",
            perspective="架构合理吗？",
            questions=["模块划分清晰吗？", "接口设计合理吗？", "如何演进？"]
        ),
        MindModel(
            model_id="devops",
            name="运维工程师",
            description="稳定性视角",
            perspective="能稳定运行吗？",
            questions=["监控到位吗？", "容错如何？", "灾备方案？"]
        ),
        # ── 时间与演化模型 ─────────────────────────────────────────
        MindModel(
            model_id="gardener",
            name="园丁",
            description="长期培育",
            perspective="3年后这还在吗？",
            questions=["可持续吗？", "维护成本？", "如何迭代？"]
        ),
        MindModel(
            model_id="futurist",
            name="未来学家",
            description="趋势外推",
            perspective="5-10年后会怎样？",
            questions=["趋势如何？", "有哪些颠覆性因素？", "长期影响？"]
        ),
        # ── 执行与行动模型 ─────────────────────────────────────────
        MindModel(
            model_id="soldier",
            name="士兵",
            description="执行效率",
            perspective="如何快速落地？",
            questions=["第一步做什么？", "关键路径？", "如何快速迭代？"]
        ),
        MindModel(
            model_id="missionary",
            name="传教士",
            description="使命驱动",
            perspective="这符合更高使命吗？",
            questions=["使命感？", "愿景一致吗？", "初心是什么？"]
        ),
        MindModel(
            model_id="teacher",
            name="教师",
            description="教育视角",
            perspective="这能帮用户学到什么？",
            questions=["如何解释清楚？", "有什么教育价值？", "用户能理解吗？"]
        ),
        MindModel(
            model_id="designer",
            name="设计师",
            description="用户体验",
            perspective="用起来舒服吗？",
            questions=["体验流畅吗？", "界面美观吗？", "符合直觉吗？"]
        ),
        MindModel(
            model_id="philosopher",
            name="哲学家",
            description="本质追问",
            perspective="这为什么重要？",
            questions=["本质是什么？", "真正的问题是什么？", "有意义吗？"]
        ),
    ]

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.active_models = self.config.get("active_models", self.MIND_MODELS)
        self.reasoning_depth = self.config.get("depth", 3)  # 推理深度
        self.last_reasoning = None

    def reason(
        self,
        user_input: str,
        perception_data: Dict[str, Any],
        memories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        多路径推理
        
        对用户输入进行多角度、多路径的推理分析。
        """
        paths = []
        insights = []
        
        # Step 1: 理解问题本质
        problem = self._decompose_problem(user_input, perception_data)
        
        # Step 2: 多心智模型分析
        for model in self.active_models:
            analysis = self._analyze_with_model(
                problem, model, perception_data, memories
            )
            insights.append(analysis)
        
        # Step 3: 生成多个行动路径
        paths = self._generate_paths(problem, insights)
        
        # Step 4: 评估并排序路径
        for path in paths:
            path.final_score = self._score_path(path, insights)
        
        paths.sort(key=lambda p: p.final_score, reverse=True)
        
        # Step 5: Consequence 坍缩
        collapsed = self._collapse_consequences(paths, insights)
        
        result = {
            "problem": problem,
            "insights": insights,
            "paths": [
                {
                    "id": p.path_id,
                    "description": p.description,
                    "score": p.final_score,
                    "likelihood": p.likelihood,
                    "pros": p.pros,
                    "cons": p.cons
                }
                for p in paths
            ],
            "recommendation": paths[0].description if paths else None,
            "confidence": paths[0].final_score if paths else 0,
            "collapsed_reasoning": collapsed
        }
        
        self.last_reasoning = result
        return result

    def _decompose_problem(
        self,
        user_input: str,
        perception_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分解问题"""
        return {
            "raw_input": user_input,
            "type": self._classify_problem(user_input),
            "context": perception_data.get("raw", ""),
            "constraints": self._extract_constraints(user_input),
            "goals": self._extract_goals(user_input)
        }

    def _classify_problem(self, text: str) -> str:
        """问题分类"""
        text_lower = text.lower()
        if any(k in text_lower for k in ["如何", "怎么", "方法", "步骤"]):
            return "how_to"
        elif any(k in text_lower for k in ["为什么", "原因", "为何"]):
            return "why"
        elif any(k in text_lower for k in ["什么", "哪个", "哪些"]):
            return "what"
        elif any(k in text_lower for k in ["帮我", "请", "能不能", "可以帮我"]):
            return "task"
        elif any(k in text_lower for k in ["比较", "对比", "区别"]):
            return "compare"
        return "general"

    def _extract_constraints(self, text: str) -> List[str]:
        """提取约束条件"""
        constraints = []
        if "但不" in text:
            constraints.append("包含否定条件")
        if "只能" in text:
            constraints.append("限制条件")
        return constraints

    def _extract_goals(self, text: str) -> List[str]:
        """提取目标"""
        goals = []
        # 简单关键词提取
        if "为了" in text:
            goals.append("明确目标")
        if "想要" in text or "希望" in text:
            goals.append("期望结果")
        return goals

    def _analyze_with_model(
        self,
        problem: Dict[str, Any],
        model: MindModel,
        perception_data: Dict[str, Any],
        memories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """使用心智模型分析问题"""
        return {
            "model": model.name,
            "perspective": model.perspective,
            "analysis": f"[{model.name}] 视角分析",
            "key_considerations": [
                f"从{model.description}角度思考"
            ],
            "concerns": [],
            "suggestions": []
        }

    def _generate_paths(
        self,
        problem: Dict[str, Any],
        insights: List[Dict[str, Any]]
    ) -> List[ReasoningPath]:
        """生成多个行动路径"""
        paths = []
        problem_type = problem.get("type", "general")
        
        if problem_type == "task":
            # 任务类型：生成执行路径
            paths.append(ReasoningPath(
                path_id="path-1",
                description="直接执行",
                likelihood=0.7,
                consequences=["完成任务", "消耗资源"],
                pros=["效率高", "直接"],
                cons=["可能不够周全"]
            ))
            paths.append(ReasoningPath(
                path_id="path-2",
                description="分步执行 + 确认",
                likelihood=0.85,
                consequences=["更安全", "需要更多交互"],
                pros=["风险低", "可控"],
                cons=["速度较慢"]
            ))
            paths.append(ReasoningPath(
                path_id="path-3",
                description="先研究后执行",
                likelihood=0.6,
                consequences=["准备充分", "延迟执行"],
                pros=["质量高"],
                cons=["周期长"]
            ))
        else:
            # 问答类型
            paths.append(ReasoningPath(
                path_id="path-a",
                description="简洁直接回答",
                likelihood=0.8,
                consequences=["快速响应"],
                pros=["效率高"],
                cons=["可能不够详细"]
            ))
            paths.append(ReasoningPath(
                path_id="path-b",
                description="详细解释 + 举例",
                likelihood=0.75,
                consequences=["全面理解", "耗时更长"],
                pros=["更清晰"],
                cons=["信息量大"]
            ))
            
        return paths

    def _score_path(self, path: ReasoningPath, insights: List[Dict[str, Any]]) -> float:
        """计算路径评分"""
        score = path.likelihood * 50  # 基础分
        
        # 加分项
        if len(path.pros) > len(path.cons):
            score += 20
        if path.likelihood > 0.7:
            score += 15
        if len(path.consequences) > 0:
            score += 10
            
        # 减分项
        if len(path.cons) > 2:
            score -= 10
            
        return min(100, max(0, score))

    def _collapse_consequences(
        self,
        paths: List[ReasoningPath],
        insights: List[Dict[str, Any]]
    ) -> str:
        """Consequence 坍缩 - 选择最优路径"""
        if not paths:
            return "无法推理出有效路径"
        
        best = paths[0]
        reasoning = f"经过 {len(paths)} 条路径推演，选择「{best.description}」"
        reasoning += f"（置信度 {best.final_score:.0f}%）"
        
        if best.cons:
            reasoning += f"，需注意：{'、'.join(best.cons)}"
            
        return reasoning

    def add_mind_model(self, model: MindModel):
        """添加心智模型"""
        self.active_models.append(model)

    def get_models_info(self) -> List[Dict[str, str]]:
        """获取当前心智模型列表"""
        return [
            {"name": m.name, "description": m.description}
            for m in self.active_models
        ]
