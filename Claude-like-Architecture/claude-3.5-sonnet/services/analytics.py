# services/analytics.py
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json

class AnalyticsType(Enum):
    """Analytics type enumeration."""
    PERFORMANCE = "performance"
    USAGE = "usage"
    QUALITY = "quality"
    CUSTOM = "custom"

@dataclass
class AnalyticsMetric:
    """Individual analytics metric."""
    name: str
    value: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class AnalyticsReport:
    """Comprehensive analytics report."""
    metrics: List[AnalyticsMetric]
    summary: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime

class AnalyticsService:
    """Service for collecting and analyzing metrics."""

    def __init__(self):
        self.metrics: Dict[str, List[AnalyticsMetric]] = {}
        self.reports: List[AnalyticsReport] = []

    def track_metric(self, 
                    name: str,
                    value: float,
                    metadata: Optional[Dict[str, Any]] = None) -> None:
        """Track a new metric."""
        metric = AnalyticsMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(metric)

    def generate_report(self, 
                       metrics: Optional[List[str]] = None,
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None) -> AnalyticsReport:
        """Generate analytics report."""
        metrics_to_analyze = metrics or list(self.metrics.keys())
        collected_metrics = []
        
        for metric_name in metrics_to_analyze:
            if metric_name in self.metrics:
                metric_data = self.metrics[metric_name]
                if start_time:
                    metric_data = [m for m in metric_data if m.timestamp >= start_time]
                if end_time:
                    metric_data = [m for m in metric_data if m.timestamp <= end_time]
                collected_metrics.extend(metric_data)

        summary = self._generate_summary(collected_metrics)
        recommendations = self._generate_recommendations(summary)
        
        report = AnalyticsReport(
            metrics=collected_metrics,
            summary=summary,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
        
        self.reports.append(report)
        return report

    def get_metric_history(self, 
                          metric_name: str) -> List[AnalyticsMetric]:
        """Get history for specific metric."""
        return self.metrics.get(metric_name, [])

    def export_report(self, 
                     report: AnalyticsReport,
                     format: str = 'json') -> str:
        """Export report in specified format."""
        if format == 'json':
            return self._export_json(report)
        raise ValueError(f"Unsupported format: {format}")

    def clear_metrics(self, 
                     metric_names: Optional[List[str]] = None) -> None:
        """Clear metrics history."""
        if metric_names:
            for name in metric_names:
                self.metrics.pop(name, None)
        else:
            self.metrics.clear()

    def _generate_summary(self, 
                         metrics: List[AnalyticsMetric]) -> Dict[str, Any]:
        """Generate summary statistics."""
        summary = {}
        for metric in metrics:
            if metric.name not in summary:
                summary[metric.name] = {
                    'count': 0,
                    'sum': 0.0,
                    'min': float('inf'),
                    'max': float('-inf')
                }
            
            stats = summary[metric.name]
            stats['count'] += 1
            stats['sum'] += metric.value
            stats['min'] = min(stats['min'], metric.value)
            stats['max'] = max(stats['max'], metric.value)
            stats['avg'] = stats['sum'] / stats['count']
            
        return summary

    def _generate_recommendations(self, 
                                summary: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analytics."""
        recommendations = []
        for metric_name, stats in summary.items():
            if stats['count'] > 0:
                if stats['avg'] > stats['max'] * 0.8:
                    recommendations.append(
                        f"High average for {metric_name}: Consider optimization"
                    )
                if stats['max'] > stats['avg'] * 2:
                    recommendations.append(
                        f"Large variance in {metric_name}: Investigate spikes"
                    )
        return recommendations

    def _export_json(self, report: AnalyticsReport) -> str:
        """Export report as JSON."""
        return json.dumps({
            'timestamp': report.timestamp.isoformat(),
            'summary': report.summary,
            'recommendations': report.recommendations,
            'metrics': [
                {
                    'name': metric.name,
                    'value': metric.value,
                    'timestamp': metric.timestamp.isoformat(),
                    'metadata': metric.metadata
                }
                for metric in report.metrics
            ]
        }, indent=2)