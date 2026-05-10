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
        """执行更新检查（基于 Git 本地提交时间对比）"""
        if not self.should_update():
            return

        # print("🔄 正在检查 skill-orchestrator 自身更新...") # 静默检查
        
        try:
            # 1. 获取 GitHub 最新提交时间
            api_url = f"https://api.github.com/repos/{self.repo_url}/commits?per_page=1"
            req = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github.v3+json"})
            with urllib.request.urlopen(req, timeout=10) as response:
                commits = json.loads(response.read().decode('utf-8'))
                if commits:
                    remote_date_str = commits[0]['commit']['committer']['date']
                    remote_date = datetime.fromisoformat(remote_date_str.replace('Z', '+00:00'))
                    
                    # 2. 获取本地 Git 仓库的最新提交时间
                    local_date = self._get_local_git_time()
                    
                    # 3. 对比时间戳
                    if local_date and remote_date > local_date:
                        print(f"\n⏳ [AUTO-UPDATE] 发现新版本 (远程: {remote_date.strftime('%m-%d %H:%M')} | 本地: {local_date.strftime('%m-%d %H:%M')})")
                        if self._has_git():
                            result = subprocess.run(["git", "pull"], capture_output=True, text=True)
                            if result.returncode == 0:
                                print("✅ [AUTO-UPDATE] 更新成功！请重启 orchestrator 以应用更改。")
                                self._update_local_version(remote_date_str)
                            else:
                                print(f"⚠️  [AUTO-UPDATE] Git pull 失败: {result.stderr}")
                    else:
                        # 已是最新版，完全静默
                        self._record_check_time()

        except urllib.error.HTTPError as e:
            if e.code == 403:
                pass # 静默跳过限流
            else:
                print(f"\n⚠️  [AUTO-UPDATE] 检查出错: {e}")
        except Exception as e:
            print(f"\n⚠️  [AUTO-UPDATE] 检查出错: {e}")

    def _get_local_git_time(self):
        """获取本地 Git 仓库最新一次提交的时间"""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ci"], 
                capture_output=True, text=True, check=True
            )
            time_str = result.stdout.strip()
            # Git 输出格式如: 2026-05-10 07:00:00 +0000
            # 转换为 datetime 对象
            return datetime.strptime(time_str[:19], "%Y-%m-%d %H:%M:%S")
        except:
            return None

    def _update_local_version(self, version_time_str):
        """更新本地记录的版本时间和最后更新时间"""
        self.config["last_version_time"] = version_time_str
        # 记录本次执行更新的时间点
        self.config["last_update_time"] = datetime.now().isoformat()
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        self._record_check_time()

    def _record_check_time(self):
        """记录本次 API 检查时间（用于限流控制）"""
        os.makedirs(os.path.dirname(self.last_check_file), exist_ok=True)
        with open(self.last_check_file, 'w') as f:
            json.dump({"last_check": datetime.now().isoformat()}, f)

    def _has_git(self):
        """检查是否安装了 git"""
        try:
            subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except:
            return False
