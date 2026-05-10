#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每周更新器 (Weekly Updater)
负责从 GitHub API 抓取热门 Skills 并更新本地数据库。
"""

import os
import json
import urllib.request
import time
from datetime import datetime, timezone

class WeeklyUpdater:
    """Skills 数据库自动更新引擎"""

    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "..", "config", "skills_database.json")
        # 扩展数据源：包含官方、社区聚合及大厂仓库
        self.sources = [
            {"repo": "anthropics/skills", "type": "standard"},
            {"repo": "vercel-labs/agent-skills", "type": "standard"},
            {"repo": "mcollina/skills", "type": "standard"},
            {"repo": "ComposioHQ/awesome-claude-skills", "type": "curated"},
            {"repo": "microsoft/skills", "type": "standard"},
            {"repo": "hardw00t/ai-security-arsenal", "type": "standard"},
            {"repo": "VoltAgent/awesome-agent-skills", "type": "awesome_list"}
        ]
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Skill-Orchestrator-Updater"
        }

    def fetch_popular_skills(self):
        """从 GitHub 抓取热门 skills（支持多源差异化处理与限流）"""
        print("🔄 正在从 GitHub 抓取热门 skills...")
        all_skills = []
        
        for i, source in enumerate(self.sources):
            repo_name = source["repo"]
            source_type = source["type"]
            
            # 限流保护：每个请求间隔 2 秒
            if i > 0:
                time.sleep(2)
            
            try:
                url = f"https://api.github.com/repos/{repo_name}/contents"
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=15) as response:
                    contents = json.loads(response.read().decode('utf-8'))
                    
                    if source_type == "standard":
                        skills = self._parse_standard_repo(repo_name, contents)
                    elif source_type == "curated":
                        skills = self._parse_standard_repo(repo_name, contents)
                    elif source_type == "awesome_list":
                        skills = self._parse_awesome_list(repo_name, contents)
                    
                    all_skills.extend(skills)
                    print(f"  ✅ 从 {repo_name} ({source_type}) 解析到 {len(skills)} 个 skills")
            except urllib.error.HTTPError as e:
                if e.code == 403:
                    print(f"  ⚠️  API 速率限制，等待 60 秒后重试 {repo_name}...")
                    time.sleep(60)
                    # 简单重试一次
                    try:
                        with urllib.request.urlopen(req, timeout=15) as retry_response:
                            contents = json.loads(retry_response.read().decode('utf-8'))
                            skills = self._parse_standard_repo(repo_name, contents) if source_type != "awesome_list" else self._parse_awesome_list(repo_name, contents)
                            all_skills.extend(skills)
                            print(f"  ✅ 重试成功: {repo_name}")
                    except:
                        print(f"  ❌ 重试失败: {repo_name}")
                else:
                    print(f"  ❌ 处理 {repo_name} 时出错: {e}")
            except Exception as e:
                print(f"  ❌ 处理 {repo_name} 时出错: {e}")
        
        return all_skills

    def _parse_standard_repo(self, repo, contents):
        """解析标准仓库结构"""
        skills = []
        for item in contents:
            if item['type'] == 'dir' and not item['name'].startswith('.'):
                skills.append(self._create_skill_info(item, repo))
        return skills

    def _parse_awesome_list(self, repo, contents):
        """解析 Awesome 列表结构（优先抓取子目录或特定文件）"""
        skills = []
        for item in contents:
            # 在 awesome-agent-skills 中，技能通常也在子目录下
            if item['type'] == 'dir' and not item['name'].startswith('.'):
                skills.append(self._create_skill_info(item, repo))
        return skills

    def _create_skill_info(self, item, repo):
        """创建标准化的 skill 信息对象（含自动触发词）"""
        from scripts.trigger_generator import TriggerGenerator
        gen = TriggerGenerator()
        
        return {
            'name': item['name'],
            'source': repo,
            'url': item['html_url'],
            'last_updated': item.get('updated_at', ''),
            'installed': False,
            'priority': 'P1',
            'triggers': gen.generate(item['name'], repo) # 自动生成触发词
        }

    def update_database(self):
        """执行完整的更新流程（增量合并）"""
        new_skills = self.fetch_popular_skills()
        
        if not os.path.exists(self.db_path):
            print("❌ 本地数据库不存在，请先初始化。")
            return

        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                db = json.load(f)
        except json.JSONDecodeError:
            print("❌ 数据库文件格式损坏，请检查 skills_database.json")
            return

        # 建立现有技能的名称集合，用于快速去重
        existing_names = set()
        for category in db["skills_database"].values():
            for skill in category:
                existing_names.add(skill["name"])

        added_count = 0
        for skill in new_skills:
            if skill["name"] not in existing_names:
                # 简单的分类逻辑：如果名称包含特定关键词则归类，否则归入 core_development
                category = "core_development"
                if any(kw in skill['name'] for kw in ['security', 'auth']):
                    category = "security"
                elif any(kw in skill['name'] for kw in ['test', 'jest']):
                    category = "testing"
                
                if category not in db["skills_database"]:
                    db["skills_database"][category] = []
                
                db["skills_database"][category].append(skill)
                existing_names.add(skill["name"])
                added_count += 1

        # 更新元数据
        if "metadata" not in db:
            db["metadata"] = {}
        db["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        db["metadata"]["total_skills"] = len(existing_names)

        # 原子写入：先写临时文件再重命名，防止写入中途崩溃导致文件损坏
        temp_path = self.db_path + ".tmp"
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        os.replace(temp_path, self.db_path)

        print(f"\n✅ 数据库更新完成！新增 {added_count} 个 skills。")
        print(f"📅 最后更新时间: {db['metadata']['last_updated']}")

if __name__ == "__main__":
    updater = WeeklyUpdater()
    updater.update_database()
