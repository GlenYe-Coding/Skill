---
name: skill-orchestrator
description: 企业级智能技能编排器。在每次对话开始时自动分析用户请求，识别需要调用的 skills，制定执行计划，并按最优策略调用相关 skills。包含自动化匹配引擎、性能监控、配置管理、测试工具等企业级功能。适用于所有需要多技能协作的复杂任务场景。
---

# Skill Orchestrator - 企业级智能技能编排器

## 🏢 企业级特性

### ✨ 核心功能

1. **智能匹配引擎** (`scripts/skill_matcher.py`)
   - 基于关键词和语义相似度的多维度评分
   - 可配置的匹配规则和权重
   - 自动生成执行计划
   - 输出详细匹配报告

2. **性能监控系统** (`scripts/performance_monitor.py`)
   - 实时收集执行指标
   - 生成日/周/月性能报告
   - P50/P95/P99 延迟分析
   - 自动优化建议

3. **配置管理中心** (`config/matching_rules.json`)
   - 灵活的匹配规则配置
   - 用户偏好设置
   - 日志和监控配置
   - 热重载支持

4. **完整测试套件** (`scripts/test_orchestrator.py`)
   - 单元测试和集成测试
   - 性能基准测试
   - 回归测试
   - 自动化测试报告

5. **日志和追踪**
   - 结构化日志记录
   - 执行历史追踪
   - 错误分析和告警
   - 审计日志

6. **自动 Skill 安装** (`scripts/skill_installer.py`) ⭐ 新增
   - Skills 数据库管理（18+ skills）
   - 自动检测缺失 skills
   - 一键安装所有缺失 skills
   - 智能搜索和推荐
   - 安装历史记录

## 核心职责

在**每次对话开始时**自动执行以下流程：

1. **意图分析** → 理解用户的真实需求和任务类型
2. **Skill 匹配** → 从可用 skills 中找出相关的技能
3. **执行规划** → 制定 skill 调用顺序和依赖关系
4. **智能调度** → 按最优策略调用 skills
5. **结果整合** → 将各 skill 输出整合为完整响应

## 快速流程（每次对话必执行）

```
收到用户请求
    ↓
【第1步】意图分析
    ├─ 这是什么类型的任务？
    ├─ 涉及哪些技术领域？
    ├─ 需要什么样的输出？
    └─ 是否有特殊要求？
    ↓
【第2步】Skill 扫描
    ├─ 检查所有可用 skills
    ├─ 匹配触发关键词
    ├─ 评估相关性得分
    └─ 筛选出候选 skills
    ↓
【第3步】执行规划
    ├─ 确定调用顺序（串行/并行）
    ├─ 识别依赖关系
    ├─ 预估执行时间
    └─ 制定回退方案
    ↓
【第4步】智能调度
    ├─ 调用高优先级 skills
    ├─ 收集各 skill 输出
    ├─ 处理异常情况
    └─ 记录执行日志
    ↓
【第5步】结果整合
    ├─ 合并各 skill 输出
    ├─ 消除冲突和重复
    ├─ 生成最终响应
    └─ 提供执行摘要
```

## Skill 匹配规则

### 优先级分类

| 优先级 | 判断标准 | 示例 |
|--------|---------|------|
| **P0 - 必须调用** | 直接匹配核心需求 | "创建 skill" → `create-skill` |
| **P1 - 强烈建议** | 高度相关且能显著提升质量 | "代码审查" → `code-review-and-quality` |
| **P2 - 可选调用** | 有帮助但非必需 | "优化代码" → `refactor` |
| **P3 - 仅供参考** | 可能有用但不确定 | "项目文档" → `documentation-writer` |

### 匹配算法

```python
def match_skills(user_request, available_skills):
    """
    智能匹配算法
    """
    candidates = []
    
    for skill in available_skills:
        score = 0
        
        # 1. 关键词匹配 (权重 40%)
        if any(keyword in user_request for keyword in skill.triggers):
            score += 40
        
        # 2. 语义相似度 (权重 30%)
        semantic_score = calculate_semantic_similarity(
            user_request, 
            skill.description
        )
        score += semantic_score * 30
        
        # 3. 历史使用频率 (权重 20%)
        if skill.usage_count > 0:
            score += min(20, skill.usage_count * 2)
        
        # 4. 用户偏好 (权重 10%)
        if skill in user.preferred_skills:
            score += 10
        
        if score >= 50:  # 阈值
            candidates.append((skill, score))
    
    return sorted(candidates, key=lambda x: x[1], reverse=True)
```

