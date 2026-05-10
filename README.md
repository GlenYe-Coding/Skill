# XiaoYe Agent Skills 集合

这个仓库包含 XiaoYe 项目开发中常用的 Agent Skills，以及自定义的 Skill 编排器。

## 🎯 核心组件

### 🤖 Skill Orchestrator（智能编排器）
- **skill-orchestrator** - 在每次对话前自动识别和调度需要的 skills
- **作用**：智能分析用户请求，制定 skill 调用计划，按最优策略执行
- **位置**：`skill-orchestrator/SKILL.md`

## 📦 包含的 Skills

### 🔧 核心开发
- **requesting-code-review** - 代码审查
- **refactor** - 代码重构
- **systematic-debugging** - 系统调试

### 💻 语言特定
- **java-springboot** - Spring Boot 最佳实践
- **python-design-patterns** - Python 设计模式

### 📝 文档与可视化
- **documentation-writer** - 技术文档编写
- **mermaid-diagrams** - Mermaid 图表绘制

### 🧪 测试
- **webapp-testing** - Web 应用测试

### 🏗️ 架构
- **improve-codebase-architecture** - 架构改进

### 🔍 工具与编排
- **find-skills** - 技能发现与安装
- **skill-orchestrator** - 智能技能编排器（本地开发）

## 🚀 使用方法

### Skill Orchestrator 工作流程

每次对话开始时，skill-orchestrator 会自动执行：

1. **意图分析** → 理解用户需求和任务类型
2. **Skill 匹配** → 从可用 skills 中找出相关技能
3. **执行规划** → 制定调用顺序和依赖关系
4. **智能调度** → 按最优策略调用 skills
5. **结果整合** → 将各 skill 输出整合为完整响应

### 直接使用 Skills

这些 skills 可以直接在支持 Agent Skills 的环境中使用。

## 📋 更新日志

- **2026-05-10**: 
  - 新增 `skill-orchestrator` - 智能技能编排器
  - 移除旧的 `skill-discovery`（已升级为 orchestrator）
  - 完善 skill 调用流程和执行策略
- **2026-05-10**: 初始版本，包含常用开发 skills
