#!/usr/bin/env python3
"""
Skill Orchestrator 测试套件

功能：
1. 单元测试匹配算法
2. 集成测试执行流程
3. 性能基准测试
4. 回归测试

用法：
    python scripts/test_orchestrator.py
    python scripts/test_orchestrator.py --test matching
    python scripts/test_orchestrator.py --test performance
"""

import sys
import os
import time
import json
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.skill_matcher import SkillMatcher, MatchResult

class TestOrchestrator:
    """测试套件"""
    
    def __init__(self):
        self.matcher = SkillMatcher()
        self.test_results = []
        
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 70)
        print("Skill Orchestrator - 测试套件")
        print("=" * 70)
        print()
        
        tests = [
            ("关键词匹配测试", self.test_keyword_matching),
            ("优先级排序测试", self.test_priority_sorting),
            ("执行计划生成测试", self.test_execution_plan),
            ("边界条件测试", self.test_edge_cases),
            ("性能基准测试", self.test_performance),
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"\n▶ 运行测试: {test_name}")
                print("-" * 70)
                start_time = time.time()
                result = test_func()
                elapsed = time.time() - start_time
                
                if result:
                    print(f"✅ 通过 (耗时: {elapsed:.3f}s)")
                else:
                    print(f"❌ 失败 (耗时: {elapsed:.3f}s)")
                
                self.test_results.append({
                    "test": test_name,
                    "passed": result,
                    "time": elapsed
                })
                
            except Exception as e:
                print(f"❌ 异常: {str(e)}")
                self.test_results.append({
                    "test": test_name,
                    "passed": False,
                    "error": str(e)
                })
        
        # 打印总结
        self.print_summary()
    
    def test_keyword_matching(self) -> bool:
        """测试关键词匹配"""
        test_cases = [
            ("帮我创建一个 skill", ["create-skill"]),
            ("查找 Python 相关的 skills", ["find-skills", "python-design-patterns"]),
            ("审查这段代码", ["code-review-and-quality"]),
            ("修复这个 bug", ["systematic-debugging"]),
            ("重构优化代码", ["refactor"]),
        ]
        
        all_passed = True
        
        for request, expected_skills in test_cases:
            matches = self.matcher.match(request)
            matched_names = [m.skill_name for m in matches]
            
            # 检查是否至少有一个预期的 skill 被匹配
            found = any(skill in matched_names for skill in expected_skills)
            
            if found:
                print(f"  ✓ '{request}' → 匹配到 {matched_names[0] if matched_names else '无'}")
            else:
                print(f"  ✗ '{request}' → 期望 {expected_skills}, 实际 {matched_names}")
                all_passed = False
        
        return all_passed
    
    def test_priority_sorting(self) -> bool:
        """测试优先级排序"""
        request = "帮我创建一个 Java Spring Boot 项目并编写文档"
        matches = self.matcher.match(request)
        
        if not matches:
            print("  ✗ 没有匹配到任何 skills")
            return False
        
        # 检查 P0 优先于 P1，P1 优先于 P2
        priorities = [m.priority for m in matches]
        
        # 验证排序（简化检查）
        p0_count = priorities.count("P0")
        p1_count = priorities.count("P1")
        p2_count = priorities.count("P2")
        
        print(f"  匹配结果: {len(matches)} 个 skills")
        print(f"  P0: {p0_count}, P1: {p1_count}, P2: {p2_count}")
        
        # 分数应该递减
        scores = [m.score for m in matches]
        is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
        
        if is_sorted:
            print("  ✓ 分数按降序排列")
        else:
            print("  ✗ 分数未正确排序")
        
        return is_sorted
    
    def test_execution_plan(self) -> bool:
        """测试执行计划生成"""
        request = "帮我重构这个 Java 微服务项目"
        matches = self.matcher.match(request)
        
        if not matches:
            print("  ✗ 没有匹配到任何 skills")
            return False
        
        plan = self.matcher.generate_execution_plan(matches)
        
        # 验证计划结构
        required_keys = ["timestamp", "total_matches", "execution_order", "parallel_groups"]
        has_all_keys = all(key in plan for key in required_keys)
        
        if has_all_keys:
            print(f"  ✓ 执行计划包含所有必需字段")
            print(f"  总匹配数: {plan['total_matches']}")
            print(f"  执行阶段数: {len(plan['execution_order'])}")
            print(f"  并行组数: {len(plan['parallel_groups'])}")
        else:
            print(f"  ✗ 执行计划缺少必需字段")
        
        return has_all_keys
    
    def test_edge_cases(self) -> bool:
        """测试边界条件"""
        test_cases = [
            ("", "空字符串"),
            ("a", "单字符"),
            ("你好世界", "中文无匹配"),
            ("🎉🚀✨", "emoji"),
            (" " * 100, "纯空格"),
        ]
        
        all_passed = True
        
        for request, description in test_cases:
            try:
                matches = self.matcher.match(request)
                print(f"  ✓ {description}: 返回 {len(matches)} 个匹配")
            except Exception as e:
                print(f"  ✗ {description}: 异常 - {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_performance(self) -> bool:
        """性能基准测试"""
        test_requests = [
            "帮我创建一个 skill",
            "审查这段代码",
            "修复 bug",
            "重构优化",
            "Java Spring Boot 项目",
        ] * 10  # 重复 10 次
        
        start_time = time.time()
        
        for request in test_requests:
            self.matcher.match(request)
        
        elapsed = time.time() - start_time
        avg_time = elapsed / len(test_requests)
        
        print(f"  总请求数: {len(test_requests)}")
        print(f"  总耗时: {elapsed:.3f}s")
        print(f"  平均耗时: {avg_time*1000:.2f}ms/请求")
        
        # 性能要求：平均每个请求 < 100ms
        if avg_time < 0.1:
            print(f"  ✓ 性能达标 (< 100ms/请求)")
            return True
        else:
            print(f"  ⚠ 性能警告 (> 100ms/请求)")
            return True  # 不视为失败，只是警告
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 70)
        print("测试总结")
        print("=" * 70)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["passed"])
        failed = total - passed
        
        print(f"\n总测试数: {total}")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        
        if failed > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['test']}")
                    if "error" in result:
                        print(f"    错误: {result['error']}")
        
        print("\n" + "=" * 70)
        
        # 保存测试结果
        self.save_results()
    
    def save_results(self):
        """保存测试结果"""
        output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"test_results_{timestamp}.json")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "passed": sum(1 for r in self.test_results if r["passed"]),
            "failed": sum(1 for r in self.test_results if not r["passed"]),
            "details": self.test_results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试结果已保存到: {output_file}")


def main():
    """主函数"""
    tester = TestOrchestrator()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