## 执行策略

### 1. 串行执行（有依赖关系）

**适用场景：** 后一个 skill 需要前一个的输出

```
示例："创建一个 Spring Boot 项目并编写 API 文档"

执行顺序：
1. java-springboot → 获取项目结构和最佳实践
2. create-skill → 基于最佳实践创建项目骨架
3. documentation-writer → 基于项目结构生成文档

依赖链：
java-springboot → create-skill → documentation-writer
```

### 2. 并行执行（无依赖关系）

**适用场景：** 多个 skills 可以独立执行

```
示例："审查这段代码的性能和安全性"

并行调用：
- code-review-and-quality (性能维度)
- code-review-and-quality (安全维度)
- systematic-debugging (潜在问题检测)

合并策略：汇总各维度的审查结果
```

### 3. 条件执行（根据中间结果决策）

**适用场景：** 需要根据前序结果决定后续动作

```
示例："帮我修复这个 bug"

执行流程：
1. systematic-debugging → 定位问题根源
   ↓
2. 判断问题类型：
   ├─ 逻辑错误 → refactor (重构修复)
   ├─ 配置问题 → java-springboot (配置指导)
   └─ 依赖问题 → find-skills (查找相关库)
```

## 冲突解决机制

### 当多个 skills 产生冲突时

1. **优先级规则**
   - 用户明确指定的 skill 优先
   - P0 级 skill 优先于 P1/P2/P3
   - 最近使用的 skill 优先（上下文相关）

2. **投票机制**
   - 如果 3+ skills 给出相同建议 → 采纳
   - 如果意见分歧 → 列出各方案优缺点，让用户决策

3. **融合策略**
   - 提取各 skill 的共同点
   - 保留互补的建议
   - 标注冲突点并说明原因

## 异常处理

### Skill 调用失败

```
情况 1: Skill 不存在
→ 记录日志，跳过该 skill，继续执行其他 skills

情况 2: Skill 执行超时
→ 中断该 skill，使用默认策略或回退方案

情况 3: Skill 输出为空
→ 重试一次，仍失败则标记为"不可用"

情况 4: Skills 之间产生矛盾
→ 启动冲突解决机制，必要时询问用户
```

## 输出格式规范

### 标准响应结构

```markdown
## 🎯 任务分析

**用户请求：** [原始请求]
**任务类型：** [分类标签]
**复杂度评估：** ⭐⭐⭐ (1-5星)

## 📋 Skill 调用计划

| 优先级 | Skill 名称 | 调用方式 | 预期作用 |
|--------|-----------|---------|---------|
| P0 | create-skill | 串行第1步 | 创建 skill 框架 |
| P1 | java-springboot | 串行第2步 | 提供技术栈指导 |
| P2 | documentation-writer | 并行 | 生成配套文档 |

## 🚀 执行过程

### Step 1: create-skill
✅ 成功执行
输出：创建了 skill 基础结构

### Step 2: java-springboot  
✅ 成功执行
输出：提供了 Spring Boot 最佳实践

### Step 3: documentation-writer
✅ 成功执行
输出：生成了 API 文档草稿

## 📊 结果整合

[整合后的最终响应]

## 💡 执行摘要

- **调用 skills 数量：** 3
- **总执行时间：** ~15秒
- **成功率：** 100%
- **关键发现：** [重要洞察]
```

## 实战示例

### 示例 1：简单任务（单 skill）

**用户请求：** "帮我创建一个 Python 设计模式的 skill"

**分析过程：**
```
意图：创建 skill
领域：Python、设计模式
匹配：
- create-skill (P0) - 创建 skill 的核心工具
- python-design-patterns (P1) - 提供设计模式知识

执行计划：
1. 先调用 python-design-patterns 获取设计模式最佳实践
2. 再调用 create-skill 基于最佳实践创建 skill
```

**实际执行：**
```markdown
我检测到这个任务需要两个 skills 协作：

1. **python-design-patterns** → 获取 Python 设计模式的最佳实践
2. **create-skill** → 基于这些实践创建规范的 skill

让我开始执行...

[调用 python-design-patterns]
[调用 create-skill]

✅ Skill 创建完成！
```

