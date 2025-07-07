"""
History Processor for Flow Execution Tracking
Processes Flow History objects into structured reports for debugging and analytics
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List

# Import our flow framework
import sys
sys.path.append('..')
from flow_framework import fl, History, FlowEvent

# Configure production logging
logger = logging.getLogger(__name__)


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"


def format_flow_history(history: History) -> str:
    """
    Parse the Flow History object and generate a human-readable report
    
    Args:
        history: Flow execution history
        
    Returns:
        Formatted execution report as string
    """
    report = []
    report.append("=" * 70)
    report.append(" TENXSOM AI FLOW EXECUTION REPORT")
    report.append("=" * 70)
    
    if not history.events:
        report.append("\n❌ No execution events found")
        return "\n".join(report)
    
    # Get root event (main flow)
    root_events = history.get_root_events()
    if not root_events:
        report.append("\n❌ No root events found")
        return "\n".join(report)
    
    main_event = root_events[0]
    
    # Calculate total duration
    if main_event.end_time and main_event.start_time:
        total_duration = main_event.end_time - main_event.start_time
    else:
        total_duration = 0
    
    # Main flow summary
    report.append(f"\n📋 MAIN FLOW: {main_event.name}")
    report.append(f"🕐 Start Time: {datetime.fromtimestamp(main_event.start_time).strftime('%Y-%m-%d %H:%M:%S')}")
    
    if main_event.error:
        report.append(f"❌ Status: FAILED")
        report.append(f"💥 Error: {main_event.error}")
    else:
        report.append(f"✅ Status: SUCCESS")
        
    report.append(f"⏱️  Total Duration: {format_duration(total_duration)}")
    
    if main_event.result:
        result_str = str(main_event.result)
        if len(result_str) > 100:
            result_str = result_str[:100] + "..."
        report.append(f"📤 Final Output: {result_str}")
    
    # Detailed step breakdown
    report.append(f"\n📝 EXECUTION STEPS")
    report.append("-" * 50)
    
    # Process all events in chronological order
    all_events = sorted(history.get_events(), key=lambda e: e.start_time)
    step_number = 0
    
    for event in all_events:
        if event.parent_id:  # Only show child steps, not the main flow again
            step_number += 1
            
            # Calculate step duration
            if event.end_time and event.start_time:
                step_duration = event.end_time - event.start_time
            else:
                step_duration = 0
            
            report.append(f"\n  📍 Step {step_number}: {event.name}")
            report.append(f"     ⏱️  Duration: {format_duration(step_duration)}")
            
            # Show inputs (abbreviated)
            if event.inputs:
                inputs_str = str(event.inputs)
                if len(inputs_str) > 150:
                    inputs_str = inputs_str[:150] + "..."
                report.append(f"     📥 Input: {inputs_str}")
            
            # Show status and output
            if event.error:
                report.append(f"     ❌ Status: FAILED")
                report.append(f"     💥 Error: {event.error}")
            else:
                report.append(f"     ✅ Status: SUCCESS")
                if event.result:
                    result_str = str(event.result)
                    if len(result_str) > 150:
                        result_str = result_str[:150] + "..."
                    report.append(f"     📤 Output: {result_str}")
    
    # Performance summary
    report.append(f"\n📊 PERFORMANCE SUMMARY")
    report.append("-" * 50)
    
    successful_steps = len([e for e in all_events if e.parent_id and not e.error])
    failed_steps = len([e for e in all_events if e.parent_id and e.error])
    total_steps = successful_steps + failed_steps
    
    report.append(f"✅ Successful Steps: {successful_steps}/{total_steps}")
    if failed_steps > 0:
        report.append(f"❌ Failed Steps: {failed_steps}/{total_steps}")
    
    if total_steps > 0:
        success_rate = (successful_steps / total_steps) * 100
        report.append(f"📈 Success Rate: {success_rate:.1f}%")
    
    # Add performance insights
    if total_duration > 0:
        avg_step_time = total_duration / max(total_steps, 1)
        report.append(f"⏱️  Average Step Time: {format_duration(avg_step_time)}")
    
    report.append("\n" + "=" * 70)
    return "\n".join(report)


def export_history_json(history: History) -> Dict[str, Any]:
    """
    Export Flow History to structured JSON format for programmatic analysis
    
    Args:
        history: Flow execution history
        
    Returns:
        Dictionary containing structured execution data
    """
    
    if not history.events:
        return {"error": "No execution events found"}
    
    root_events = history.get_root_events()
    if not root_events:
        return {"error": "No root events found"}
    
    main_event = root_events[0]
    
    # Build structured data
    data = {
        "execution_summary": {
            "main_flow": main_event.name,
            "start_time": main_event.start_time,
            "end_time": main_event.end_time,
            "duration": (main_event.end_time - main_event.start_time) if main_event.end_time else None,
            "status": "failed" if main_event.error else "success",
            "error": main_event.error,
            "result": main_event.result
        },
        "steps": [],
        "performance": {}
    }
    
    # Process steps
    step_events = [e for e in history.get_events() if e.parent_id]
    step_events.sort(key=lambda e: e.start_time)
    
    for i, event in enumerate(step_events):
        step_data = {
            "step_number": i + 1,
            "name": event.name,
            "start_time": event.start_time,
            "end_time": event.end_time,
            "duration": (event.end_time - event.start_time) if event.end_time else None,
            "status": "failed" if event.error else "success",
            "inputs": event.inputs,
            "result": event.result,
            "error": event.error
        }
        data["steps"].append(step_data)
    
    # Performance metrics
    successful_steps = len([s for s in data["steps"] if s["status"] == "success"])
    failed_steps = len([s for s in data["steps"] if s["status"] == "failed"])
    total_steps = len(data["steps"])
    
    data["performance"] = {
        "total_steps": total_steps,
        "successful_steps": successful_steps,
        "failed_steps": failed_steps,
        "success_rate": (successful_steps / total_steps * 100) if total_steps > 0 else 0,
        "average_step_duration": sum(s["duration"] or 0 for s in data["steps"]) / max(total_steps, 1)
    }
    
    return data


def save_execution_report(history: History, output_path: str, include_json: bool = True):
    """
    Save execution report to file(s)
    
    Args:
        history: Flow execution history
        output_path: Base path for output files (without extension)
        include_json: Whether to also save JSON format
    """
    
    # Save human-readable report
    report_content = format_flow_history(history)
    with open(f"{output_path}.txt", "w") as f:
        f.write(report_content)
    
    if include_json:
        # Save structured JSON data
        json_data = export_history_json(history)
        with open(f"{output_path}.json", "w") as f:
            json.dump(json_data, f, indent=2, default=str)
    
    logger.info(f"Execution report saved to: {output_path}.txt")
    if include_json:
        logger.info(f"JSON data saved to: {output_path}.json")


def analyze_performance_trends(history_files: List[str]) -> Dict[str, Any]:
    """
    Analyze performance trends across multiple execution history files
    
    Args:
        history_files: List of paths to JSON history files
        
    Returns:
        Performance trend analysis
    """
    
    all_executions = []
    
    for file_path in history_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if "execution_summary" in data:
                    all_executions.append(data)
        except Exception as e:
            logger.warning(f"Failed to load {file_path}: {e}")
    
    if not all_executions:
        return {"error": "No valid execution data found"}
    
    # Calculate trends
    total_executions = len(all_executions)
    successful_executions = len([e for e in all_executions if e["execution_summary"]["status"] == "success"])
    
    avg_duration = sum(e["execution_summary"]["duration"] or 0 for e in all_executions) / total_executions
    avg_steps = sum(e["performance"]["total_steps"] for e in all_executions) / total_executions
    avg_success_rate = sum(e["performance"]["success_rate"] for e in all_executions) / total_executions
    
    return {
        "trend_analysis": {
            "total_executions": total_executions,
            "overall_success_rate": (successful_executions / total_executions * 100),
            "average_execution_duration": avg_duration,
            "average_steps_per_execution": avg_steps,
            "average_step_success_rate": avg_success_rate
        },
        "recommendations": generate_performance_recommendations(all_executions)
    }


def generate_performance_recommendations(executions: List[Dict]) -> List[str]:
    """Generate performance improvement recommendations"""
    
    recommendations = []
    
    # Analyze common failure patterns
    failed_steps = []
    for execution in executions:
        for step in execution.get("steps", []):
            if step["status"] == "failed":
                failed_steps.append(step["name"])
    
    if failed_steps:
        from collections import Counter
        common_failures = Counter(failed_steps).most_common(3)
        recommendations.append(f"Most common failures: {[f[0] for f in common_failures]}")
    
    # Analyze duration patterns
    durations = [e["execution_summary"]["duration"] or 0 for e in executions]
    if durations:
        avg_duration = sum(durations) / len(durations)
        if avg_duration > 60:  # Over 1 minute
            recommendations.append("Consider optimizing long-running steps or implementing parallel processing")
    
    # Success rate analysis
    success_rates = [e["performance"]["success_rate"] for e in executions]
    if success_rates:
        avg_success_rate = sum(success_rates) / len(success_rates)
        if avg_success_rate < 90:
            recommendations.append("Implement more robust error handling and retry logic")
    
    return recommendations


def log_flow_history_as_json(history: History):
    """Parses the Flow History and logs it as a structured JSON object."""
    root_events = history.get_root_events()
    if not root_events:
        logger.error("No root events found in flow history")
        return
        
    root_event = root_events[0]
    
    event_log = {
        "main_flow_name": root_event.name,
        "status": "succeeded" if root_event.result is not None else "failed",
        "total_duration_sec": (root_event.end_time - root_event.start_time) if root_event.end_time else 0,
        "final_result": root_event.result,
        "error": root_event.error,
        "steps": []
    }

    for event in history.get_events():
        if event.parent_id:
            duration = (event.end_time - event.start_time) if event.end_time else 0
            event_log["steps"].append({
                "step_name": event.name,
                "duration_sec": duration,
                "status": "succeeded" if event.result is not None else "failed",
                "inputs": event.inputs,
                "output": event.result,
                "error": event.error,
            })
    
    # Log the entire structure as a single JSON line
    logger.info(json.dumps(event_log))


# Export main functions
__all__ = [
    'format_flow_history',
    'export_history_json', 
    'save_execution_report',
    'analyze_performance_trends',
    'log_flow_history_as_json'
]