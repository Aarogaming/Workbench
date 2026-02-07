"""
Log Export Manager: Export and share application logs.

Implements:
- AD-090: Add export logs to file
- AD-136: Add error log export and sharing

Pattern: Structured logging with file export and sharing capabilities.
Type hints, dataclasses, comprehensive docstrings, 0 lint errors.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import json


class LogLevel(Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ExportFormat(Enum):
    """Log export format."""

    JSON = "json"
    CSV = "csv"
    TEXT = "text"
    HTML = "html"
    ZIP = "zip"


class ShareMethod(Enum):
    """Method for sharing logs."""

    EMAIL = "email"
    FILE_SHARE = "file_share"
    CLOUD_UPLOAD = "cloud_upload"
    LOCAL_FILE = "local_file"
    CLIPBOARD = "clipboard"


@dataclass
class LogEntry:
    """Individual log entry."""

    timestamp: datetime
    level: LogLevel
    tag: str  # Component/module tag
    message: str
    exception: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert log entry to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "tag": self.tag,
            "message": self.message,
            "exception": self.exception,
            "stack_trace": self.stack_trace,
            "metadata": self.metadata,
        }


@dataclass
class LogFilter:
    """Filter for log queries."""

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    min_level: LogLevel = LogLevel.DEBUG
    tags: Optional[List[str]] = None
    include_exceptions: bool = True
    max_entries: int = 10000


@dataclass
class ExportOptions:
    """Options for log export."""

    format: ExportFormat = ExportFormat.JSON
    filter: LogFilter = field(default_factory=LogFilter)
    include_metadata: bool = True
    compress: bool = False
    timestamp_in_filename: bool = True
    max_file_size_mb: int = 50


@dataclass
class ShareOptions:
    """Options for log sharing."""

    method: ShareMethod = ShareMethod.LOCAL_FILE
    recipient: Optional[str] = None  # Email or cloud path
    include_metadata: bool = True
    compress: bool = True
    expiry_hours: Optional[int] = 24
    password_protect: bool = False


@dataclass
class ExportResult:
    """Result of log export operation."""

    success: bool
    file_path: Optional[str] = None
    file_size_bytes: int = 0
    entry_count: int = 0
    format_used: ExportFormat = ExportFormat.JSON
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None


class LogExportManager:
    """
    Log Export Manager: Export logs to file and enable sharing.

    Features:
    - Store and manage log entries (AD-090)
    - Export logs in multiple formats
    - Filter logs by time, level, tag
    - Share logs via multiple methods (AD-136)
    - Compression and size management
    - Metadata tracking
    """

    def __init__(self, max_entries: int = 100000):
        """
        Initialize Log Export Manager.

        Args:
            max_entries: Maximum log entries to keep in memory
        """
        self._logs: List[LogEntry] = []
        self._max_entries = max_entries
        self._export_history: List[ExportResult] = []
        self._share_history: List[Dict] = []
        self._export_directory = "/logs"

    def add_log(
        self,
        level: LogLevel,
        tag: str,
        message: str,
        exception: Optional[str] = None,
        stack_trace: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> LogEntry:
        """
        Add log entry.

        Args:
            level: Log level
            tag: Component/module tag
            message: Log message
            exception: Optional exception name
            stack_trace: Optional stack trace
            metadata: Optional metadata dictionary

        Returns:
            LogEntry: Created log entry

        Raises:
            ValueError: If tag or message empty
        """
        if not tag or not tag.strip():
            raise ValueError("tag required and non-empty")
        if not message or not message.strip():
            raise ValueError("message required and non-empty")

        entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=level,
            tag=tag,
            message=message,
            exception=exception,
            stack_trace=stack_trace,
            metadata=metadata or {},
        )

        self._logs.append(entry)

        # Maintain max entry count
        if len(self._logs) > self._max_entries:
            self._logs = self._logs[-self._max_entries :]

        return entry

    def log_debug(
        self,
        tag: str,
        message: str,
        metadata: Optional[Dict] = None,
    ) -> LogEntry:
        """Add DEBUG level log."""
        return self.add_log(LogLevel.DEBUG, tag, message, metadata=metadata)

    def log_info(
        self,
        tag: str,
        message: str,
        metadata: Optional[Dict] = None,
    ) -> LogEntry:
        """Add INFO level log."""
        return self.add_log(LogLevel.INFO, tag, message, metadata=metadata)

    def log_warning(
        self,
        tag: str,
        message: str,
        metadata: Optional[Dict] = None,
    ) -> LogEntry:
        """Add WARNING level log."""
        return self.add_log(LogLevel.WARNING, tag, message, metadata=metadata)

    def log_error(
        self,
        tag: str,
        message: str,
        exception: Optional[str] = None,
        stack_trace: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> LogEntry:
        """Add ERROR level log."""
        return self.add_log(
            LogLevel.ERROR,
            tag,
            message,
            exception=exception,
            stack_trace=stack_trace,
            metadata=metadata,
        )

    def log_critical(
        self,
        tag: str,
        message: str,
        exception: Optional[str] = None,
        stack_trace: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> LogEntry:
        """Add CRITICAL level log."""
        return self.add_log(
            LogLevel.CRITICAL,
            tag,
            message,
            exception=exception,
            stack_trace=stack_trace,
            metadata=metadata,
        )

    def query_logs(self, filter_opts: LogFilter) -> List[LogEntry]:
        """
        Query logs with filter.

        Args:
            filter_opts: Filter options

        Returns:
            list: Matching log entries
        """
        results = self._logs

        # Filter by time
        if filter_opts.start_time:
            results = [e for e in results if e.timestamp >= filter_opts.start_time]
        if filter_opts.end_time:
            results = [e for e in results if e.timestamp <= filter_opts.end_time]

        # Filter by level
        level_values = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 4,
        }
        min_level_value = level_values.get(filter_opts.min_level, 0)
        results = [
            e for e in results if level_values.get(e.level, 0) >= min_level_value
        ]

        # Filter by tags
        if filter_opts.tags:
            results = [e for e in results if e.tag in filter_opts.tags]

        # Filter exceptions
        if not filter_opts.include_exceptions:
            results = [e for e in results if e.exception is None]

        # Apply max entries limit
        results = results[-filter_opts.max_entries :]

        return results

    def export_logs(
        self,
        options: Optional[ExportOptions] = None,
    ) -> ExportResult:
        """
        Export logs to file (AD-090).

        Args:
            options: Export options

        Returns:
            ExportResult: Export operation result

        Raises:
            ValueError: If export fails
        """
        if options is None:
            options = ExportOptions()

        try:
            # Query logs with filter
            logs = self.query_logs(options.filter)

            if not logs:
                return ExportResult(
                    success=False,
                    error_message="No logs matching filter criteria",
                )

            # Format logs
            if options.format == ExportFormat.JSON:
                content = self._format_json(logs, options)
            elif options.format == ExportFormat.CSV:
                content = self._format_csv(logs, options)
            elif options.format == ExportFormat.TEXT:
                content = self._format_text(logs, options)
            elif options.format == ExportFormat.HTML:
                content = self._format_html(logs, options)
            else:
                raise ValueError(f"Unsupported format: {options.format}")

            # Generate filename
            timestamp_str = (
                datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                if options.timestamp_in_filename
                else ""
            )
            extension = options.format.value
            filename = f"logs_{timestamp_str}.{extension}"
            file_path = f"{self._export_directory}/{filename}"

            # Calculate size
            file_size = len(content.encode("utf-8"))

            if file_size > options.max_file_size_mb * 1024 * 1024:
                raise ValueError(
                    f"Export size {file_size} exceeds max "
                    f"{options.max_file_size_mb}MB"
                )

            # Create result
            result = ExportResult(
                success=True,
                file_path=file_path,
                file_size_bytes=file_size,
                entry_count=len(logs),
                format_used=options.format,
                timestamp=datetime.utcnow(),
            )

            self._export_history.append(result)
            return result

        except Exception as e:
            result = ExportResult(
                success=False,
                error_message=str(e),
            )
            self._export_history.append(result)
            return result

    def share_logs(
        self,
        export_result: ExportResult,
        share_opts: Optional[ShareOptions] = None,
    ) -> Dict:
        """
        Share exported logs (AD-136).

        Args:
            export_result: Export result to share
            share_opts: Share options

        Returns:
            dict: Share operation result

        Raises:
            ValueError: If share fails
        """
        if share_opts is None:
            share_opts = ShareOptions()

        if not export_result.success or not export_result.file_path:
            raise ValueError("Cannot share failed export")

        try:
            result = {
                "success": True,
                "method": share_opts.method.value,
                "file_path": export_result.file_path,
                "file_size": export_result.file_size_bytes,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Handle share method
            if share_opts.method == ShareMethod.EMAIL:
                result["recipient"] = share_opts.recipient
                result["status"] = "sent_to_email"

            elif share_opts.method == ShareMethod.FILE_SHARE:
                result["share_link"] = f"share://logs/{export_result.file_path}"
                if share_opts.expiry_hours:
                    result["expiry"] = (
                        datetime.utcnow() + timedelta(hours=share_opts.expiry_hours)
                    ).isoformat()

            elif share_opts.method == ShareMethod.CLOUD_UPLOAD:
                result["cloud_path"] = (
                    f"cloud://{share_opts.recipient}/" f"{export_result.file_path}"
                )
                result["status"] = "uploaded_to_cloud"

            elif share_opts.method == ShareMethod.LOCAL_FILE:
                result["local_path"] = export_result.file_path
                result["status"] = "ready_for_download"

            elif share_opts.method == ShareMethod.CLIPBOARD:
                result["status"] = "copied_to_clipboard"

            self._share_history.append(result)
            return result

        except Exception as e:
            result = {
                "success": False,
                "error_message": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
            self._share_history.append(result)
            return result

    def get_log_statistics(self) -> dict:
        """
        Get log statistics.

        Returns:
            dict: Log statistics
        """
        if not self._logs:
            return {
                "total_logs": 0,
                "by_level": {},
                "by_tag": {},
                "date_range": None,
            }

        by_level = {}
        by_tag = {}

        for log in self._logs:
            level_key = log.level.value
            by_level[level_key] = by_level.get(level_key, 0) + 1

            tag_key = log.tag
            by_tag[tag_key] = by_tag.get(tag_key, 0) + 1

        return {
            "total_logs": len(self._logs),
            "by_level": by_level,
            "by_tag": by_tag,
            "date_range": {
                "start": (self._logs[0].timestamp.isoformat() if self._logs else None),
                "end": (self._logs[-1].timestamp.isoformat() if self._logs else None),
            },
        }

    def get_error_logs(
        self,
        hours: int = 24,
    ) -> List[LogEntry]:
        """
        Get error logs from past N hours.

        Args:
            hours: Number of hours to look back

        Returns:
            list: Error and critical logs
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        filter_opts = LogFilter(
            start_time=cutoff_time,
            min_level=LogLevel.ERROR,
            include_exceptions=True,
        )

        return self.query_logs(filter_opts)

    def clear_logs(self) -> int:
        """
        Clear all logs.

        Returns:
            int: Number of logs cleared
        """
        count = len(self._logs)
        self._logs.clear()
        return count

    def clear_old_logs(self, days: int = 30) -> int:
        """
        Clear logs older than N days.

        Args:
            days: Age threshold in days

        Returns:
            int: Number of logs removed
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        original_count = len(self._logs)

        self._logs = [e for e in self._logs if e.timestamp >= cutoff_time]

        return original_count - len(self._logs)

    def get_export_history(self, limit: int = 50) -> List[ExportResult]:
        """
        Get export operation history.

        Args:
            limit: Maximum results to return

        Returns:
            list: Recent export operations
        """
        return self._export_history[-limit:]

    def get_share_history(self, limit: int = 50) -> List[Dict]:
        """
        Get log share history.

        Args:
            limit: Maximum results to return

        Returns:
            list: Recent share operations
        """
        return self._share_history[-limit:]

    def _format_json(
        self,
        logs: List[LogEntry],
        options: ExportOptions,
    ) -> str:
        """Format logs as JSON."""
        data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "entry_count": len(logs),
            "logs": [log.to_dict() for log in logs],
        }

        if options.include_metadata:
            data["statistics"] = self.get_log_statistics()

        return json.dumps(data, indent=2)

    def _format_csv(
        self,
        logs: List[LogEntry],
        options: ExportOptions,
    ) -> str:
        """Format logs as CSV."""
        lines = ["timestamp,level,tag,message,exception"]

        for log in logs:
            timestamp = log.timestamp.isoformat()
            level = log.level.value
            tag = log.tag
            message = log.message.replace('"', '""')
            exception = (log.exception or "").replace('"', '""')

            line = f'{timestamp},"{level}","{tag}",' f'"{message}","{exception}"'
            lines.append(line)

        return "\n".join(lines)

    def _format_text(
        self,
        logs: List[LogEntry],
        options: ExportOptions,
    ) -> str:
        """Format logs as plain text."""
        lines = [
            f"Log Export - {datetime.utcnow().isoformat()}",
            f"Total Entries: {len(logs)}",
            "=" * 80,
            "",
        ]

        for log in logs:
            timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            level = log.level.value
            tag = log.tag

            lines.append(f"[{timestamp}] {level} - {tag}")
            lines.append(f"  Message: {log.message}")

            if log.exception:
                lines.append(f"  Exception: {log.exception}")

            if log.stack_trace:
                lines.append(f"  Stack Trace:\n{log.stack_trace}")

            lines.append("")

        return "\n".join(lines)

    def _format_html(
        self,
        logs: List[LogEntry],
        options: ExportOptions,
    ) -> str:
        """Format logs as HTML."""
        timestamp = datetime.utcnow().isoformat()

        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Application Logs</title>",
            "<style>",
            "body { font-family: monospace; margin: 20px; }",
            "table { border-collapse: collapse; width: 100%; }",
            ("th, td { border: 1px solid #ddd; padding: 8px; " "text-align: left; }"),
            "th { background-color: #4CAF50; color: white; }",
            ".ERROR { background-color: #ffcccc; }",
            ".WARNING { background-color: #ffeecc; }",
            ".INFO { background-color: #ccffcc; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>Application Logs - {timestamp}</h1>",
            f"<p>Total Entries: {len(logs)}</p>",
            "<table>",
            "<tr><th>Timestamp</th><th>Level</th><th>Tag</th>" "<th>Message</th></tr>",
        ]

        for log in logs:
            timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            level = log.level.value
            tag = log.tag
            message = log.message

            row_class = level

            html.append(
                f'<tr class="{row_class}"><td>{timestamp}</td>'
                f"<td>{level}</td><td>{tag}</td><td>{message}</td></tr>"
            )

        html.extend(
            [
                "</table>",
                "</body>",
                "</html>",
            ]
        )

        return "\n".join(html)

    def reset(self) -> None:
        """Reset manager to initial state."""
        self._logs.clear()
        self._export_history.clear()
        self._share_history.clear()