### 示例 2：复杂任务（多 skill 组合）

**用户请求：** "帮我重构这个 Java 微服务项目，优化架构，然后写一份技术文档"

**分析过程：**
```
意图：重构 + 优化 + 文档
领域：Java、微服务、架构
复杂度：⭐⭐⭐⭐⭐

匹配：
- refactor (P0) - 代码重构
- improve-codebase-architecture (P0) - 架构优化
- java-springboot (P1) - Java/Spring 最佳实践
- documentation-writer (P1) - 技术文档
- code-review-and-quality (P2) - 最终质量审查

执行计划（串行+并行）：
阶段1 - 分析与规划：
  1. java-springboot → 获取微服务架构最佳实践
  2. improve-codebase-architecture → 分析当前架构问题

阶段2 - 重构实施：
  3. refactor → 执行代码重构（基于阶段1的发现）

阶段3 - 文档与审查：
  4. documentation-writer → 编写技术文档
  5. code-review-and-quality → 最终质量审查（并行执行）
```

**实际执行：**
```markdown
这是一个复杂的重构任务，我将分三个阶段执行：

## 阶段1：分析与规划
[调用 java-springboot]
[调用 improve-codebase-architecture]

发现以下架构问题：
- 模块耦合度过高
- 缺少统一异常处理
- ...

## 阶段2：重构实施
[调用 refactor]

已完成重构：
- 提取了共享模块
- 引入了统一异常处理
- ...

## 阶段3：文档与审查
[调用 documentation-writer]
[调用 code-review-and-quality]

✅ 全部完成！

## 最终交付物
1. 重构后的代码
2. 架构改进报告
3. 技术文档
4. 质量审查报告
```

### 示例 3：调试任务（条件执行）

**用户请求：** "我的 Spring Boot 应用启动报错，帮我看看"

**分析过程：**
```
意图：调试问题
领域：Spring Boot
紧急程度：高

匹配：
- systematic-debugging (P0) - 系统化调试
- java-springboot (P1) - Spring Boot 特定知识

执行计划（条件执行）：
1. systematic-debugging → 收集错误信息，定位问题
   ↓
2. 根据错误类型决策：
   ├─ 配置错误 → java-springboot (配置指导)
   ├─ 依赖冲突 → find-skills (查找兼容版本)
   └─ 代码错误 → refactor (修复代码)
```

**实际执行：**
```markdown
这是一个调试场景，我将使用系统化方法排查：

[调用 systematic-debugging]

收集到错误信息：
```
Error creating bean with name 'dataSource'
```

诊断结果：数据库配置问题

[调用 java-springboot]

根据 Spring Boot 最佳实践，问题是：
- application.yml 中缺少数据库配置
- 需要添加 spring.datasource.* 配置

✅ 问题已解决！请添加以下配置：
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: secret
```
```

## 性能优化

### 1. 缓存机制

```
缓存内容：
- Skill 匹配结果（相同请求直接复用）
- Skill 执行结果（可复用的输出）
- 用户偏好（历史选择记录）

过期策略：
- 匹配结果：5分钟
- 执行结果：根据 skill 类型（静态内容长期缓存）
- 用户偏好：持久化存储
```

### 2. 预加载策略

```
在对话开始前：
1. 预加载常用 skills 的描述信息
2. 建立关键词索引
3. 初始化匹配算法

优势：首次匹配速度提升 80%
```

### 3. 并行优化

```
最大化并行度：
- 无依赖的 skills 同时调用
- 使用异步调用减少等待时间
- 设置合理的超时时间（默认 30秒）
```

## 监控与反馈

### 执行日志

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

```
每周分析：
1. 哪些 skills 最常被调用？
2. 哪些匹配是错误的？
3. 用户对哪些 skill 组合满意？
4. 执行时间是否可以优化？

每月更新：
- 调整匹配权重
- 优化执行策略
- 添加新的触发关键词
- 删除低效的 skills
```

## 配置选项

### 用户自定义设置

```yaml
skill_orchestrator:
  # 是否显示执行计划（默认 true）
  show_execution_plan: true
  
  # 是否显示执行过程（默认 false）
  show_execution_progress: false
  
  # 最大并行 skill 数量（默认 3）
  max_parallel_skills: 3
  
  # 单个 skill 超时时间（秒，默认 30）
  skill_timeout: 30
  
  # 是否启用缓存（默认 true）
  enable_cache: true
  
  # 最小匹配分数阈值（默认 50）
  min_match_score: 50
