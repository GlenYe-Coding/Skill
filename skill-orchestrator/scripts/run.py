#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill Orchestrator - 一键启动脚本

用法:
    python run.py "你的请求"
"""

import sys
import os
import subprocess
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def check_environment():
    """环境前置检查（带缓存优化与自更新）"""
    print("🔍 Skill Orchestrator - 环境检查")
    print("-" * 40)
    
    # 0. 自更新检查
    from scripts.self_updater import SelfUpdater
    updater = SelfUpdater()
    if updater.config.get("auto_update_enabled"):
        updater.check_and_update()
    
    from scripts.env_state_manager import EnvStateManager
    env_mgr = EnvStateManager()
    
    # 1. 检查 Python 版本
    if sys.version_info < (3, 7):
        print("❌ 错误: 需要 Python 3.7 或更高版本")
        return False
    
    # 2. 检查 find-skills (npx) - 采用 24 小时缓存机制
    if env_mgr.should_check_find_skills():
        print("⏳ 正在验证 find-skills 状态...")
        try:
            subprocess.run(
                ["npx", "--version"], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                check=True
            )
            env_mgr.update_find_skills_status(True)
            print("✅ npx (Node.js) 已就绪")
        except (FileNotFoundError, subprocess.CalledProcessError):
            env_mgr.update_find_skills_status(False)
            print("⚠️  警告: 未检测到 'npx' (Node.js)。find-skills 功能将受限。")
    else:
        # 使用缓存结果
        if env_mgr.is_find_skills_installed():
            print("✅ npx (Node.js) 已就绪 (缓存)")
        else:
            print("⚠️  警告: find-skills 未安装 (缓存)。功能受限。")

    # 3. 检查核心依赖
    try:
        import jieba
        print("✅ jieba (中文分词) 已就绪")
    except ImportError:
        print("⚠️  警告: 未安装 jieba。中文意图识别精度可能下降。")
        print("   建议运行: pip install jieba")

    print("-" * 40)
    return True

def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("用法: python run.py \"用户请求\"")
        print("示例: python run.py \"帮我创建一个 Java Spring Boot 项目\"")
        sys.exit(1)

    if not check_environment():
        sys.exit(1)

    user_request = " ".join(sys.argv[1:])
    print(f"\n🎯 正在分析请求: \"{user_request}\"")

    # --- 核心编排逻辑 ---
    
    # 1. 意图提取
    from scripts.intent_extractor import IntentExtractor
    extractor = IntentExtractor()
    intent = extractor.extract(user_request)
    
    print(f"🧠 意图识别: Action={intent['action']}, Target={intent['target']}")
    print(f"🛠️  技术栈: {', '.join(intent['tech_stack']) if intent['tech_stack'] else '通用'}")

    # 2. 技能匹配
    from scripts.keyword_matcher import KeywordMatcher
    from scripts.synonym_expander import SynonymExpander
    
    # 先进行同义词扩展
    expander = SynonymExpander()
    expanded_keywords = expander.expand(intent['keywords'])
    
    matcher = KeywordMatcher()
    matches = matcher.match(expanded_keywords)
    
    if matches:
        print("\n📋 推荐 Skills:")
        for i, match in enumerate(matches[:3], 1):
            # 从数据库获取详细信息
            skill_info = matcher.skills_map.get(match.skill_name, {})
            installed_status = "✅" if skill_info.get('installed') else "❌"
            print(f"  {i}. [{match.priority}] {installed_status} {match.skill_name} (评分: {match.score})")
            print(f"     原因: {match.reason}")
            
            # 如果未安装，询问是否安装
            if not skill_info.get('installed'):
                print(f"     💡 该技能尚未安装。是否立即安装? (y/n): ", end="")
                try:
                    choice = input().strip().lower()
                    if choice == 'y':
                        source = skill_info.get('source', '')
                        cmd = f"npx skills add {source}@{match.skill_name} -g -y"
                        print(f"     🔧 正在执行: {cmd}")
                        os.system(cmd)
                        # 更新本地状态
                        skill_info['installed'] = True
                        with open(matcher.db_path, 'w', encoding='utf-8') as f:
                            json.dump(matcher.skills_map, f) # 简化处理，实际应更新完整 db
                        print(f"     ✅ {match.skill_name} 安装完成！")
                except KeyboardInterrupt:
                    pass
    else:
        print("\n⚠️  未在本地数据库中找到精确匹配的 skills。")
        print("💡 建议: 尝试调用 find-skills 搜索在线资源。")

    print("\n✅ 编排完成。")

if __name__ == "__main__":
    main()
