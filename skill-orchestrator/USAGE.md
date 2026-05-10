# Skill Orchestrator 使用指南

## 概述

`skill-orchestrator` 是一个智能技能编排器，在每次对话开始时自动分析用户请求，识别需要调用的 skills，并制定最优执行计划。

## 工作原理

```
用户请求 → 意图分析 → Skill 匹配 → 执行规划 → 智能调度 → 结果整合 → 最终响应
```

## 核心功能

### 1. 意图分析

自动识别：
- 任务类型（创建/调试/重构/审查等）
- 技术领域（Java/Python/Web等）
- 复杂度评估（1-5星）
- 紧急程度

### 2. Skill 匹配

基于以下维度评分：
- 关键词匹配（40%权重）
- 语义相似度（30%权重）
- 历史使用频率（20%权重）
- 用户偏好（10%权重）

### 3. 执行策略

#### 串行执行
适用于有依赖关系的 tasks：
```
java-springboot → create-skill → documentation-writer
```

#### 并行执行
适用于独立 tasks：
```
code-review-and-quality (性能) + code-review-and-quality (安全)
```

#### 条件执行
根据中间结果决策：
```
systematic-debugging → 判断问题类型 → 选择修复方案
```

## 使用示例

### 示例 1：创建 Skill

**用户请求：**
```
帮我创建一个 Python 设计模式的 skill
```

**Orchestrator 分析：**
```markdown
## 🎯 任务分析
**用户请求：** 帮我创建一个 Python 设计模式的 skill
**任务类型：** Skill 创建
**复杂度评估：** ⭐⭐⭐

## 📋 Skill 调用计划
| 优先级 | Skill 名称 | 调用方式 | 预期作用 |
|--------|-----------|---------|---------|
| P0 | python-design-patterns | 第1步 | 获取设计模式最佳实践 |
| P0 | create-skill | 第2步 | 创建 skill 框架 |

## 🚀 执行过程
[调用 python-design-patterns]
[调用 create-skill]

✅ Skill 创建完成！
```

### 示例 2：复杂重构

**用户请求：**
```
帮我重构这个 Java 微服务项目，优化架构，然后写一份技术文档
```

**Orchestrator 分析：**
```markdown
## 🎯 任务分析
**用户请求：** 重构 Java 微服务项目
**任务类型：** 重构 + 架构优化 + 文档
**复杂度评估：** ⭐⭐⭐⭐⭐

## 📋 Skill 调用计划
**阶段1 - 分析与规划：**
1. java-springboot → 获取微服务最佳实践
2. improve-codebase-architecture → 分析架构问题

**阶段2 - 重构实施：**
3. refactor → 执行代码重构

**阶段3 - 文档与审查：**
4. documentation-writer → 编写技术文档
5. code-review-and-quality → 质量审查

## 🚀 执行过程
[阶段1执行...]
[阶段2执行...]
[阶段3执行...]

✅ 全部完成！
```

### 示例 3：调试问题

**用户请求：**
```
我的 Spring Boot 应用启动报错，帮我看看
```

**Orchestrator 分析：**
```markdown
## 🎯 任务分析
**用户请求：** Spring Boot 启动错误
**任务类型：** 调试
**紧急程度：** 高

## 📋 Skill 调用计划
1. systematic-debugging → 定位问题
   ↓
2. 根据错误类型：
   ├─ 配置错误 → java-springboot
   ├─ 依赖冲突 → find-skills
   └─ 代码错误 → refactor

## 🚀 执行过程
[调用 systematic-debugging]
诊断：数据库配置缺失

[调用 java-springboot]
解决方案：添加 spring.datasource.* 配置

✅ 问题已解决！
```

## 配置选项

你可以在 `.lingma/config.yml` 中配置 orchestrator 的行为：

```yaml
skill_orchestrator:
  # 是否显示执行计划
  show_execution_plan: true
  
  # 是否显示执行过程
  show_execution_progress: false
  
  # 最大并行 skill 数量
  max_parallel_skills: 3
  
  # 单个 skill 超时时间（秒）
  skill_timeout: 30
  
  # 是否启用缓存
  enable_cache: true
  
  # 最小匹配分数阈值
  min_match_score: 50
```

