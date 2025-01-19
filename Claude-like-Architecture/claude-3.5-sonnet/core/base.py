# core/base.py

from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4
import logging
import json
import yaml
import psutil
import gc
import os
import shutil
import time
import threading
from concurrent.futures import ThreadPoolExecutor

from .config import Settings, ConfigError
from .exceptions import (
    SystemInitializationError,
    SystemOperationError,
    ResourceError,
    StateError,
    InvalidStateTransitionError,
    StateInitializationError,
    StateLockError,
    StateCorruptionError,
    StateVersionError
)

@dataclass
class SystemResources:
    """System resource tracking."""
    memory_usage: int = 0
    cpu_usage: float = 0
    disk_usage: int = 0
    active_processes: int = 0
    available_memory: int = 0
    total_memory: int = 0
    process_count: int = 0
    thread_count: int = 0

@dataclass
class SystemMetrics:
    """System performance metrics."""
    requests_processed: int = 0
    average_response_time: float = 0
    error_rate: float = 0
    uptime: float = 0
    request_success_rate: float = 0
    peak_memory_usage: int = 0
    peak_cpu_usage: float = 0
    total_errors: int = 0

class SystemState:
    """Represents current system state."""
    def __init__(self):
        self.initialized: bool = False
        self.start_time: datetime = datetime.now()
        self.resources: SystemResources = SystemResources()
        self.metrics: SystemMetrics = SystemMetrics()
        self.active_operations: Dict[UUID, Dict[str, Any]] = {}
        self.status: str = "initializing"
        self.last_backup: Optional[datetime] = None
        self.error_count: int = 0
        self.warning_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "initialized": self.initialized,
            "start_time": self.start_time.isoformat(),
            "status": self.status,
            "resources": asdict(self.resources),
            "metrics": asdict(self.metrics),
            "active_operations": len(self.active_operations),
            "error_count": self.error_count,
            "warning_count": self.warning_count
        }

