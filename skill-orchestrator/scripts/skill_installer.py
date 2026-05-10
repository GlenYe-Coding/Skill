#!/usr/bin/env python3
"""
Skill 自动安装器

功能：
1. 检查 skill 是否已安装
2. 自动查找和安装缺失的 skills
3. 批量安装推荐 skills
4. 验证安装结果

用法：
    python scripts/skill_installer.py --check api-security
    python scripts/skill_installer.py --install api-security
    python scripts/skill_installer.py --install-all-missing
    python scripts/skill_installer.py --list-available
"""

import json
import os
import sys
import subprocess
from typing import List, Dict, Optional
from datetime import datetime

class SkillInstaller:
    """Skill 自动安装器"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "..", "config", "skills_database.json"
        )
        self.skills_db = self._load_skills_database()
        self.install_log = []
        
    def _load_skills_database(self) -> Dict:
        """加载 skills 数据库"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"Error: Config file not found: {self.config_path}")
            sys.exit(1)
    
    def get_all_skills(self) -> List[Dict]:
        """获取所有 skills"""
        all_skills = []
        for category, skills in self.skills_db["skills_database"].items():
            all_skills.extend(skills)
        return all_skills
    
    def get_installed_skills(self) -> List[Dict]:
        """获取已安装的 skills"""
        return [s for s in self.get_all_skills() if s.get("installed", False)]
    
    def get_missing_skills(self) -> List[Dict]:
        """获取未安装的 skills"""
        return [s for s in self.get_all_skills() if not s.get("installed", False)]
    
    def find_skill_by_name(self, name: str) -> Optional[Dict]:
        """根据名称查找 skill"""
        for skill in self.get_all_skills():
            if skill["name"] == name:
                return skill
        return None
    
    def check_skill_installed(self, skill_name: str) -> bool:
        """检查 skill 是否已安装"""
        skill = self.find_skill_by_name(skill_name)
        if skill:
            return skill.get("installed", False)
        return False
    
    def install_skill(self, skill_name: str, auto_confirm: bool = False) -> bool:
        """
        安装指定的 skill
        
        Args:
            skill_name: skill 名称
            auto_confirm: 是否自动确认
            
        Returns:
            是否安装成功
        """
        skill = self.find_skill_by_name(skill_name)
        
        if not skill:
            print(f"❌ 错误: 找不到 skill '{skill_name}'")
            return False
        
        if skill.get("installed", False):
            print(f"✅ Skill '{skill_name}' 已安装")
            return True
        
        # 获取安装命令
        install_command = skill.get("install_command")
        if not install_command:
            # 如果没有预定义命令，尝试构造
            source = skill.get("source", "")
            if source and source != "builtin":
                install_command = f"npx skills add {source}@{skill_name} -g -y"
            else:
                print(f"⚠️  Skill '{skill_name}' 没有安装命令")
                return False
        
        print(f"\n📦 准备安装 skill: {skill_name}")
        print(f"   描述: {skill['description']}")
        print(f"   来源: {skill.get('source', 'unknown')}")
        print(f"   命令: {install_command}")
        
        # 询问用户确认
        if not auto_confirm:
            confirm = input("\n是否继续安装? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 取消安装")
                return False
        
        # 执行安装
        print(f"\n🔧 正在安装...")
        try:
            result = subprocess.run(
                install_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120  # 2分钟超时
            )
            
            if result.returncode == 0:
                print(f"✅ Skill '{skill_name}' 安装成功!")
                
                # 更新数据库
                skill["installed"] = True
                self._save_skills_database()
                
                # 记录日志
                self.install_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "skill": skill_name,
                    "action": "install",
                    "status": "success"
                })
                
                return True
            else:
                print(f"❌ 安装失败:")
                print(f"   stdout: {result.stdout}")
                print(f"   stderr: {result.stderr}")
                
                self.install_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "skill": skill_name,
                    "action": "install",
                    "status": "failed",
                    "error": result.stderr
                })
                
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ 安装超时 (>120秒)")
            return False
        except Exception as e:
            print(f"❌ 安装异常: {str(e)}")
            return False
    
    def install_all_missing(self, auto_confirm: bool = False) -> Dict:
        """
        安装所有缺失的 skills
        
        Returns:
            安装结果统计
        """
        missing_skills = self.get_missing_skills()
        
        if not missing_skills:
            print("✅ 所有 skills 都已安装")
            return {"total": 0, "success": 0, "failed": 0}
        
        print(f"\n📋 发现 {len(missing_skills)} 个未安装的 skills:\n")
        for i, skill in enumerate(missing_skills, 1):
            print(f"{i}. {skill['name']} - {skill['description']}")
        
        if not auto_confirm:
            confirm = input("\n是否全部安装? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 取消批量安装")
                return {"total": len(missing_skills), "success": 0, "failed": 0}
        
        # 批量安装
        stats = {"total": len(missing_skills), "success": 0, "failed": 0}
        
        for skill in missing_skills:
            print(f"\n{'='*60}")
            if self.install_skill(skill["name"], auto_confirm=True):
                stats["success"] += 1
            else:
                stats["failed"] += 1
        
        # 打印总结
        print(f"\n{'='*60}")
        print(f"📊 安装总结:")
        print(f"   总数: {stats['total']}")
        print(f"   成功: {stats['success']} ✅")
        print(f"   失败: {stats['failed']} ❌")
        
        return stats
    
    def list_available_skills(self, category: str = None):
        """列出可用的 skills"""
        if category:
            skills = self.skills_db["skills_database"].get(category, [])
            print(f"\n📂 Category: {category}\n")
        else:
            skills = self.get_all_skills()
            print(f"\n📚 所有可用 Skills\n")
        
        print(f"{'Name':<35} {'Priority':<10} {'Installed':<12} {'Description'}")
        print("-" * 100)
        
        for skill in skills:
            installed_mark = "✅ Yes" if skill.get("installed") else "❌ No"
            print(f"{skill['name']:<35} {skill['priority']:<10} {installed_mark:<12} {skill['description']}")
        
        print()
    
    def search_skills(self, keyword: str) -> List[Dict]:
        """搜索 skills"""
        keyword_lower = keyword.lower()
        results = []
        
        for skill in self.get_all_skills():
            if (keyword_lower in skill["name"].lower() or
                keyword_lower in skill["description"].lower() or
                any(keyword_lower in t.lower() for t in skill.get("triggers", []))):
                results.append(skill)
        
        return results
    
    def _save_skills_database(self):
        """保存 skills 数据库"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.skills_db, f, ensure_ascii=False, indent=2)
    
    def save_install_log(self):
        """保存安装日志"""
        if self.install_log:
            log_dir = os.path.join(os.path.dirname(__file__), "..", "output")
            os.makedirs(log_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(log_dir, f"install_log_{timestamp}.json")
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(self.install_log, f, ensure_ascii=False, indent=2)
            
            print(f"\n📝 安装日志已保存到: {log_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Skill 自动安装器")
    parser.add_argument(
        "--check",
        metavar="SKILL_NAME",
        help="检查 skill 是否已安装"
    )
    parser.add_argument(
        "--install",
        metavar="SKILL_NAME",
        help="安装指定的 skill"
    )
    parser.add_argument(
        "--install-all-missing",
        action="store_true",
        help="安装所有缺失的 skills"
    )
    parser.add_argument(
        "--list",
        type=str,
        nargs='?',
        default=None,
        metavar="CATEGORY",
        help="列出 skills（可选指定分类）"
    )
    parser.add_argument(
        "--search",
        metavar="KEYWORD",
        help="搜索 skills"
    )
    parser.add_argument(
        "--auto-confirm",
        action="store_true",
        help="自动确认（无需交互）"
    )
    
    args = parser.parse_args()
    
    installer = SkillInstaller()
    
    if args.check:
        installed = installer.check_skill_installed(args.check)
        status = "✅ 已安装" if installed else "❌ 未安装"
        print(f"{args.check}: {status}")
        
    elif args.install:
        installer.install_skill(args.install, auto_confirm=args.auto_confirm)
        
    elif args.install_all_missing:
        installer.install_all_missing(auto_confirm=args.auto_confirm)
        
    elif args.list is not None:
        installer.list_available_skills(args.list if args.list else None)
        
    elif args.search:
        results = installer.search_skills(args.search)
        if results:
            print(f"\n🔍 找到 {len(results)} 个匹配的 skills:\n")
            for skill in results:
                print(f"- {skill['name']}: {skill['description']}")
        else:
            print(f"\n❌ 未找到匹配 '{args.search}' 的 skills")
    
    else:
        parser.print_help()
    
    # 保存安装日志
    installer.save_install_log()


if __name__ == "__main__":
    main()
