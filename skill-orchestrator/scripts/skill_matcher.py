#!/usr/bin/env python3
"""
Skill Matcher - 智能技能匹配引擎

功能：
1. 基于关键词和语义相似度匹配 skills
2. 计算优先级评分
3. 生成执行计划
4. 输出匹配报告

用法：
    python scripts/skill_matcher.py "用户请求文本"
    python scripts/skill_matcher.py --config config/matching_rules.json
"""

import json
import sys
import os
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SkillInfo:
    """Skill 信息"""
    name: str
    description: str
    triggers: List[str]
    priority: str  # P0, P1, P2, P3
    category: str

@dataclass
class MatchResult:
    """匹配结果"""
    skill_name: str
    score: float
    priority: str
    matched_keywords: List[str]
    reason: str

class SkillMatcher:
    """智能技能匹配器"""
    
    def __init__(self, skills_dir: str = None):
        self.skills_dir = skills_dir or self._find_skills_dir()
        self.skills = self._load_skills()
        self.matching_rules = self._load_matching_rules()
        
    def _find_skills_dir(self) -> str:
        """查找 skills 目录"""
        # 默认路径
        default_paths = [
            os.path.expanduser("~/.lingma/skills"),
            os.path.join(os.getcwd(), ".lingma", "skills"),
            os.path.join(os.getcwd(), "skills"),
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                return path
        
        return default_paths[0]
    
    def _load_skills(self) -> List[SkillInfo]:
        """加载所有可用的 skills"""
        skills = []
        
        # 从 skills_database.json 加载
        db_path = os.path.join(os.path.dirname(__file__), "..", "config", "skills_database.json")
        
        if os.path.exists(db_path):
            try:
                with open(db_path, 'r', encoding='utf-8') as f:
                    db = json.load(f)
                    
                    # 遍历所有分类
                    for category, skills_list in db.get("skills_database", {}).items():
                        for skill_data in skills_list:
                            # 加载所有 skills（无论是否安装）
                            # 安装状态仅用于提示用户，不影响匹配
                            skills.append(SkillInfo(
                                name=skill_data["name"],
                                description=skill_data["description"],
                                triggers=skill_data.get("triggers", []),
                                priority=skill_data.get("priority", "P2"),
                                category=skill_data.get("category", "general")
                            ))
                    
                    print(f"✅ 从数据库加载了 {len(skills)} 个 skills")
                    return skills
                    
            except Exception as e:
                print(f"Warning: Failed to load skills database: {e}")
        
        # 如果数据库加载失败，使用预定义的 skills
        print("⚠️  使用预定义 skills")
        
        # 预定义的 skills 列表（可以从配置文件加载）
        predefined_skills = [
            SkillInfo(
                name="create-skill",
                description="创建新的 skill",
                triggers=["创建 skill", "编写 skill", "新 skill", "skill 文档"],
                priority="P0",
                category="creation"
            ),
            SkillInfo(
                name="find-skills",
                description="查找和安装 skills",
                triggers=["查找 skill", "安装 skill", "有没有 skill", "推荐 skill"],
                priority="P0",
                category="discovery"
            ),
            SkillInfo(
                name="code-review-and-quality",
                description="代码审查和质量检查",
                triggers=["审查", "review", "PR", "代码检查", "合并前"],
                priority="P0",
                category="quality"
            ),
            SkillInfo(
                name="systematic-debugging",
                description="系统化调试",
                triggers=["bug", "错误", "调试", "不工作", "异常", "报错"],
                priority="P0",
                category="debugging"
            ),
            SkillInfo(
                name="refactor",
                description="代码重构",
                triggers=["重构", "优化代码", "清理代码", "改进结构", "简化"],
                priority="P0",
                category="refactoring"
            ),
            SkillInfo(
                name="java-springboot",
                description="Spring Boot 最佳实践",
                triggers=["Spring Boot", "Java 后端", "Spring", "REST API"],
                priority="P1",
                category="language"
            ),
            SkillInfo(
                name="python-design-patterns",
                description="Python 设计模式",
                triggers=["Python", "设计模式", "Python 架构", "类设计"],
                priority="P1",
                category="language"
            ),
            SkillInfo(
                name="improve-codebase-architecture",
                description="架构改进",
                triggers=["架构", "重构架构", "改进结构", "模块解耦"],
                priority="P1",
                category="architecture"
            ),
            SkillInfo(
                name="mermaid-diagrams",
                description="绘制图表",
                triggers=["图表", "流程图", "架构图", "可视化", "diagram", "UML"],
                priority="P1",
                category="visualization"
            ),
            SkillInfo(
                name="documentation-writer",
                description="编写文档",
                triggers=["文档", "README", "写文档", "说明", "API 文档"],
                priority="P2",
                category="documentation"
            ),
            SkillInfo(
                name="webapp-testing",
                description="Web 应用测试",
                triggers=["测试", "Web 测试", "Playwright", "UI 测试", "E2E"],
                priority="P2",
                category="testing"
            ),
        ]
        
        return predefined_skills
    
    def _load_matching_rules(self) -> Dict:
        """加载匹配规则"""
        rules_path = os.path.join(os.path.dirname(__file__), "..", "config", "matching_rules.json")
        
        default_rules = {
            "keyword_weight": 0.5,
            "semantic_weight": 0.2,
            "frequency_weight": 0.2,
            "preference_weight": 0.1,
            "min_score_threshold": 30,
            "max_results": 5
        }
        
        if os.path.exists(rules_path):
            try:
                with open(rules_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 提取 matching_rules 部分
                    return config.get("matching_rules", default_rules)
            except Exception as e:
                print(f"Warning: Failed to load config file: {e}")
                return default_rules
        
        return default_rules
    
    def match(self, user_request: str) -> List[MatchResult]:
        """
        匹配用户请求到合适的 skills
        
        Args:
            user_request: 用户请求文本
            
        Returns:
            匹配的 skills 列表，按分数排序
        """
        results = []
        
        for skill in self.skills:
            score, matched_keywords = self._calculate_score(user_request, skill)
            
            if score >= self.matching_rules["min_score_threshold"]:
                result = MatchResult(
                    skill_name=skill.name,
                    score=score,
                    priority=skill.priority,
                    matched_keywords=matched_keywords,
                    reason=self._generate_reason(skill, matched_keywords)
                )
                results.append(result)
        
        # 按分数排序
        results.sort(key=lambda x: x.score, reverse=True)
        
        # 限制返回数量
        max_results = self.matching_rules["max_results"]
        return results[:max_results]
    
    def _calculate_score(self, user_request: str, skill: SkillInfo) -> Tuple[float, List[str]]:
        """
        计算匹配分数
        
        Returns:
            (分数, 匹配的关键词列表)
        """
        # 1. 关键词匹配 (40%)
        keyword_score, matched_keywords = self._keyword_match(user_request, skill)
        
        # 2. 语义相似度 (30%) - 简化版本，可以使用更高级的 NLP
        semantic_score = self._semantic_similarity(user_request, skill.description)
        
        # 3. 历史使用频率 (20%) - 这里简化为固定值
        frequency_score = 50  # 默认中等频率
        
        # 4. 用户偏好 (10%) - 这里简化为固定值
        preference_score = 50  # 默认无特殊偏好
        
        # 加权计算
        weights = self.matching_rules
        final_score = (
            keyword_score * weights["keyword_weight"] +
            semantic_score * weights["semantic_weight"] +
            frequency_score * weights["frequency_weight"] +
            preference_score * weights["preference_weight"]
        )
        
        return round(final_score, 2), matched_keywords
    
    def _keyword_match(self, user_request: str, skill: SkillInfo) -> Tuple[float, List[str]]:
        """关键词匹配"""
        user_request_lower = user_request.lower()
        matched = []
        
        for trigger in skill.triggers:
            trigger_lower = trigger.lower()
            # 支持多种匹配方式
            # 1. 触发词包含在请求中（子串匹配）
            # 2. 请求包含在触发词中
            # 3. 对于英文：分词后部分匹配
            # 4. 对于中文：直接子串匹配
            if (trigger_lower in user_request_lower or 
                user_request_lower in trigger_lower):
                matched.append(trigger)
            else:
                # 尝试分词匹配（仅对英文有效）
                trigger_words = trigger_lower.split()
                if len(trigger_words) > 1:
                    if any(word in user_request_lower for word in trigger_words if len(word) > 1):
                        matched.append(trigger)
        
        # 计算关键词匹配分数
        if len(matched) > 0:
            # 有匹配时，基础分数为 60，每个匹配的关键词加 10 分
            score = 60 + (len(matched) * 10)
        else:
            score = 0
        
        return min(score, 100), matched
    
    def _semantic_similarity(self, text1: str, text2: str) -> float:
        """
        简化的语义相似度计算
        实际项目中可以使用 transformers 或其他 NLP 库
        """
        # 简单的词袋模型相似度
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        # Jaccard 相似度
        similarity = len(intersection) / len(union)
        
        return similarity * 100
    
    def _generate_reason(self, skill: SkillInfo, matched_keywords: List[str]) -> str:
        """生成匹配原因说明"""
        if matched_keywords:
            return f"匹配到关键词: {', '.join(matched_keywords)}"
        else:
            return f"基于语义相似度匹配到 {skill.description}"
    
    def generate_execution_plan(self, matches: List[MatchResult]) -> Dict:
        """
        生成执行计划
        
        Returns:
            执行计划字典
        """
        # 按优先级分组
        p0_skills = [m for m in matches if m.priority == "P0"]
        p1_skills = [m for m in matches if m.priority == "P1"]
        p2_skills = [m for m in matches if m.priority == "P2"]
        p3_skills = [m for m in matches if m.priority == "P3"]
        
        plan = {
            "timestamp": datetime.now().isoformat(),
            "total_matches": len(matches),
            "execution_order": [],
            "parallel_groups": [],
            "estimated_time_seconds": len(matches) * 5  # 假设每个 skill 5秒
        }
        
        # 串行执行 P0
        if p0_skills:
            plan["execution_order"].append({
                "phase": "Phase 1 - Critical",
                "skills": [asdict(m) for m in p0_skills],
                "execution_type": "sequential"
            })
        
        # 并行执行 P1
        if p1_skills:
            plan["parallel_groups"].append({
                "phase": "Phase 2 - Important",
                "skills": [asdict(m) for m in p1_skills],
                "execution_type": "parallel"
            })
        
        # 条件执行 P2/P3
        if p2_skills or p3_skills:
            plan["execution_order"].append({
                "phase": "Phase 3 - Optional",
                "skills": [asdict(m) for m in p2_skills + p3_skills],
                "execution_type": "conditional"
            })
        
        return plan
    
    def generate_report(self, user_request: str, matches: List[MatchResult], plan: Dict) -> str:
        """生成匹配报告"""
        report = []
        report.append("=" * 60)
        report.append("Skill Matcher - 匹配报告")
        report.append("=" * 60)
        report.append("")
        report.append(f"用户请求: {user_request}")
        report.append(f"匹配时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"匹配数量: {len(matches)}")
        report.append("")
        
        if matches:
            report.append("匹配结果:")
            report.append("-" * 60)
            for i, match in enumerate(matches, 1):
                report.append(f"{i}. {match.skill_name}")
                report.append(f"   优先级: {match.priority}")
                report.append(f"   分数: {match.score}")
                report.append(f"   原因: {match.reason}")
                report.append("")
            
            report.append("执行计划:")
            report.append("-" * 60)
            for phase in plan.get("execution_order", []):
                report.append(f"\n{phase['phase']} ({phase['execution_type']})")
                for skill in phase["skills"]:
                    report.append(f"  - {skill['skill_name']} (Score: {skill['score']})")
            
            for group in plan.get("parallel_groups", []):
                report.append(f"\n{group['phase']} ({group['execution_type']})")
                for skill in group["skills"]:
                    report.append(f"  - {skill['skill_name']} (Score: {skill['score']})")
        else:
            report.append("未找到匹配的 skills")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python skill_matcher.py <用户请求>")
        print("示例: python skill_matcher.py \"帮我创建一个 Java Spring Boot 项目\"")
        sys.exit(1)
    
    user_request = " ".join(sys.argv[1:])
    
    # 创建匹配器
    matcher = SkillMatcher()
    
    # 执行匹配
    matches = matcher.match(user_request)
    
    # 生成执行计划
    plan = matcher.generate_execution_plan(matches)
    
    # 生成报告
    report = matcher.generate_report(user_request, matches, plan)
    
    # 输出报告
    print(report)
    
    # 同时输出 JSON 格式（便于程序处理）
    output = {
        "request": user_request,
        "matches": [asdict(m) for m in matches],
        "plan": plan
    }
    
    # 保存到文件
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"match_result_{timestamp}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细结果已保存到: {output_file}")


if __name__ == "__main__":
    main()