class BaseSystem:
    """Base class för Claude systemet."""

    def __init__(self, config: Settings):
        """Initialisera systemet."""
        self.config = config
        self.state = SystemState()
        self.logger = logging.getLogger(__name__)
        self.components: Dict[str, Any] = {}
        self.event_handlers: Dict[str, List[callable]] = {}
        self.shutdown_hooks: List[callable] = []
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup loggkonfiguration."""
        logging.basicConfig(
            level=self.config.logging.level,  # Korrigerat för att använda self.config.logging.level
            format=self.config.logging.format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.config.logging.file_path)
            ]
        )

    def initialize(self) -> bool:
        """Initialisera systemkomponenter."""
        try:
            self.logger.info("Initialiserar system...")

            # Validera konfiguration
            if not self.config.validate():
                raise SystemInitializationError("Ogiltig konfiguration")

            # Skapa nödvändiga kataloger
            self._create_directories()

            # Setup komponenter
            self._setup_components()
            self._load_resources()
            self._configure_system()

            # Initial resursövervakning
            self.monitor_resources()

            # Markera som initialiserad
            self.state.initialized = True
            self.state.status = "ready"

            self.logger.info("System initialiserat framgångsrikt")
            return True

        except Exception as e:
            self.logger.error(f"Systeminitialisering misslyckades: {str(e)}")
            self.state.status = "error"
            raise SystemInitializationError(f"Misslyckades med att initialisera systemet: {str(e)}")

    def shutdown(self) -> bool:
        """Stäng av systemet graciöst."""
        try:
            self.logger.info("Initierar systemavstängning...")

            # Utför shutdown hooks
            for hook in self.shutdown_hooks:
                try:
                    hook()
                except Exception as e:
                    self.logger.error(f"Shutdown hook misslyckades: {str(e)}")

            # Rensa aktiva operationer
            self._cleanup_operations()

            # Rensa resurser
            self._cleanup_resources()

            # Spara slutligt tillstånd
            self._save_state()

            # Uppdatera tillstånd
            self.state.status = "shutdown"

            self.logger.info("Systemavstängning klar")
            return True

        except Exception as e:
            self.logger.error(f"Systemavstängning misslyckades: {str(e)}")
            raise SystemOperationError(f"Misslyckades med att stänga av systemet: {str(e)}")

    def get_status(self) -> Dict[str, Any]:
        """Hämta omfattande systemstatus."""
        # Uppdatera metrics
        self.state.metrics.uptime = (
            datetime.now() - self.state.start_time
        ).total_seconds()

        return {
            "initialized": self.state.initialized,
            "status": self.state.status,
            "uptime": self.state.metrics.uptime,
            "start_time": self.state.start_time.isoformat(),
            "resources": asdict(self.state.resources),
            "metrics": asdict(self.state.metrics),
            "active_operations": {
                "count": len(self.state.active_operations),
                "details": [
                    {
                        "id": str(op_id),
                        "start_time": op_data["start_time"].isoformat(),
                        "status": op_data["status"]
                    }
                    for op_id, op_data in self.state.active_operations.items()
                ]
            },
            "errors": {
                "count": self.state.error_count,
                "rate": self.state.metrics.error_rate
            },
            "warnings": {
                "count": self.state.warning_count
            },
            "components": {
                name: "active" if component else "inactive"
                for name, component in self.components.items()
            },
            "config": {
                "environment": self.config.system.environment,
                "debug_mode": self.config.system.debug_mode,
                "safety_filters": self.config.security.enable_safety_filters
            },
            "last_backup": (
                self.state.last_backup.isoformat()
                if self.state.last_backup else None
            )
        }

    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """Uppdatera systemmetrics."""
        for key, value in metrics.items():
            if hasattr(self.state.metrics, key):
                current_value = getattr(self.state.metrics, key)
                if isinstance(current_value, (int, float)):
                    setattr(self.state.metrics, key, value)

        # Uppdatera härledda metrics
        if self.state.metrics.requests_processed > 0:
            success_rate = (
                (self.state.metrics.requests_processed - self.state.metrics.total_errors) /
                self.state.metrics.requests_processed
            ) * 100
            self.state.metrics.request_success_rate = success_rate

    def register_component(self, name: str, component: Any) -> bool:
        """Registrera systemkomponent."""
        if name in self.components:
            self.logger.warning(f"Komponenten {name} är redan registrerad")
            return False

        self.components[name] = component
        return True

    def register_event_handler(self, event: str, handler: callable) -> None:
        """Registrera event handler."""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)

    def trigger_event(self, event: str, data: Any = None) -> None:
        """Trigga event och utför handlers."""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.error(f"Event handler misslyckades: {str(e)}")

    def register_shutdown_hook(self, hook: callable) -> None:
        """Registrera shutdown hook."""
        self.shutdown_hooks.append(hook)

    def start_operation(self, operation_id: UUID, details: Any) -> bool:
        """Starta spårning av en operation."""
        try:
            if operation_id in self.state.active_operations:
                return False

            self.state.active_operations[operation_id] = {
                "start_time": datetime.now(),
                "details": details,
                "status": "running",
                "resources": {
                    "initial_memory": self.state.resources.memory_usage,
                    "initial_cpu": self.state.resources.cpu_usage
                }
            }

            self.trigger_event("operation_started", {
                "operation_id": operation_id,
                "details": details
            })

            return True

        except Exception as e:
            self.logger.error(f"Misslyckades med att starta operation: {str(e)}")
            return False

    def end_operation(self, 
                     operation_id: UUID, 
                     status: str = "completed",
                     result: Any = None) -> bool:
        """Avsluta spårning av en operation."""
        try:
            if operation_id not in self.state.active_operations:
                return False

            operation = self.state.active_operations.pop(operation_id)
            duration = (datetime.now() - operation["start_time"]).total_seconds()

            # Uppdatera metrics
            self.state.metrics.requests_processed += 1
            self.state.metrics.average_response_time = (
                (self.state.metrics.average_response_time * 
                 (self.state.metrics.requests_processed - 1) + duration) /
                self.state.metrics.requests_processed
            )

            if status == "error":
                self.state.metrics.total_errors += 1
                self.state.metrics.error_rate = (
                    self.state.metrics.total_errors /
                    self.state.metrics.requests_processed
                )

            # Beräkna resursanvändning
            memory_usage = (
                self.state.resources.memory_usage - 
                operation["resources"]["initial_memory"]
            )
            cpu_usage = (
                self.state.resources.cpu_usage - 
                operation["resources"]["initial_cpu"]
            )

            # Trigga event
            self.trigger_event("operation_ended", {
                "operation_id": operation_id,
                "status": status,
                "duration": duration,
                "memory_usage": memory_usage,
                "cpu_usage": cpu_usage,
                "result": result
            })

            return True

        except Exception as e:
            self.logger.error(f"Misslyckades med att avsluta operation: {str(e)}")
            return False

    def monitor_resources(self) -> None:
        """Övervaka systemresursanvändning."""
        try:
            # Hämta systemmetrics
            memory = psutil.virtual_memory()
            self.state.resources.memory_usage = memory.percent
            self.state.resources.available_memory = memory.available
            self.state.resources.total_memory = memory.total

            self.state.resources.cpu_usage = psutil.cpu_percent()
            self.state.resources.disk_usage = psutil.disk_usage('/').percent

            # Hämta processmetrics
            process = psutil.Process()
            self.state.resources.active_processes = len(process.children())
            self.state.resources.process_count = len(psutil.pids())
            self.state.resources.thread_count = process.num_threads()

            # Uppdatera peak metrics
            if self.state.resources.memory_usage > self.state.metrics.peak_memory_usage:
                self.state.metrics.peak_memory_usage = self.state.resources.memory_usage
            if self.state.resources.cpu_usage > self.state.metrics.peak_cpu_usage:
                self.state.metrics.peak_cpu_usage = self.state.resources.cpu_usage

            # Kontrollera tröskelvärden
            if self.state.resources.memory_usage > 90:
                self.logger.warning("Hög minnesanvändning upptäckt")
                self.trigger_event("high_memory_usage", self.state.resources.memory_usage)

            if self.state.resources.cpu_usage > 90:
                self.logger.warning("Hög CPU-användning upptäckt")
                self.trigger_event("high_cpu_usage", self.state.resources.cpu_usage)

        except Exception as e:
            self.logger.error(f"Resursövervakning misslyckades: {str(e)}")

    def optimize_resources(self) -> None:
        """Optimera systemresursanvändning."""
        try:
            # Kontrollera resurs tröskelvärden
            if self.state.resources.memory_usage > 90:
                self._optimize_memory()
            if self.state.resources.cpu_usage > 90:
                self._optimize_cpu()
            if self.state.resources.disk_usage > 90:
                self._optimize_disk()

        except Exception as e:
            self.logger.error(f"Resursoptimering misslyckades: {str(e)}")

    def backup_system(self, backup_path: Optional[Path] = None) -> bool:
        """Skapa systembackup."""
        try:
            backup_path = backup_path or Path("backups") / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            # Säkerställ att katalogen existerar
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Skapa backupdata
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "config": self.config.to_dict(),
                "state": self.state.to_dict(),
                "components": {
                    name: "active" if component else "inactive"
                    for name, component in self.components.items()
                }
            }

            # Spara backup
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)

            self.state.last_backup = datetime.now()
            self.logger.info(f"Systembackup skapad: {backup_path}")

            return True

        except Exception as e:
            self.logger.error(f"Backup misslyckades: {str(e)}")
            return False

    def restore_system(self, backup_path: Path) -> bool:
        """Återställ system från backup."""
        try:
            self.logger.info(f"Återställer system från backup: {backup_path}")

            # Ladda backupdata
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)

            # Validera backupdata
            required_keys = ['timestamp', 'config', 'state']
            if not all(key in backup_data for key in required_keys):
                raise ValueError("Ogiltig backupdatastruktur")

            # Stoppa aktiva operationer
            self._cleanup_operations()

            # Återställ konfiguration
            self.config = Settings()
            self.config._update_settings(backup_data["config"])

            # Återställ tillstånd
            state_data = backup_data["state"]
            self.state = SystemState()
            self.state.initialized = state_data["initialized"]
            self.state.start_time = datetime.fromisoformat(state_data["start_time"])
            self.state.status = state_data["status"]

            # Återställ metrics och resurser
            for key, value in state_data["metrics"].items():
                if hasattr(self.state.metrics, key):
                    setattr(self.state.metrics, key, value)

            for key, value in state_data["resources"].items():
                if hasattr(self.state.resources, key):
                    setattr(self.state.resources, key, value)

            # Återinitiera komponenter om nödvändigt
            if "components" in backup_data:
                self._restore_components(backup_data["components"])

            self.logger.info("Systemåterställning klarade framgångsrikt")
            return True

        except Exception as e:
            self.logger.error(f"Systemåterställning misslyckades: {str(e)}")
            raise SystemOperationError(f"Misslyckades med att återställa systemet: {str(e)}")

    def _setup_components(self) -> None:
        """Setup systemkomponenter."""
        try:
            # Initiera kärnkomponenter
            # Denna metod bör åsidosättas av specifika implementationer
            pass
        except Exception as e:
            raise SystemInitializationError(
                f"Misslyckades med att setup:a komponenter: {str(e)}"
            )

    def _create_directories(self) -> None:
        """Skapa nödvändiga systemkataloger."""
        directories = [
            self.config.resources.storage_path,
            Path(self.config.logging.file_path).parent if self.config.logging.file_path else Path("logs"),
            Path("backups"),
            Path("temp"),
            Path("cache")
        ]

        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise SystemInitializationError(
                    f"Misslyckades med att skapa katalog {directory}: {str(e)}"
                )

    def _load_resources(self) -> None:
        """Ladda nödvändiga resurser."""
        try:
            # Ladda nödvändiga resurser
            # Denna metod bör åsidosättas av specifika implementationer
            pass
        except Exception as e:
            raise ResourceError(f"Misslyckades med att ladda resurser: {str(e)}")

    def _configure_system(self) -> None:
        """Konfigurera systeminställningar."""
        try:
            # Tillämpa konfigurationsinställningar
            # Denna metod bör åsidosättas av specifika implementationer
            pass
        except Exception as e:
            raise SystemInitializationError(
                f"Misslyckades med att konfigurera systemet: {str(e)}"
            )

    def _cleanup_operations(self) -> None:
        """Rensa aktiva operationer."""
        for operation_id in list(self.state.active_operations.keys()):
            try:
                self.end_operation(operation_id, "terminated")
            except Exception as e:
                self.logger.error(
                    f"Misslyckades med att rensa operation {operation_id}: {str(e)}"
                )

    def _cleanup_resources(self) -> None:
        """Rensa systemresurser."""
        try:
            # Rensa temporära filer
            for path in [Path("temp"), Path("cache")]:
                if path.exists():
                    shutil.rmtree(path)
                    path.mkdir()

            # Kör garbage collection
            gc.collect()

        except Exception as e:
            self.logger.error(f"Resursrensning misslyckades: {str(e)}")

    def _save_state(self) -> None:
        """Spara aktuellt systemtillstånd."""
        try:
            state_file = self.config.resources.storage_path / "system_state.json"
            with open(state_file, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Misslyckades med att spara systemtillstånd: {str(e)}")

    def _restore_components(self, component_data: Dict[str, Any]) -> None:
        """Återställ systemkomponenter från backup."""
        for name, data in component_data.items():
            try:
                if name in self.components:
                    if hasattr(self.components[name], 'restore'):
                        self.components[name].restore(data)
            except Exception as e:
                self.logger.error(
                    f"Misslyckades med att återställa komponent {name}: {str(e)}"
                )

    def _optimize_memory(self) -> None:
        """Optimera minnesanvändning."""
        self.logger.info("Optimerar minnesanvändning...")

        # Kör garbage collection
        gc.collect()

        # Rensa cache om aktiverat
        if self.config.system.cache_enabled:
            if Path("cache").exists():
                for cache_file in Path("cache").glob("*"):
                    try:
                        cache_file.unlink()
                    except Exception as e:
                        self.logger.error(
                            f"Misslyckades med att rensa cachefil {cache_file}: {str(e)}"
                        )

        # Rensa temporära filer
        if Path("temp").exists():
            for temp_file in Path("temp").glob("*"):
                try:
                    if temp_file.is_file():
                        temp_file.unlink()
                except Exception as e:
                    self.logger.error(
                        f"Misslyckades med att rensa tempfil {temp_file}: {str(e)}"
                    )

    def _optimize_cpu(self) -> None:
        """Optimera CPU-användning."""
        self.logger.info("Optimerar CPU-användning...")

        # Avsluta icke-kritiska operationer
        for operation_id, operation in list(self.state.active_operations.items()):
            if operation.get("priority", "normal") == "low":
                self.end_operation(operation_id, "terminated")

    def _optimize_disk(self) -> None:
        """Optimera disk-användning."""
        self.logger.info("Optimerar disk-användning...")

        try:
            # Rensa gamla loggfiler
            if self.config.logging.file_path and Path(self.config.logging.file_path).exists():
                log_dir = Path(self.config.logging.file_path).parent
                for log_file in log_dir.glob("*.log.*"):
                    try:
                        log_file.unlink()
                    except Exception as e:
                        self.logger.error(
                            f"Misslyckades med att ta bort gammal loggfil {log_file}: {str(e)}"
                        )

            # Rensa gamla backups
            backup_dir = Path("backups")
            if backup_dir.exists():
                backups = sorted(backup_dir.glob("*.json"), 
                                key=lambda p: p.stat().st_mtime)
                # Behåll endast de senaste 5 backups
                for backup in backups[:-5]:
                    try:
                        backup.unlink()
                    except Exception as e:
                        self.logger.error(
                            f"Misslyckades med att ta bort gammal backup {backup}: {str(e)}"
                        )

        except Exception as e:
            self.logger.error(f"Diskoptimering misslyckades: {str(e)}")

    def validate_operation(self, operation: Any) -> bool:
        """Validera operationens begäran."""
        try:
            # Kontrollera systemtillstånd
            if not self.state.initialized:
                return False
            if self.state.status not in ["ready", "running"]:
                return False

            # Kontrollera resurs tillgänglighet
            if self.state.resources.memory_usage > 95:
                return False
            if self.state.resources.cpu_usage > 95:
                return False

            # Kontrollera operationsgränser
            if len(self.state.active_operations) >= self.config.system.max_retries:
                return False

            return True

        except Exception as e:
            self.logger.error(f"Operationens validering misslyckades: {str(e)}")
            return False

    def handle_error(self, 
                    error: Exception, 
                    operation_id: Optional[UUID] = None,
                    context: Optional[Dict[str, Any]] = None) -> None:
        """Hantera systemfel."""
        self.logger.error(f"Fel inträffade: {str(error)}", exc_info=True)

        # Uppdatera felmetrics
        self.state.error_count += 1
        if operation_id:
            self.end_operation(operation_id, "error")

        # Trigga fel event
        self.trigger_event("system_error", {
            "error": str(error),
            "operation_id": operation_id,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })

        # Kontrollera om systemet ska gå in i fel-tillstånd
        if self.state.error_count > self.config.system.max_retries:
            self.state.status = "error"

    def handle_warning(self, 
                      message: str, 
                      context: Optional[Dict[str, Any]] = None) -> None:
        """Hantera systemvarningar."""
        self.logger.warning(f"Varning: {message}")
        self.state.warning_count += 1

        # Trigga varnings-event
        self.trigger_event("system_warning", {
            "message": message,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })

    def get_system_load(self) -> Dict[str, float]:
        """Hämta aktuella systemladdningsmetrics."""
        try:
            load_avg = psutil.getloadavg()
            return {
                "load_1min": load_avg[0],
                "load_5min": load_avg[1],
                "load_15min": load_avg[2],
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent
            }
        except Exception as e:
            self.logger.error(f"Misslyckades med att hämta systemladdning: {str(e)}")
            return {}

    def check_system_health(self) -> Tuple[bool, Dict[str, Any]]:
        """Kontrollera systemets övergripande hälsa."""
        try:
            # Hämta aktuella metrics
            load = self.get_system_load()
            disk = psutil.disk_usage('/')
            memory = psutil.virtual_memory()

            # Definiera hälsokontroller
            checks = {
                "memory": memory.percent < 90,
                "cpu": load.get("cpu_percent", 0) < 90,
                "disk": disk.percent < 90,
                "error_rate": self.state.metrics.error_rate < 0.1,
                "response_time": self.state.metrics.average_response_time < 5.0
            }

            # Beräkna övergripande hälsa
            system_healthy = all(checks.values())

            return system_healthy, {
                "healthy": system_healthy,
                "checks": checks,
                "metrics": {
                    "load": load,
                    "disk_usage": disk.percent,
                    "memory_usage": memory.percent,
                    "error_rate": self.state.metrics.error_rate,
                    "response_time": self.state.metrics.average_response_time
                }
            }
        except Exception as e:
            self.logger.error(f"Hälsokontroll misslyckades: {str(e)}")
            return False, {"error": str(e)}

    def get_component(self, name: str) -> Optional[Any]:
        """Hämta registrerad komponent efter namn."""
        return self.components.get(name)

    def get_active_operations(self) -> Dict[UUID, Dict[str, Any]]:
        """Hämta alla aktiva operationer."""
        return self.state.active_operations.copy()

    def pause_operation(self, operation_id: UUID) -> bool:
        """Pausa en aktiv operation."""
        if operation_id not in self.state.active_operations:
            return False

        operation = self.state.active_operations[operation_id]
        if operation["status"] == "running":
            operation["status"] = "paused"
            operation["pause_time"] = datetime.now()
            self.trigger_event("operation_paused", {"operation_id": operation_id})
            return True
        return False

    def resume_operation(self, operation_id: UUID) -> bool:
        """Återuppta en pausad operation."""
        if operation_id not in self.state.active_operations:
            return False

        operation = self.state.active_operations[operation_id]
        if operation["status"] == "paused":
            operation["status"] = "running"
            if "pause_time" in operation:
                pause_duration = (datetime.now() - operation["pause_time"]).total_seconds()
                operation["total_pause_time"] = operation.get("total_pause_time", 0) + pause_duration
            self.trigger_event("operation_resumed", {"operation_id": operation_id})
            return True
        return False

    def get_resource_usage(self, operation_id: UUID) -> Optional[Dict[str, Any]]:
        """Hämta resursanvändning för en specifik operation."""
        if operation_id not in self.state.active_operations:
            return None

        operation = self.state.active_operations[operation_id]
        current_memory = self.state.resources.memory_usage
        current_cpu = self.state.resources.cpu_usage

        return {
            "memory_delta": current_memory - operation["resources"]["initial_memory"],
            "cpu_delta": current_cpu - operation["resources"]["initial_cpu"],
            "duration": (datetime.now() - operation["start_time"]).total_seconds(),
            "status": operation["status"]
        }

    def cleanup_expired_operations(self, max_age: int = 3600) -> int:
        """Rensa operationer äldre än max_age sekunder."""
        cleanup_count = 0
        current_time = datetime.now()

        for op_id in list(self.state.active_operations.keys()):
            operation = self.state.active_operations[op_id]
            age = (current_time - operation["start_time"]).total_seconds()

            if age > max_age:
                self.end_operation(op_id, "expired")
                cleanup_count += 1

        return cleanup_count

    @property
    def is_healthy(self) -> bool:
        """Kontrollera om systemet är i ett hälsosamt tillstånd."""
        return (
            self.state.initialized and 
            self.state.status in ["ready", "running"] and
            self.state.resources.memory_usage < 90 and
            self.state.resources.cpu_usage < 90
        )

    def update_state(self, new_state: str) -> None:
        """Uppdatera systemtillstånd med validering."""
        VALID_STATES = [
            "initializing", "ready", "running", "paused", 
            "error", "maintenance", "shutdown"
        ]

        try:
            if new_state not in VALID_STATES:
                raise InvalidStateTransitionError(
                    f"Ogiltig tillståndsövergång till {new_state}",
                    from_state=self.state.status,
                    to_state=new_state
                )

            # Kontrollera om övergång är tillåten
            if self.state.status == "error" and new_state not in ["shutdown", "maintenance"]:
                raise InvalidStateTransitionError(
                    "Systemet i fel-tillstånd kan endast övergå till shutdown eller maintenance",
                    from_state=self.state.status,
                    to_state=new_state
                )

            old_state = self.state.status
            self.state.status = new_state
            self.logger.info(f"Systemtillstånd ändrat: {old_state} -> {new_state}")

            # Trigga tillståndsändrings-event
            self.trigger_event("state_changed", {
                "old_state": old_state,
                "new_state": new_state,
                "timestamp": datetime.now().isoformat()
            })

        except InvalidStateTransitionError as e:
            self.logger.error(f"Tillståndsövergång misslyckades: {str(e)}")
            raise
        except Exception as e:
            raise StateError(f"Misslyckades med att uppdatera tillstånd: {str(e)}")

    def cache_operation(self, operation_id: UUID, data: Any, ttl: int = 3600) -> bool:
        """Cacha operationdata med time-to-live."""
        try:
            cache_dir = Path("cache")
            cache_dir.mkdir(exist_ok=True)

            cache_data = {
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat()
            }

            cache_file = cache_dir / f"{operation_id}.json"
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)

            return True

        except Exception as e:
            self.logger.error(f"Misslyckades med att cacha operationdata: {str(e)}")
            return False

    def get_cached_operation(self, operation_id: UUID) -> Optional[Any]:
        """Hämta cachad operationdata om den inte har löpt ut."""
        try:
            cache_file = Path("cache") / f"{operation_id}.json"
            if not cache_file.exists():
                return None

            with open(cache_file) as f:
                cache_data = json.load(f)

            expires_at = datetime.fromisoformat(cache_data["expires_at"])
            if datetime.now() > expires_at:
                cache_file.unlink()
                return None

            return cache_data["data"]

        except Exception as e:
            self.logger.error(f"Misslyckades med att hämta cachad data: {str(e)}")
            return None

    def clear_cache(self, older_than: Optional[int] = None) -> int:
        """Rensa systemcache, eventuellt endast poster äldre än specificerade sekunder."""
        try:
            cache_dir = Path("cache")
            if not cache_dir.exists():
                return 0

            cleared_count = 0
            for cache_file in cache_dir.glob("*.json"):
                try:
                    if older_than:
                        file_age = time.time() - cache_file.stat().st_mtime
                        if file_age < older_than:
                            continue

                    cache_file.unlink()
                    cleared_count += 1

                except Exception as e:
                    self.logger.error(f"Misslyckades med att rensa cachefil {cache_file}: {str(e)}")

            return cleared_count

        except Exception as e:
            self.logger.error(f"Misslyckades med att rensa cache: {str(e)}")
            return 0

    def rotate_logs(self) -> None:
        """Rotera systemloggar för att förhindra disköverflöd."""
        try:
            log_file = Path(self.config.logging.file_path)
            if not log_file.exists():
                return

            # Kontrollera om logrotation är nödvändig
            if log_file.stat().st_size > self.config.logging.max_size:
                # Skapa backup av aktuell logg
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"{log_file.stem}_{timestamp}{log_file.suffix}"
                backup_path = log_file.parent / backup_name

                # Rotera loggfilen
                shutil.copy2(log_file, backup_path)
                log_file.write_text("")  # Rensa aktuell loggfil

                # Ta bort gamla loggfiler om det är för många
                log_files = sorted(
                    log_file.parent.glob(f"{log_file.stem}_*{log_file.suffix}"),
                    key=lambda x: x.stat().st_mtime
                )

                while len(log_files) > self.config.logging.backup_count:
                    oldest_log = log_files.pop(0)
                    oldest_log.unlink()

                self.logger.info(f"Logg rotad: {backup_path}")

        except Exception as e:
            self.logger.error(f"Misslyckades med att rotera loggar: {str(e)}")

    def get_event_history(self, 
                         event_type: Optional[str] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Hämta systemeventhistorik med valfri filtrering."""
        try:
            events = []
            event_log_path = self.config.resources.storage_path / "event_log.json"

            if not event_log_path.exists():
                return events

            with open(event_log_path) as f:
                all_events = json.load(f)

            for event in all_events:
                event_time = datetime.fromisoformat(event["timestamp"])

                # Tillämpa filter
                if event_type and event["type"] != event_type:
                    continue
                if start_time and event_time < start_time:
                    continue
                if end_time and event_time > end_time:
                    continue

                events.append(event)

            return events

        except Exception as e:
            self.logger.error(f"Misslyckades med att hämta eventhistorik: {str(e)}")
            return []