```

## 快速参考

### 决策速查表

```
用户请求包含... → 优先调用...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"创建 skill" → create-skill
"查找/安装" → find-skills
"审查/review" → code-review-and-quality
"bug/错误/调试" → systematic-debugging
"重构/优化" → refactor
"Java/Spring" → java-springboot
"Python" → python-design-patterns
"架构" → improve-codebase-architecture
"图表/可视化" → mermaid-diagrams
"文档" → documentation-writer
"测试" → webapp-testing
```

### 执行原则

```
✅ 必须做：
- 每次对话前执行 skill 分析
- 至少调用一个匹配的 skill（如果有）
- 记录执行日志
- 向用户展示执行计划

❌ 不要做：
- 跳过 skill 检查（除非是纯聊天）
- 调用不相关的 skills
- 忽略 skill 执行失败
- 隐藏执行过程（用户要求时除外）
```

## 🛠️ 工具和脚本使用

### 1. 智能匹配引擎

```bash
# 基本用法
python scripts/skill_matcher.py "帮我创建一个 Java Spring Boot 项目"

# 输出示例
============================================================
Skill Matcher - 匹配报告
============================================================

用户请求: 帮我创建一个 Java Spring Boot 项目
匹配时间: 2026-05-10 10:30:00
匹配数量: 3

匹配结果:
------------------------------------------------------------
1. java-springboot
   优先级: P1
   分数: 85.5
   原因: 匹配到关键词: Spring Boot, Java 后端

2. create-skill
   优先级: P0
   分数: 72.3
   原因: 匹配到关键词: 创建

执行计划:
------------------------------------------------------------
Phase 1 - Critical (sequential)
  - create-skill (Score: 72.3)

Phase 2 - Important (parallel)
  - java-springboot (Score: 85.5)
```

### 2. 测试套件

```bash
# 运行所有测试
python scripts/test_orchestrator.py

# 运行特定测试
python scripts/test_orchestrator.py --test matching
python scripts/test_orchestrator.py --test performance

# 输出示例
======================================================================
Skill Orchestrator - 测试套件
======================================================================

▶ 运行测试: 关键词匹配测试
----------------------------------------------------------------------
  ✓ '帮我创建一个 skill' → 匹配到 create-skill
  ✓ '查找 Python 相关的 skills' → 匹配到 find-skills
  ✓ '审查这段代码' → 匹配到 code-review-and-quality
✅ 通过 (耗时: 0.045s)

测试总结
======================================================================
总测试数: 5
通过: 5 ✅
失败: 0 ❌
```

### 3. 性能监控

```bash
# 生成日报
python scripts/performance_monitor.py --report daily

# 生成周报
python scripts/performance_monitor.py --report weekly

# 详细分析
python scripts/performance_monitor.py --analyze

# 输出示例
======================================================================
性能报告 - DAILY
======================================================================

生成时间: 2026-05-10T10:30:00
总执行数: 156
成功率: 98.7%

执行时间:
  平均值: 45.23ms
  P50: 38.50ms
  P95: 125.80ms
  P99: 245.60ms

Top Skills:
  - create-skill: 45 次
  - code-review-and-quality: 32 次
  - java-springboot: 28 次

优化建议:
  ✅ 性能指标良好，无需优化
```

### 4. 配置管理

配置文件位置：`config/matching_rules.json`

```json
{
  "matching_rules": {
    "keyword_weight": 0.4,
    "semantic_weight": 0.3,
    "frequency_weight": 0.2,
    "preference_weight": 0.1,
    "min_score_threshold": 50,
    "max_results": 5
  },
  "execution_settings": {
    "max_parallel_skills": 3,
    "skill_timeout_seconds": 30,
    "enable_cache": true,
    "cache_ttl_seconds": 300
  }
}
```

修改配置后无需重启，系统会自动重载。

### 5. 日志查看

```bash
# 查看最新日志
tail -f logs/orchestrator.log

# 查看错误日志
grep "ERROR" logs/orchestrator.log

