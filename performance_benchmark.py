#!/usr/bin/env python3
"""
Performance benchmarking and optimization for MCP server
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List
import statistics

import httpx


class MCPPerformanceBenchmark:
    """Performance benchmarking suite for MCP server"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server_url": server_url,
            "benchmark_results": {},
            "recommendations": []
        }
    
    async def benchmark_endpoint(self, endpoint: str, method: str = "GET", 
                                payload: Dict[str, Any] = None, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark a specific endpoint"""
        print(f"🔧 Benchmarking {method} {endpoint} ({iterations} iterations)...")
        
        response_times = []
        status_codes = []
        errors = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(iterations):
                start_time = time.time()
                try:
                    if method == "GET":
                        response = await client.get(f"{self.server_url}{endpoint}")
                    elif method == "POST":
                        response = await client.post(f"{self.server_url}{endpoint}", json=payload)
                    
                    duration_ms = (time.time() - start_time) * 1000
                    response_times.append(duration_ms)
                    status_codes.append(response.status_code)
                    
                    if response.status_code >= 400:
                        errors.append(f"HTTP {response.status_code}: {response.text[:100]}")
                        
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    response_times.append(duration_ms)
                    errors.append(str(e))
                    status_codes.append(0)
                
                # Small delay between requests
                await asyncio.sleep(0.1)
        
        # Calculate statistics
        if response_times:
            avg_time = statistics.mean(response_times)
            median_time = statistics.median(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            p95_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max_time
        else:
            avg_time = median_time = min_time = max_time = p95_time = 0
        
        success_rate = (len([sc for sc in status_codes if 200 <= sc < 300]) / len(status_codes)) * 100
        
        return {
            "endpoint": endpoint,
            "method": method,
            "iterations": iterations,
            "average_response_time_ms": avg_time,
            "median_response_time_ms": median_time,
            "min_response_time_ms": min_time,
            "max_response_time_ms": max_time,
            "p95_response_time_ms": p95_time,
            "success_rate_percent": success_rate,
            "total_errors": len(errors),
            "error_samples": errors[:3]  # First 3 errors
        }
    
    async def benchmark_template_operations(self) -> Dict[str, Any]:
        """Benchmark template-related operations"""
        print("📊 Benchmarking template operations...")
        
        results = {}
        
        # 1. List templates
        results["list_templates"] = await self.benchmark_endpoint("/api/templates", "GET", iterations=20)
        
        # 2. Get specific template
        results["get_template"] = await self.benchmark_endpoint("/api/templates/youtube_viral_trends", "GET", iterations=15)
        
        # 3. Template processing
        template_process_payload = {
            "template_name": "youtube_viral_trends",
            "context_variables": {
                "target_audience": "tech enthusiasts",
                "current_trends": ["AI", "blockchain", "gaming"],
                "duration_preference": "short"
            }
        }
        results["process_template"] = await self.benchmark_endpoint(
            "/api/templates/process", "POST", template_process_payload, iterations=10
        )
        
        return results
    
    async def benchmark_system_endpoints(self) -> Dict[str, Any]:
        """Benchmark system endpoints"""
        print("🔍 Benchmarking system endpoints...")
        
        results = {}
        
        # Health checks
        results["health_basic"] = await self.benchmark_endpoint("/health", "GET", iterations=30)
        results["health_detailed"] = await self.benchmark_endpoint("/health/detailed", "GET", iterations=20)
        
        # Metrics
        results["metrics"] = await self.benchmark_endpoint("/metrics", "GET", iterations=15)
        
        # Status
        results["system_status"] = await self.benchmark_endpoint("/api/status", "GET", iterations=15)
        
        return results
    
    async def load_test(self, concurrent_users: int = 5, duration_seconds: int = 30) -> Dict[str, Any]:
        """Perform load testing with concurrent requests"""
        print(f"⚡ Load testing with {concurrent_users} concurrent users for {duration_seconds}s...")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        async def worker(worker_id: int):
            """Single worker making requests"""
            requests_made = 0
            response_times = []
            errors = 0
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                while time.time() < end_time:
                    try:
                        req_start = time.time()
                        response = await client.get(f"{self.server_url}/health")
                        req_duration = (time.time() - req_start) * 1000
                        
                        response_times.append(req_duration)
                        requests_made += 1
                        
                        if response.status_code >= 400:
                            errors += 1
                            
                    except Exception:
                        errors += 1
                        requests_made += 1
                    
                    # Small delay
                    await asyncio.sleep(0.1)
            
            return {
                "worker_id": worker_id,
                "requests_made": requests_made,
                "average_response_time_ms": statistics.mean(response_times) if response_times else 0,
                "errors": errors
            }
        
        # Run concurrent workers
        tasks = [worker(i) for i in range(concurrent_users)]
        worker_results = await asyncio.gather(*tasks)
        
        # Aggregate results
        total_requests = sum(w["requests_made"] for w in worker_results)
        total_errors = sum(w["errors"] for w in worker_results)
        avg_response_times = [w["average_response_time_ms"] for w in worker_results if w["average_response_time_ms"] > 0]
        
        actual_duration = time.time() - start_time
        
        return {
            "concurrent_users": concurrent_users,
            "duration_seconds": actual_duration,
            "total_requests": total_requests,
            "requests_per_second": total_requests / actual_duration,
            "total_errors": total_errors,
            "error_rate_percent": (total_errors / total_requests) * 100 if total_requests > 0 else 0,
            "average_response_time_ms": statistics.mean(avg_response_times) if avg_response_times else 0,
            "worker_results": worker_results
        }
    
    def analyze_results(self):
        """Analyze benchmark results and generate recommendations"""
        print("🔍 Analyzing results and generating recommendations...")
        
        recommendations = []
        
        # Check response times
        template_results = self.results["benchmark_results"].get("template_operations", {})
        system_results = self.results["benchmark_results"].get("system_endpoints", {})
        load_results = self.results["benchmark_results"].get("load_test", {})
        
        # Response time analysis
        slow_endpoints = []
        for category, endpoints in [("template", template_results), ("system", system_results)]:
            for endpoint_name, data in endpoints.items():
                if data.get("average_response_time_ms", 0) > 1000:
                    slow_endpoints.append(f"{endpoint_name} ({data.get('average_response_time_ms', 0):.1f}ms)")
        
        if slow_endpoints:
            recommendations.append({
                "category": "performance",
                "priority": "high",
                "issue": "Slow response times detected",
                "details": f"Endpoints with >1s response time: {', '.join(slow_endpoints)}",
                "solutions": [
                    "Add database query optimization with indexes",
                    "Implement response caching for frequently accessed templates", 
                    "Consider connection pooling optimization",
                    "Add database query monitoring"
                ]
            })
        
        # Error rate analysis
        high_error_endpoints = []
        for category, endpoints in [("template", template_results), ("system", system_results)]:
            for endpoint_name, data in endpoints.items():
                if data.get("success_rate_percent", 100) < 95:
                    high_error_endpoints.append(f"{endpoint_name} ({data.get('success_rate_percent', 100):.1f}%)")
        
        if high_error_endpoints:
            recommendations.append({
                "category": "reliability",
                "priority": "high", 
                "issue": "High error rates detected",
                "details": f"Endpoints with <95% success rate: {', '.join(high_error_endpoints)}",
                "solutions": [
                    "Add retry logic with exponential backoff",
                    "Improve error handling and logging",
                    "Add circuit breaker pattern for external dependencies",
                    "Implement graceful degradation"
                ]
            })
        
        # Load test analysis
        if load_results:
            rps = load_results.get("requests_per_second", 0)
            error_rate = load_results.get("error_rate_percent", 0)
            
            if rps < 10:
                recommendations.append({
                    "category": "scalability",
                    "priority": "medium",
                    "issue": "Low throughput under load",
                    "details": f"Only {rps:.1f} requests/second with {load_results.get('concurrent_users', 0)} users",
                    "solutions": [
                        "Increase Cloud Run concurrency settings",
                        "Optimize database connection pooling",
                        "Add Redis caching layer",
                        "Consider horizontal scaling"
                    ]
                })
            
            if error_rate > 5:
                recommendations.append({
                    "category": "stability",
                    "priority": "high",
                    "issue": "High error rate under load",
                    "details": f"{error_rate:.1f}% error rate during load test",
                    "solutions": [
                        "Increase Cloud Run memory allocation",
                        "Add request rate limiting",
                        "Implement queue-based processing for heavy operations",
                        "Add health check endpoints with graceful degradation"
                    ]
                })
        
        # General optimization recommendations
        recommendations.append({
            "category": "optimization",
            "priority": "low",
            "issue": "General performance improvements",
            "details": "Proactive optimizations for better performance",
            "solutions": [
                "Implement template result caching",
                "Add database query result caching", 
                "Optimize JSON serialization/deserialization",
                "Add request/response compression",
                "Implement database read replicas for scaling"
            ]
        })
        
        self.results["recommendations"] = recommendations
    
    async def run_full_benchmark(self) -> Dict[str, Any]:
        """Run complete benchmark suite"""
        print("🚀 Starting comprehensive MCP server benchmark...")
        print(f"Target server: {self.server_url}")
        print("=" * 60)
        
        # Run benchmarks
        self.results["benchmark_results"]["template_operations"] = await self.benchmark_template_operations()
        self.results["benchmark_results"]["system_endpoints"] = await self.benchmark_system_endpoints()
        self.results["benchmark_results"]["load_test"] = await self.load_test(concurrent_users=5, duration_seconds=30)
        
        # Analyze and generate recommendations
        self.analyze_results()
        
        print("\n" + "=" * 60)
        print("✅ Benchmark complete!")
        
        return self.results
    
    def print_summary(self):
        """Print benchmark summary"""
        print("\n📊 PERFORMANCE BENCHMARK SUMMARY")
        print("=" * 50)
        
        # Template operations summary
        template_ops = self.results["benchmark_results"].get("template_operations", {})
        if template_ops:
            print("\n🔧 Template Operations:")
            for op_name, data in template_ops.items():
                avg_time = data.get("average_response_time_ms", 0)
                success_rate = data.get("success_rate_percent", 0)
                print(f"  {op_name}: {avg_time:.1f}ms avg, {success_rate:.1f}% success")
        
        # System endpoints summary  
        system_ops = self.results["benchmark_results"].get("system_endpoints", {})
        if system_ops:
            print("\n🔍 System Endpoints:")
            for op_name, data in system_ops.items():
                avg_time = data.get("average_response_time_ms", 0)
                success_rate = data.get("success_rate_percent", 0)
                print(f"  {op_name}: {avg_time:.1f}ms avg, {success_rate:.1f}% success")
        
        # Load test summary
        load_test = self.results["benchmark_results"].get("load_test", {})
        if load_test:
            print("\n⚡ Load Test Results:")
            print(f"  Concurrent users: {load_test.get('concurrent_users', 0)}")
            print(f"  Requests/second: {load_test.get('requests_per_second', 0):.1f}")
            print(f"  Error rate: {load_test.get('error_rate_percent', 0):.1f}%")
            print(f"  Avg response time: {load_test.get('average_response_time_ms', 0):.1f}ms")
        
        # Recommendations summary
        recommendations = self.results.get("recommendations", [])
        if recommendations:
            print("\n💡 TOP RECOMMENDATIONS:")
            high_priority = [r for r in recommendations if r.get("priority") == "high"]
            medium_priority = [r for r in recommendations if r.get("priority") == "medium"]
            
            for rec in high_priority[:2]:  # Top 2 high priority
                print(f"  🔴 HIGH: {rec.get('issue', 'Unknown')}")
                print(f"     Solution: {rec.get('solutions', [''])[0]}")
            
            for rec in medium_priority[:1]:  # Top 1 medium priority
                print(f"  🟡 MED: {rec.get('issue', 'Unknown')}")
                print(f"     Solution: {rec.get('solutions', [''])[0]}")


async def main():
    """Main function"""
    server_url = "https://tenxsom-mcp-server-hpkm6siuqq-uc.a.run.app"
    
    benchmark = MCPPerformanceBenchmark(server_url)
    results = await benchmark.run_full_benchmark()
    
    # Print summary
    benchmark.print_summary()
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"mcp_benchmark_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")


if __name__ == "__main__":
    asyncio.run(main())