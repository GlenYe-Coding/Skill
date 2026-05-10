#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
意图提取器 (Intent Extractor)
负责从用户请求中提取动作、目标对象和技术栈信息。
遵循单一职责原则 (SRP) 和 KISS 原则。
"""

import re
from typing import Dict, List, Optional

try:
    import jieba
except ImportError:
    print("Warning: jieba not installed. Chinese segmentation will be limited.")


class IntentExtractor:
    """用户意图提取器"""

    def __init__(self):
        # 预定义意图模式 (Action Patterns)
        self.intent_patterns = {
            'create': r'(创建|新建|生成|建立|初始化|搭建)',
            'review': r'(审查|检查|review|审计|评估|检视)',
            'debug': r'(调试|修复|bug|错误|异常|报错|解决)',
            'refactor': r'(重构|优化|改进|清理|简化|enhance)',
            'test': r'(测试|验证|单元测试|集成测试|校验)',
            'document': r'(文档|说明|readme|注释|解释)',
            'deploy': r'(部署|发布|上线|docker|k8s|publish)',
            'search': r'(查找|搜索|寻找|有没有|find)',
        }

        # 技术栈关键词 (Tech Stack Keywords)
        self.tech_keywords = {
            'java': ['java', 'spring', 'springboot', 'maven', 'jdk'],
            'python': ['python', 'django', 'flask', 'pip', 'pytorch'],
            'frontend': ['react', 'vue', 'angular', 'javascript', 'typescript', 'css'],
            'database': ['mysql', 'postgres', 'mongodb', 'sql', 'redis'],
            'devops': ['docker', 'kubernetes', 'ci/cd', 'jenkins', 'aws'],
        }

        # 目标对象模式 (Target Patterns)
        self.target_patterns = {
            'skill': r'(skill|技能)',
            'project': r'(项目|工程|应用|系统)',
            'code': r'(代码|函数|类|模块|脚本)',
            'api': r'(api|接口|endpoint|服务)',
            'database': r'(数据库|表|schema|数据)',
        }

    def extract(self, text: str) -> Dict:
        """
        提取用户意图
        
        Args:
            text: 用户输入的原始文本
            
        Returns:
            包含 action, target, tech_stack, keywords 和 confidence 的字典
        """
        if not text or not isinstance(text, str):
            return self._empty_result()

        result = {
            'action': None,
            'target': None,
            'tech_stack': [],
            'keywords': self._segment_text(text),
            'confidence': 0.0
        }

        # 1. 识别动作类型
        action_scores = {}
        for action, pattern in self.intent_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                action_scores[action] = len(matches)

        if action_scores:
            result['action'] = max(action_scores, key=action_scores.get)
            # 基础置信度 0.8，每多一个匹配词增加 0.05
            match_count = action_scores[result['action']]
            result['confidence'] = min(0.95, 0.8 + (match_count * 0.05))

        # 2. 识别技术栈
        text_lower = text.lower()
        for tech, keywords in self.tech_keywords.items():
            if any(kw in text_lower for kw in keywords):
                result['tech_stack'].append(tech)

        # 3. 识别目标对象
        for target, pattern in self.target_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                result['target'] = target
                break

        return result

    def _segment_text(self, text: str) -> List[str]:
        """中文分词处理"""
        try:
            return list(jieba.cut(text))
        except Exception:
            # Fallback: 简单的按空格或字符分割
            return text.split()

    def _empty_result(self) -> Dict:
        """返回空结果模板"""
        return {
            'action': None,
            'target': None,
            'tech_stack': [],
            'keywords': [],
            'confidence': 0.0
        }


if __name__ == "__main__":
    # 简单测试
    extractor = IntentExtractor()
    
    test_cases = [
        "帮我创建一个 Java Spring Boot 项目",
        "审查这段代码的安全性",
        "如何调试 Python Flask 应用的数据库连接？"
    ]
    
    for case in test_cases:
        print(f"\n输入: {case}")
        print(f"结果: {extractor.extract(case)}")
