#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自更新管理器 (Self Updater)
监控 GitHub 仓库并自动拉取最新版本。
"""

import os
import json
import subprocess
import urllib.request
from datetime import datetime, timezone, timedelta

class SelfUpdater:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), "..", "config", "orchestrator_config.json")
        self.config = self._load_config()
        self.repo_url = self.config.get("github_repo", "")
        self.last_check_file = os.path.join(os.path.dirname(__file__), "..", "logs", "last_self_check.json")

    def _load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"github_repo": ""}

    def should_update(self):
        """判断是否需要更新（每天检查一次）"""
        if not self.repo_url:
            return False

        last_check = None
        if os.path.exists(self.last_check_file):
            with open(self.last_check_file, 'r') as f:
                try:
                    data = json.load(f)
                    last_check = datetime.fromisoformat(data.get("last_check"))
                except:
                    pass

        # 如果超过 24 小时未检查，则执行检查
        if not last_check or (datetime.now() - last_check) > timedelta(hours=24):
            return True
        return False

    def check_and_update(self):
        """执行更新检查"""
        if not self.should_update():
            return

        print("🔄 正在检查 skill-orchestrator 自身更新...")
        
        try:
            # 获取 GitHub 最新提交时间
            api_url = f"https://api.github.com/repos/{self.repo_url}/commits?per_page=1"
            req = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github.v3+json"})
            with urllib.request.urlopen(req, timeout=10) as response:
                commits = json.loads(response.read().decode('utf-8'))
                if commits:
                    remote_date_str = commits[0]['commit']['committer']['date']
                    remote_date = datetime.fromisoformat(remote_date_str.replace('Z', '+00:00'))
                    
                    # 获取本地最后更新时间（简单起见，这里对比文件修改时间或记录在 config 中）
                    # 此处简化逻辑：直接尝试 git pull
                    if self._has_git():
                        print("⏳ 发现新版本，正在执行 git pull...")
                        result = subprocess.run(["git", "pull"], capture_output=True, text=True)
                        if result.returncode == 0:
                            if "Already up to date" in result.stdout:
                                print("✅ 当前已是最新版本")
                            else:
                                print("✅ 更新成功！请重启 orchestrator 以应用更改。")
                        else:
                            print(f"⚠️  更新失败: {result.stderr}")
            
            # 记录本次检查时间
            os.makedirs(os.path.dirname(self.last_check_file), exist_ok=True)
            with open(self.last_check_file, 'w') as f:
                json.dump({"last_check": datetime.now().isoformat()}, f)

        except Exception as e:
            print(f"⚠️  自更新检查出错: {e}")

    def _has_git(self):
        """检查是否安装了 git"""
        try:
            subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except:
            return False
