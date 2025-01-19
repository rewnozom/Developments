# controllers/quality/metrics.py
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum
from core.exceptions import MetricsError

class MetricType(Enum):
    """Types of quality metrics."""
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    RELEVANCE = "relevance"
    CLARITY = "clarity"
    CUSTOM = "custom"

@dataclass
class Metric:
    """Individual metric measurement."""
    type: MetricType
    value: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class MetricsReport:
    """Comprehensive metrics report."""
    metrics: Dict[MetricType, Metric]
    averages: Dict[MetricType, float]
    trends: Dict[MetricType, float]
    timestamp: datetime

class QualityMetrics:
    """Handles quality metrics collection and analysis."""

    def __init__(self):
        self.metrics_history: Dict[UUID, Dict[MetricType, List[Metric]]] = {}
        self.custom_metrics: Dict[str, MetricType] = {}

    def track_metric(self,
                    content_id: UUID,
                    metric_type: Union[MetricType, str],
                    value: float,
                    metadata: Optional[Dict[str, Any]] = None) -> None:
        """Track quality metric."""
        try:
            # Validate content_id
            if not isinstance(content_id, UUID):
                raise MetricsError("Invalid content ID type")

            # Validate value
            if not isinstance(value, (int, float)):
                raise MetricsError("Value must be a number")

            # Convert string to MetricType if needed
            if isinstance(metric_type, str):
                try:
                    metric_type = self._get_metric_type(metric_type)
                except ValueError as e:
                    raise MetricsError(f"Invalid metric type: {str(e)}")

            # Validate metric type
            if not isinstance(metric_type, MetricType):
                raise MetricsError("Invalid metric type")

            # Validate metadata
            if metadata is not None and not isinstance(metadata, dict):
                raise MetricsError("Metadata must be a dictionary")

            # Initialize history if needed
            if content_id not in self.metrics_history:
                self.metrics_history[content_id] = {
                    type_: [] for type_ in MetricType
                }

            # Create metric
            try:
                metric = Metric(
                    type=metric_type,
                    value=float(value),
                    timestamp=datetime.now(),
                    metadata=metadata or {}
                )
            except Exception as e:
                raise MetricsError(f"Failed to create metric: {str(e)}")

            # Store metric
            try:
                self.metrics_history[content_id][metric_type].append(metric)
            except Exception as e:
                raise MetricsError(f"Failed to store metric: {str(e)}")

        except MetricsError:
            raise
        except Exception as e:
            raise MetricsError(f"Failed to track metric: {str(e)}")

    def get_metrics(self,
                   content_id: UUID,
                   metric_type: Optional[Union[MetricType, str]] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> List[Metric]:
        """Get metrics history."""
        try:
            if content_id not in self.metrics_history:
                return []

            # Convert string to MetricType if needed
            if isinstance(metric_type, str):
                metric_type = self._get_metric_type(metric_type)

            # Get metrics
            metrics = []
            types_to_get = ([metric_type] if metric_type 
                          else [type_ for type_ in MetricType])

            for type_ in types_to_get:
                type_metrics = self.metrics_history[content_id][type_]
                
                # Apply time filters
                if start_time:
                    type_metrics = [m for m in type_metrics 
                                  if m.timestamp >= start_time]
                if end_time:
                    type_metrics = [m for m in type_metrics 
                                  if m.timestamp <= end_time]
                    
                metrics.extend(type_metrics)

            return sorted(metrics, key=lambda m: m.timestamp)

        except Exception as e:
            raise MetricsError(f"Failed to export metrics: {str(e)}")

    def import_metrics(self,
                        content_id: UUID,
                        data: str,
                        format: str = 'json') -> int:
        """Import metrics data."""
        try:
            imported = 0
            if format == 'json':
                import json
                metrics_data = json.loads(data)
                for metric in metrics_data:
                    self.track_metric(
                        content_id,
                        metric['type'],
                        metric['value'],
                        metric.get('metadata')
                    )
                    imported += 1
                    
            elif format == 'csv':
                import csv
                import io
                reader = csv.reader(io.StringIO(data))
                next(reader)  # Skip header
                for row in reader:
                    self.track_metric(
                        content_id,
                        row[0],
                        float(row[1]),
                        eval(row[3]) if row[3] else None
                    )
                    imported += 1
                    
            else:
                raise ValueError(f"Unsupported import format: {format}")
                
            return imported

        except Exception as e:
            raise MetricsError(f"Failed to import metrics: {str(e)}")
