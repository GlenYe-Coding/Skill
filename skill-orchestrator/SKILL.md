---
name: skill-orchestrator
description: >
  Enterprise-grade skill orchestrator. Automatically analyzes user requests, checks for 'find-skills' availability, 
  updates the skills database weekly, matches required skills, and executes them in optimal order. 
  Includes auto-installation, intent recognition, and cross-model compatibility.
  Triggers: "每次对话前", "技能编排", "自动安装", "skill调度", "find-skills检查".
  IMPORTANT: When triggered, ALWAYS execute `python scripts/run.py "user_request"` first to get intelligent recommendations.
---

# Skill Orchestrator - 企业级智能技能编排器

## 🎯 核心职责 (Core Responsibilities)

**在每次对话开始时，必须严格按以下顺序执行：**

1. **环境前置检查** → 确保 `find-skills` 可用且 `skills_database.json` 为最新
2. **意图分析与匹配** → 分析用户请求，从数据库中匹配最合适的 skills
3. **自动安装与执行** → 处理缺失的 skills，并按计划执行

---

## ⚡ 快速执行流程（必读）

### 【步骤 1】环境前置检查

```bash
# 1.1 检查 find-skills 是否安装
npx skills --version

# 如果失败 → 提示用户安装: npm install -g @anthropic-ai/skills

# 1.2 检查 skills_database.json 是否需要更新
# 读取 config/skills_database.json 中的 metadata.last_updated
# 如果超过 7 天 → 调用周更流程（见下方【步骤 4】）
```

### 【步骤 2】意图分析与匹配

**优先使用 Python 脚本进行智能匹配：**
```bash
python scripts/run.py "<用户请求>"
```

该脚本会自动：
- ✅ 提取意图（动作/目标/技术栈）
- ✅ 同义词扩展（提高召回率）
- ✅ 倒排索引匹配（毫秒级响应）
- ✅ 按优先级排序（P0 > P1 > P2）
- ✅ 提示安装缺失的 skills

**如果无法执行脚本，手动匹配：**
1. 分析用户请求的动作（创建/审查/调试）、目标（项目/代码/API）和技术栈（Java/Python等）
2. 在 `config/skills_database.json` 中查找匹配的 skills（优先匹配 P0/P1 级）
3. 如果未找到 → 调用 `npx skills find <关键词>` 搜索

### 【步骤 3】执行与安装

1. **检查安装状态**：对于匹配到的 skills，确认其是否已安装
2. **处理未安装 Skills**：
   ```bash
   npx skills add [source]@[name] -g -y
   ```
3. **执行 Skills**：按优先级顺序调用匹配的 skills 处理用户请求
4. **整合结果**：将各 skill 的输出整合为最终响应

### 【步骤 4】周更流程（数据库更新）

当触发数据库更新时执行：
```bash
python scripts/weekly_updater.py
```

该脚本会：
- 🔄 从 GitHub 抓取热门 skills（anthropics/skills, vercel-labs/agent-skills 等）
- 🧹 过滤低质量 skills（安装数 < 100 或评分过低）
- 💾 增量合并到本地数据库（保留已安装状态）
- 📊 生成更新报告到 output/ 目录

---

## 📋 决策速查表（快速参考）

**用户请求包含... → 优先调用...**

| 关键词 | Skill | 优先级 |
|--------|-------|--------|
| "创建 skill" | `create-skill` | P0 |
| "查找/安装" | `find-skills` | P0 |
| "审查/review" | `code-review-and-quality` | P0 |
| "bug/错误/调试" | `systematic-debugging` | P0 |
| "重构/优化" | `refactor` | P0 |
| "Java/Spring" | `java-springboot` | P1 |
| "Python" | `python-design-patterns` | P1 |
| "架构" | `improve-codebase-architecture` | P1 |
| "图表/可视化" | `mermaid-diagrams` | P1 |
| "文档" | `documentation-writer` | P2 |
| "测试" | `webapp-testing` | P2 |

---

## ✅ 执行原则（必须遵守）

### 必须做：
- ✅ 每次对话前执行 skill 分析
- ✅ 至少调用一个匹配的 skill（如果有）
- ✅ 记录执行日志
- ✅ 向用户展示执行计划

### 不要做：
- ❌ 跳过 skill 检查（除非是纯聊天）
- ❌ 调用不相关的 skills
- ❌ 忽略 skill 执行失败
- ❌ 隐藏执行过程（用户要求时除外）

---

## 💡 跨模型兼容说明

*   **本地增强模式**：如果当前环境支持 Python，请优先调用 `python scripts/run.py "<用户请求>"` 以获得最佳的意图匹配和自动化体验。
*   **通用回退模式**：如果无法执行脚本，请严格遵循上述【步骤 1】至【步骤 3】的手动指令，利用 `npx skills` 完成编排任务。

---

## 🛠️ 常用命令速查

### 智能匹配引擎
```bash
python scripts/run.py "<用户请求>"
```

### 测试套件
```bash
python scripts/test_orchestrator.py
```

### 数据库更新
```bash
python scripts/weekly_updater.py
```

### Skill 安装管理
```bash
# 检查 skill 状态
python scripts/skill_installer.py --check <skill-name>

# 安装缺失的 skills
python scripts/skill_installer.py --install-all-missing --auto-confirm
```

---

**最后更新：** 2026-05-10  
**版本：** v3.0 (Optimized Edition)  
**维护者：** XiaoYe Team
