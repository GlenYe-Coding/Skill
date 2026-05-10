# Skill Orchestrator - 企业级智能技能编排器 🚀

**Skill Orchestrator** 是一个专为 AI 助手设计的智能调度系统。它在每次对话开始前自动分析用户意图，精准匹配并调度所需的 Skills，确保你的 AI 工作流始终处于最佳状态。

---

## ✨ 核心特性

- **🧠 智能意图识别**：基于 `jieba` 分词和正则匹配，精准识别“创建”、“审查”、“调试”等开发动作及技术栈。
- **⚡ 毫秒级匹配引擎**：采用倒排索引（Inverted Index）与同义词扩展算法，在海量 Skills 库中实现快速召回。
- **🔄 自进化数据库**：内置周更机制，自动从 GitHub 热门仓库抓取最新 Skills，保持知识库与时俱进。
- **🌍 跨模型兼容**：遵循 Anthropic 标准格式，完美适配 Lingma、Cursor、Claude Code 等主流 AI 平台。
- **🛠️ 零配置启动**：提供一键安装脚本，自动检测 Python/Node.js 环境并处理依赖。

---

## 📦 快速开始

### 1. 环境要求
- Python 3.7+
- Node.js (用于 `npx skills` 功能)

### 2. 一键安装
根据你的操作系统运行以下脚本：

```bash
# Windows
install.bat

# Linux / macOS
chmod +x install.sh && ./install.sh
```

### 3. 运行测试
```bash
python scripts/run.py "帮我创建一个 Java Spring Boot 项目"
```

---

## 🏗️ 架构概览

Skill Orchestrator 采用模块化设计，主要包含以下核心组件：

| 模块 | 描述 |
| :--- | :--- |
| **IntentExtractor** | 意图提取器，负责从自然语言中提取动作、目标和技术栈。 |
| **KeywordMatcher** | 关键词匹配器，基于倒排索引实现高效的技能检索。 |
| **SynonymExpander** | 同义词扩展器，通过映射表提高模糊搜索的召回率。 |
| **WeeklyUpdater** | 自动更新器，定期从 GitHub API 同步热门技能数据。 |

---

## 💡 使用场景

### 场景 A：本地开发增强
在终端直接调用，获取技能推荐并自动安装：
```bash
$ python scripts/run.py "如何优化 React 应用的性能？"
📋 推荐 Skills:
  1. [P1] ❌ react-best-practices (评分: 80)
     💡 该技能尚未安装。是否立即安装? (y/n): y
```

### 场景 B：AI 助手集成
将 `SKILL.md` 放置在 `.lingma/skills/` 或 Cursor 的配置目录中。AI 将在每次对话前自动执行前置检查，确保拥有完成任务所需的所有工具。

---

## 🤝 贡献指南

我们欢迎任何形式的贡献！
1. **Fork** 本仓库。
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)。
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)。
4. 推送到分支 (`git push origin feature/AmazingFeature`)。
5. 开启一个 **Pull Request**。

---

## 📄 许可证

本项目遵循 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。
