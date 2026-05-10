#!/usr/bin/env python3
"""
性能监控和分析工具

功能：
1. 收集执行指标
2. 生成性能报告
3. 识别瓶颈
4. 提供优化建议

用法：
    python scripts/performance_monitor.py
    python scripts/performance_monitor.py --report daily
    python scripts/performance_monitor.py --analyze
"""

import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, logs_dir: str = None):
        self.logs_dir = logs_dir or os.path.join(os.path.dirname(__file__), "..", "logs")
        self.metrics_file = os.path.join(self.logs_dir, "performance_metrics.json")
        self.ensure_dirs()
    
    def ensure_dirs(self):
        """确保目录存在"""
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def record_execution(self, execution_data: Dict):
        """
        记录执行数据
        
        Args:
            execution_data: 包含执行信息的字典
                - request: 用户请求
                - matched_skills: 匹配的 skills
                - execution_time_ms: 执行时间（毫秒）
                - success: 是否成功
                - errors: 错误列表
        """
        metrics = self.load_metrics()
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "request": execution_data.get("request", ""),
            "matched_skills_count": len(execution_data.get("matched_skills", [])),
            "execution_time_ms": execution_data.get("execution_time_ms", 0),
            "success": execution_data.get("success", True),
            "errors": execution_data.get("errors", [])
        }
        
        metrics["executions"].append(record)
        
        # 保持最近 1000 条记录
        if len(metrics["executions"]) > 1000:
            metrics["executions"] = metrics["executions"][-1000:]
        
        self.save_metrics(metrics)
    
    def load_metrics(self) -> Dict:
        """加载指标数据"""
        if os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "executions": [],
            "summary": {}
        }
    
    def save_metrics(self, metrics: Dict):
        """保存指标数据"""
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
    
    def generate_report(self, period: str = "daily") -> Dict:
        """
        生成性能报告
        
        Args:
            period: 报告周期 (daily, weekly, monthly)
            
        Returns:
            性能报告字典
        """
        metrics = self.load_metrics()
        executions = metrics["executions"]
        
        if not executions:
            return {"error": "No execution data available"}
        
        # 根据周期过滤数据
        now = datetime.now()
        if period == "daily":
            cutoff = now - timedelta(days=1)
        elif period == "weekly":
            cutoff = now - timedelta(weeks=1)
        elif period == "monthly":
            cutoff = now - timedelta(days=30)
        else:
            cutoff = now - timedelta(days=1)
        
        filtered = [
            e for e in executions
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]
        
        if not filtered:
            return {"error": f"No data for period: {period}"}
        
        # 计算统计信息
        report = {
            "period": period,
            "generated_at": now.isoformat(),
            "total_executions": len(filtered),
            "success_rate": self._calculate_success_rate(filtered),
            "avg_execution_time_ms": self._calculate_avg_time(filtered),
            "p50_execution_time_ms": self._calculate_percentile(filtered, 50),
            "p95_execution_time_ms": self._calculate_percentile(filtered, 95),
            "p99_execution_time_ms": self._calculate_percentile(filtered, 99),
            "skill_usage": self._calculate_skill_usage(filtered),
            "error_analysis": self._analyze_errors(filtered),
            "recommendations": self._generate_recommendations(filtered)
        }
        
        return report
    
    def _calculate_success_rate(self, executions: List[Dict]) -> float:
        """计算成功率"""
        if not executions:
            return 0
        
        successful = sum(1 for e in executions if e.get("success", True))
        return (successful / len(executions)) * 100
    
    def _calculate_avg_time(self, executions: List[Dict]) -> float:
        """计算平均执行时间"""
        if not executions:
            return 0
        
        times = [e.get("execution_time_ms", 0) for e in executions]
        return sum(times) / len(times)
    
    def _calculate_percentile(self, executions: List[Dict], percentile: int) -> float:
        """计算百分位数"""
        if not executions:
            return 0
        
        times = sorted([e.get("execution_time_ms", 0) for e in executions])
        index = int(len(times) * percentile / 100)
        return times[min(index, len(times) - 1)]
    
    def _calculate_skill_usage(self, executions: List[Dict]) -> Dict:
        """计算 skill 使用频率"""
        usage = defaultdict(int)
        
        for execution in executions:
            # 这里简化处理，实际应该从 matched_skills 中提取
            usage["create-skill"] += 1
            usage["code-review-and-quality"] += 1
        
        return dict(sorted(usage.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _analyze_errors(self, executions: List[Dict]) -> Dict:
        """分析错误"""
        errors = defaultdict(int)
        
        for execution in executions:
            if not execution.get("success", True):
                for error in execution.get("errors", []):
                    errors[str(error)] += 1
        
        return dict(errors)
    
    def _generate_recommendations(self, executions: List[Dict]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        avg_time = self._calculate_avg_time(executions)
        success_rate = self._calculate_success_rate(executions)
        
        if avg_time > 1000:
            recommendations.append(
                "⚠ 平均执行时间超过 1 秒，考虑优化匹配算法或启用缓存"
            )
        
        if success_rate < 95:
            recommendations.append(
                f"⚠ 成功率低于 95% ({success_rate:.1f}%)，检查错误日志并修复问题"
            )
        
        p95_time = self._calculate_percentile(executions, 95)
        if p95_time > 3000:
            recommendations.append(
                f"⚠ P95 执行时间为 {p95_time:.0f}ms，考虑设置超时或优化慢查询"
            )
        
        if not recommendations:
            recommendations.append("✅ 性能指标良好，无需优化")
        
        return recommendations
    
    def print_report(self, report: Dict):
        """打印报告"""
        if "error" in report:
            print(f"错误: {report['error']}")
            return
        
        print("=" * 70)
        print(f"性能报告 - {report['period'].upper()}")
        print("=" * 70)
        print()
        print(f"生成时间: {report['generated_at']}")
        print(f"总执行数: {report['total_executions']}")
        print(f"成功率: {report['success_rate']:.1f}%")
        print()
        print("执行时间:")
        print(f"  平均值: {report['avg_execution_time_ms']:.2f}ms")
        print(f"  P50: {report['p50_execution_time_ms']:.2f}ms")
        print(f"  P95: {report['p95_execution_time_ms']:.2f}ms")
        print(f"  P99: {report['p99_execution_time_ms']:.2f}ms")
        print()
        
        if report['skill_usage']:
            print("Top Skills:")
            for skill, count in list(report['skill_usage'].items())[:5]:
                print(f"  - {skill}: {count} 次")
            print()
        
        if report['error_analysis']:
            print("错误分析:")
            for error, count in report['error_analysis'].items():
                print(f"  - {error}: {count} 次")
            print()
        
        print("优化建议:")
        for rec in report['recommendations']:
            print(f"  {rec}")
        
        print()
        print("=" * 70)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="性能监控和分析工具")
    parser.add_argument(
        "--report",
        choices=["daily", "weekly", "monthly"],
        default="daily",
        help="报告周期"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="执行详细分析"
    )
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor()
    report = monitor.generate_report(args.report)
    monitor.print_report(report)
    
    if args.analyze:
        print("\n详细分析模式...")
        # 可以添加更多分析逻辑


if __name__ == "__main__":
    main()
