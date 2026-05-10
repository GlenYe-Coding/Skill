#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同义词扩展器 (Synonym Expander)
通过扩展关键词的同义词来提高技能匹配的召回率。
"""

class SynonymExpander:
    """同义词扩展引擎"""

    def __init__(self):
        # 核心开发术语同义词库
        self.synonyms = {
            '创建': ['新建', '生成', '建立', '初始化', '搭建', 'create'],
            '审查': ['检查', 'review', '审计', '评估', '检视', 'code review'],
            '修复': ['调试', '解决', '修正', 'bugfix', '排错', 'debug'],
            '优化': ['改进', '重构', '提升', 'enhance', '改善', 'refactor'],
            '测试': ['验证', 'test', '校验', '检测', 'unit test'],
            '部署': ['发布', '上线', 'deploy', 'publish', 'docker'],
            '查找': ['搜索', '寻找', 'find', '查询', '检索', 'search'],
            '项目': ['工程', '应用', '系统', 'app', 'project'],
            '代码': ['函数', '类', '模块', '脚本', 'code'],
        }

    def expand(self, keywords: list) -> list:
        """
        扩展关键词列表
        
        Args:
            keywords: 原始关键词列表
            
        Returns:
            包含原始词和同义词的去重列表
        """
        expanded_set = set(keywords)
        
        for keyword in keywords:
            # 支持中文和部分英文关键词的扩展
            if keyword in self.synonyms:
                expanded_set.update(self.synonyms[keyword])
            
            # 简单的反向映射（如果同义词在原文中出现，也能映射回主词）
            for main_word, syn_list in self.synonyms.items():
                if keyword in syn_list:
                    expanded_set.add(main_word)
        
        return list(expanded_set)

if __name__ == "__main__":
    expander = SynonymExpander()
    original = ['创建', 'java']
    print(f"原始: {original}")
    print(f"扩展后: {expander.expand(original)}")
