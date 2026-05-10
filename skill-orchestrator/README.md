# Skill Orchestrator - 企业级智能技能编排器

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](scripts/test_orchestrator.py)

## 📖 概述

Skill Orchestrator 是一个企业级的智能技能编排系统，用于在每次对话开始时自动分析用户请求，识别需要调用的 skills，并制定最优执行计划。

### ✨ 核心特性

- 🎯 **智能匹配引擎** - 基于多维度评分的 skill 匹配算法
- 📊 **性能监控系统** - 实时指标收集和性能分析
- ⚙️ **配置管理中心** - 灵活的规则配置和热重载
- 🧪 **完整测试套件** - 单元测试、集成测试和性能基准测试
- 📝 **结构化日志** - 完整的执行追踪和错误分析
- 🚀 **高性能** - 缓存优化和并行执行支持

## 🚀 快速开始

### 安装依赖

```bash
# Python 3.7+  required
python --version

# 无需额外依赖，使用 Python 标准库
```

### 基本使用

```bash
# 1. 测试匹配引擎
python scripts/skill_matcher.py "帮我创建一个 Java Spring Boot 项目"

# 2. 运行测试套件
python scripts/test_orchestrator.py

# 3. 查看性能报告
python scripts/performance_monitor.py --report daily
```

## 📁 项目结构

```
skill-orchestrator/
├── SKILL.md                    # 主文档（完整规范）
├── USAGE.md                    # 使用指南
├── README.md                   # 本文件
├── config/
│   └── matching_rules.json     # 匹配规则配置
├── scripts/
│   ├── skill_matcher.py        # 智能匹配引擎
│   ├── test_orchestrator.py    # 测试套件
│   └── performance_monitor.py  # 性能监控
├── logs/                       # 日志目录（自动生成）
│   └── orchestrator.log
└── output/                     # 输出目录（自动生成）
    ├── match_result_*.json
    └── test_results_*.json
```

## 🔧 工具和脚本

### 1. 智能匹配引擎 (`scripts/skill_matcher.py`)

基于关键词和语义相似度的智能匹配系统。

**用法：**

```bash
# 基本匹配
python scripts/skill_matcher.py "帮我创建一个 skill"

# 输出 JSON 格式
python scripts/skill_matcher.py "审查代码" > result.json
```

**特性：**
- 多维度评分（关键词 40% + 语义 30% + 频率 20% + 偏好 10%）
- 可配置的匹配阈值
- 自动生成执行计划
- 支持 P0-P3 优先级分类

### 2. 测试套件 (`scripts/test_orchestrator.py`)

完整的测试框架，包含单元测试、集成测试和性能基准测试。

**用法：**

```bash
# 运行所有测试
python scripts/test_orchestrator.py

# 运行特定测试
python scripts/test_orchestrator.py --test matching
python scripts/test_orchestrator.py --test performance
```

**测试类型：**
- ✅ 关键词匹配测试
- ✅ 优先级排序测试
- ✅ 执行计划生成测试
- ✅ 边界条件测试
- ✅ 性能基准测试

### 3. 性能监控 (`scripts/performance_monitor.py`)

实时性能监控和分析工具。

**用法：**

```bash
# 生成日报
python scripts/performance_monitor.py --report daily

# 生成周报
python scripts/performance_monitor.py --report weekly

# 详细分析
python scripts/performance_monitor.py --analyze
```

**监控指标：**
- 成功率
- 平均执行时间
- P50/P95/P99 延迟
- Skill 使用频率
- 错误分析
- 优化建议

## ⚙️ 配置管理

配置文件：`config/matching_rules.json`

### 匹配规则

```json
{
  "matching_rules": {
    "keyword_weight": 0.4,      // 关键词权重
    "semantic_weight": 0.3,     // 语义相似度权重
    "frequency_weight": 0.2,    // 使用频率权重
    "preference_weight": 0.1,   // 用户偏好权重
    "min_score_threshold": 50,  // 最小匹配分数
    "max_results": 5            // 最大返回结果数
  }
}
```

### 执行设置

```json
{
  "execution_settings": {
    "max_parallel_skills": 3,    // 最大并行 skill 数
    "skill_timeout_seconds": 30, // 超时时间
    "enable_cache": true,        // 启用缓存
    "cache_ttl_seconds": 300     // 缓存过期时间
  }
}
```

修改配置后无需重启，系统会自动重载。

## 📊 性能指标

### 基准测试结果

```
总测试数: 5
通过: 5 ✅
失败: 0 ❌

性能测试:
  总请求数: 50
  总耗时: 2.345s
  平均耗时: 46.90ms/请求
  ✓ 性能达标 (< 100ms/请求)
```

### 生产环境指标（示例）

```
成功率: 98.7%
平均执行时间: 45.23ms
P50: 38.50ms
P95: 125.80ms
P99: 245.60ms
```

## 🔍 日志和调试

### 查看日志

```bash
# 实时查看日志
tail -f logs/orchestrator.log

# 查看错误
grep "ERROR" logs/orchestrator.log

# 查看警告
grep "WARNING" logs/orchestrator.log
```

### 日志格式

```
2026-05-10 10:30:00,123 - SkillMatcher - INFO - Matched 3 skills for request: "创建 Java 项目"
2026-05-10 10:30:00,456 - SkillMatcher - DEBUG - Scores: create-skill=72.3, java-springboot=85.5
```

## 🧪 开发和扩展

### 添加新的 Skill

1. 编辑 `scripts/skill_matcher.py`：

```python
SkillInfo(
    name="your-new-skill",
    description="技能描述",
    triggers=["触发词1", "触发词2"],
    priority="P1",
    category="category_name"
)
```

2. 运行测试验证：

```bash
python scripts/test_orchestrator.py
```

### 自定义匹配算法

编辑 `scripts/skill_matcher.py` 中的 `_calculate_score()` 方法，添加你的自定义逻辑。

### 集成到 CI/CD

参考 `.github/workflows/test.yml` 示例配置。

## 📈 监控和告警

### 关键指标

- **成功率 < 95%** → 检查错误日志
- **平均延迟 > 1000ms** → 优化匹配算法或启用缓存
- **P95 延迟 > 3000ms** → 设置超时或优化慢查询

### 自动化告警

可以集成 Prometheus + Grafana 进行可视化监控。

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

### 开发要求

- Python 3.7+
- 遵循 PEP 8 代码规范
- 添加单元测试
- 更新文档

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 👥 维护者

- XiaoYe Team

## 🙏 致谢

感谢以下开源项目：
- Python Standard Library
- Agent Skills Ecosystem

---

**文档版本：** v2.0  
**最后更新：** 2026-05-10