## 优先级规则

| 优先级 | 说明 | 示例 |
|--------|------|------|
| **P0** | 必须调用 | "创建 skill" → `create-skill` |
| **P1** | 强烈建议 | "代码审查" → `code-review-and-quality` |
| **P2** | 可选调用 | "优化代码" → `refactor` |
| **P3** | 仅供参考 | "项目文档" → `documentation-writer` |

## 冲突解决

当多个 skills 产生冲突时：

1. **优先级规则**：P0 > P1 > P2 > P3
2. **投票机制**：3+ skills 相同建议 → 采纳
3. **融合策略**：提取共同点，保留互补建议

## 异常处理

| 情况 | 处理方式 |
|------|---------|
| Skill 不存在 | 记录日志，跳过，继续执行其他 skills |
| Skill 执行超时 | 中断该 skill，使用回退方案 |
| Skill 输出为空 | 重试一次，仍失败则标记为"不可用" |
| Skills 矛盾 | 启动冲突解决机制，必要时询问用户 |

## 性能优化

### 缓存机制
- Skill 匹配结果缓存（5分钟）
- Skill 执行结果缓存（根据内容类型）
- 用户偏好持久化存储

### 预加载策略
- 预加载常用 skills 描述
- 建立关键词索引
- 首次匹配速度提升 80%

### 并行优化
- 无依赖 skills 同时调用
- 异步调用减少等待时间
- 合理超时设置（默认 30秒）

## 监控与反馈

### 执行日志示例

```json
{
  "timestamp": "2026-05-10T10:30:00Z",
  "user_request": "帮我创建一个 skill",
  "matched_skills": [
    {"name": "create-skill", "priority": "P0", "score": 95},
    {"name": "documentation-writer", "priority": "P2", "score": 60}
  ],
  "execution_order": ["create-skill", "documentation-writer"],
  "execution_time_ms": 15234,
  "success_rate": 1.0,
  "errors": []
}
```

### 持续改进

**每周分析：**
- 哪些 skills 最常被调用？
- 哪些匹配是错误的？
- 用户对哪些 skill 组合满意？
- 执行时间是否可以优化？

**每月更新：**
- 调整匹配权重
- 优化执行策略
- 添加新的触发关键词
- 删除低效的 skills

## 最佳实践

### ✅ 推荐做法

1. **清晰表达需求**：越具体的请求，匹配越准确
2. **提供上下文**：包括技术栈、项目背景等
3. **指定优先级**：如果有特殊要求，明确说明
4. **反馈执行结果**：帮助优化匹配算法

### ❌ 避免做法

1. **模糊请求**："帮我做点什么"（无法匹配）
2. **矛盾要求**："既要快又要好还要便宜"（难以决策）
3. **频繁变更**：执行中途改变需求（影响效率）

## 常见问题

### Q1: 为什么有时候没有调用任何 skill？

**A:** 可能的原因：
- 请求是纯聊天或知识问答
- 没有匹配的 skills（分数低于阈值）
- 用户明确要求不使用 skills

### Q2: 可以手动指定使用哪些 skills 吗？

**A:** 可以！在请求中明确提到 skill 名称：
```
请使用 create-skill 和 java-springboot 来帮我...
```

### Q3: 如何查看执行详情？

**A:** 在配置中启用：
```yaml
show_execution_progress: true
```

### Q4: 执行太慢怎么办？

**A:** 优化建议：
- 减少并行 skill 数量
- 降低超时时间
- 启用缓存
- 简化请求（分解为多个小任务）

## 未来规划

- [ ] 支持自定义匹配算法
- [ ] 添加 skill 推荐引擎
- [ ] 实现自适应学习
- [ ] 提供可视化执行流程图
- [ ] 支持多语言 orchestration

---

**最后更新：** 2026-05-10  
**版本：** v1.0  
**维护者：** XiaoYe Team