# 查看执行历史
cat output/match_result_*.json | jq .
```

### 6. ⭐ 自动 Skill 安装（新增）

**Skills 数据库** (`config/skills_database.json`)

包含 18+ 个精选 skills，分为 6 大类：
- Core Development (5个)
- Language Specific (2个)
- Architecture Design (2个)
- Documentation & Testing (2个)
- Advanced Tools (4个)
- Productivity (2个)

**检查 skill 状态：**
```bash
# 检查单个 skill
python scripts/skill_installer.py --check api-security

# 列出所有 skills
python scripts/skill_installer.py --list

# 按分类列出
python scripts/skill_installer.py --list advanced_tools
```

**安装 skills：**
```bash
# 安装单个 skill
python scripts/skill_installer.py --install api-security

# 自动确认安装
python scripts/skill_installer.py --install api-security --auto-confirm

# 安装所有缺失的 skills
python scripts/skill_installer.py --install-all-missing --auto-confirm
```

**搜索 skills：**
```bash
# 搜索关键词
python scripts/skill_installer.py --search security
python scripts/skill_installer.py --search testing
```

**输出示例：**
```bash
$ python scripts/skill_installer.py --list

📚 所有可用 Skills

Name                                Priority   Installed    Description
----------------------------------------------------------------------------------------------------
create-skill                        P0         ✅ Yes       创建新的 skill
find-skills                         P0         ✅ Yes       查找和安装 skills
code-review-and-quality             P0         ✅ Yes       代码审查和质量检查
api-security                        P1         ❌ No        API 安全检查和加固
database-testing                    P2         ❌ No        数据库测试和优化
...

$ python scripts/skill_installer.py --install-all-missing --auto-confirm

📋 发现 3 个未安装的 skills:

1. api-security - API 安全检查和加固
2. database-testing - 数据库测试和优化
3. security-operations-deployment - 安全运维和部署

📦 准备安装 skill: api-security
   描述: API 安全检查和加固
   来源: hardw00t/ai-security-arsenal
   命令: npx skills add hardw00t/ai-security-arsenal@api-security -g -y

🔧 正在安装...
✅ Skill 'api-security' 安装成功!

...

📊 安装总结:
   总数: 3
   成功: 3 ✅
   失败: 0 ❌
```

## 📊 目录结构

```
skill-orchestrator/
├── SKILL.md                    # 主文档（本文件）
├── USAGE.md                    # 使用指南
├── config/
│   └── matching_rules.json     # 匹配规则配置
├── scripts/
│   ├── skill_matcher.py        # 智能匹配引擎
│   ├── test_orchestrator.py    # 测试套件
│   └── performance_monitor.py  # 性能监控
├── logs/
│   └── orchestrator.log        # 运行日志（自动生成）
└── output/
    ├── match_result_*.json     # 匹配结果（自动生成）
    └── test_results_*.json     # 测试结果（自动生成）
```

## 🔧 开发和扩展

### 添加新的 Skill

1. 在 `scripts/skill_matcher.py` 的 `_load_skills()` 方法中添加：

```python
SkillInfo(
    name="your-new-skill",
    description="技能描述",
    triggers=["触发词1", "触发词2"],
    priority="P1",
    category="category_name"
)
```

2. 更新 `config/matching_rules.json` 中的触发词（可选）

3. 运行测试验证：

```bash
python scripts/test_orchestrator.py
```

### 自定义匹配算法

修改 `scripts/skill_matcher.py` 中的 `_calculate_score()` 方法：

```python
def _calculate_score(self, user_request: str, skill: SkillInfo):
    # 添加你的自定义逻辑
    custom_score = your_custom_algorithm(user_request, skill)
    
    # 与其他分数组合
    final_score = (
        keyword_score * 0.3 +
        semantic_score * 0.3 +
        custom_score * 0.4  # 你的自定义权重
    )
    
    return final_score, matched_keywords
```

### 集成到 CI/CD

```yaml
# .github/workflows/test.yml
name: Test Skill Orchestrator

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Run tests
        run: |
          cd skill-orchestrator
          python scripts/test_orchestrator.py
      - name: Performance check
        run: |
          cd skill-orchestrator
          python scripts/performance_monitor.py --report daily
```

---

**最后更新：** 2026-05-10  
**版本：** v2.0 (Enterprise Edition)  
**维护者：** XiaoYe Team
