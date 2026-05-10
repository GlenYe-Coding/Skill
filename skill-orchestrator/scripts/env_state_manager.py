#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境状态管理器 (Environment State Manager)
负责缓存 find-skills 等外部依赖的检查结果，避免重复的系统调用。
"""

import os
import json
from datetime import datetime, timedelta

class EnvStateManager:
    def __init__(self):
        self.state_path = os.path.join(os.path.dirname(__file__), "..", "config", "env_status.json")
        self.state = self._load_state()

    def _load_state(self):
        """加载状态文件，如果不存在则初始化"""
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # 默认状态
        return {
            "find_skills": {
                "installed": False,
                "last_checked": None
            },
            "last_update_check": None
        }

    def _save_state(self):
        """保存状态到文件"""
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2)

    def should_check_find_skills(self) -> bool:
        """判断是否需要重新检查 find-skills (超过24小时或从未检查)"""
        last_checked = self.state["find_skills"].get("last_checked")
        if not last_checked:
            return True
        
        last_time = datetime.fromisoformat(last_checked)
        return datetime.now() - last_time > timedelta(hours=24)

    def is_find_skills_installed(self) -> bool:
        """获取当前缓存的安装状态"""
        return self.state["find_skills"].get("installed", False)

    def update_find_skills_status(self, is_installed: bool):
        """更新 find-skills 的状态并记录时间"""
        self.state["find_skills"]["installed"] = is_installed
        self.state["find_skills"]["last_checked"] = datetime.now().isoformat()
        self._save_state()
