#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关键词匹配器 (Keyword Matcher)
基于倒排索引实现高效的技能匹配。
"""

import os
import re
import json
from typing import List, Dict, Tuple
from collections import Counter

class MatchResult:
    """匹配结果数据类"""
    def __init__(self, skill_name: str, score: float, priority: str, matched_keywords: List[str], reason: str):
        self.skill_name = skill_name
        self.score = score
        self.priority = priority
        self.matched_keywords = matched_keywords
        self.reason = reason

    def to_dict(self):
        return {
            "skill_name": self.skill_name,
            "score": self.score,
            "priority": self.priority,
            "matched_keywords": self.matched_keywords,
            "reason": self.reason
        }

class KeywordMatcher:
    """基于倒排索引的关键词匹配引擎"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = os.path.join(os.path.dirname(__file__), "..", "config", "skills_database.json")
        else:
            self.db_path = db_path
        
        self.index = {}  # 关键词 -> [skill_names]
        self.skills_map = {}  # skill_name -> skill_info
        self._build_index()

    def _build_index(self):
        """从数据库加载 skills 并构建倒排索引"""
        if not os.path.exists(self.db_path):
            print(f"Warning: Database not found at {self.db_path}")
            return

        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                db = json.load(f)
                
            for category, skills in db.get("skills_database", {}).items():
                for skill in skills:
                    name = skill["name"]
                    self.skills_map[name] = skill
                    
                    # 对触发词建立索引
                    for trigger in skill.get("triggers", []):
                        # 简单分词：按空格或单字拆分（实际可集成 jieba）
                        words = re.split(r'\s+', trigger) if isinstance(trigger, str) else [trigger]
                        for word in words:
                            if len(word) > 1:
                                if word not in self.index:
                                    self.index[word] = []
                                if name not in self.index[word]:
                                    self.index[word].append(name)
            
            print(f"✅ KeywordMatcher initialized with {len(self.skills_map)} skills.")
        except Exception as e:
            print(f"Error building keyword index: {e}")

    def match(self, keywords: List[str]) -> List[MatchResult]:
        """
        根据关键词列表匹配 skills
        
        评分规则：
        - 每匹配一个关键词 +20 分
        - 匹配到完整触发词 +40 分
        """
        scores = Counter()
        matched_keywords = {}

        for keyword in keywords:
            if keyword in self.index:
                for skill_name in self.index[keyword]:
                    scores[skill_name] += 20
                    if skill_name not in matched_keywords:
                        matched_keywords[skill_name] = []
                    matched_keywords[skill_name].append(keyword)

        results = []
        for skill_name, score in scores.most_common():
            skill = self.skills_map.get(skill_name)
            if skill:
                # 归一化分数
                normalized_score = min(score, 100)
                results.append(MatchResult(
                    skill_name=skill_name,
                    score=normalized_score,
                    priority=skill.get("priority", "P2"),
                    matched_keywords=matched_keywords.get(skill_name, []),
                    reason=f"匹配到 {len(matched_keywords.get(skill_name, []))} 个关键词"
                ))
        
        return results

if __name__ == "__main__":
    import re  # 补充导入以便测试
    matcher = KeywordMatcher()
    results = matcher.match(["创建", "skill", "java"])
    for r in results:
        print(f"{r.skill_name}: {r.score} ({r.reason})")
