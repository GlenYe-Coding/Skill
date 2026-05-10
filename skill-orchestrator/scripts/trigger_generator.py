#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
触发词生成器 (Trigger Generator)
为 Skills 自动生成多维度、多语言的匹配关键词。
"""

import re

class TriggerGenerator:
    def __init__(self):
        # 核心开发术语中英映射表
        self.term_map = {
            'security': ['安全', '审计', '漏洞', '加固'],
            'review': ['审查', '检查', '检视', '评估'],
            'debug': ['调试', '排错', '修复', 'bug'],
            'test': ['测试', '验证', '校验'],
            'deploy': ['部署', '发布', '上线', '运维'],
            'optimize': ['优化', '加速', '调优', '性能'],
            'design': ['设计', 'UI', 'UX', '界面', '布局'],
            'database': ['数据库', 'SQL', '数据', '存储'],
            'api': ['接口', 'API', '服务', 'endpoint'],
            'git': ['版本控制', '提交', 'commit', '分支'],
            'doc': ['文档', '说明', 'readme', '注释']
        }
        
        # 来源仓库特定的上下文词
        self.context_map = {
            'VoltAgent': ['agent', '智能体', 'AI助手'],
            'ComposioHQ': ['claude', 'anthropic', '集成'],
            'microsoft': ['微软', 'azure', 'vscode'],
            'vercel-labs': ['nextjs', 'react', 'frontend', '前端']
        }

    def generate(self, skill_name, source_repo=""):
        """
        生成触发词列表
        
        Args:
            skill_name: 技能名称 (如 "api-security")
            source_repo: 来源仓库 (如 "VoltAgent/awesome-agent-skills")
            
        Returns:
            去重后的触发词列表
        """
        triggers = set()
        
        # 1. 基础名称拆解 (处理 kebab-case 和 camelCase)
        parts = re.split(r'[-_]', skill_name)
        if len(parts) == 1:
            # 尝试拆解驼峰命名
            parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', skill_name)
        
        # 将拆解出的单词加入触发词
        for part in parts:
            triggers.add(part.lower())
        
        # 2. 组合词触发 (如 "api security")
        triggers.add(" ".join(parts).lower())
        triggers.add(skill_name.lower())
        
        # 3. 同义词扩展 (基于 term_map)
        for part in parts:
            if part in self.term_map:
                triggers.update(self.term_map[part])
        
        # 4. 上下文增强 (基于 source_repo)
        for repo_key, context_words in self.context_map.items():
            if repo_key in source_repo:
                triggers.update(context_words)
                break
        
        # 5. 过滤掉过短的词（如单个字母）
        return [t for t in triggers if len(t) > 1]

if __name__ == "__main__":
    gen = TriggerGenerator()
    
    # 测试用例
    test_cases = [
        ("api-security", "hardw00t/ai-security-arsenal"),
        ("web-design-guidelines", "VoltAgent/awesome-agent-skills"),
        ("git-commit-helper", "VoltAgent/awesome-agent-skills")
    ]
    
    for name, source in test_cases:
        print(f"Skill: {name}")
        print(f"Triggers: {gen.generate(name, source)}\n")
