"""
Request Recorder for APIMockLite

Records incoming requests and responses for later replay and analysis.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse


class RecordedRequest:
    """Represents a recorded request/response pair"""
    
    def __init__(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        query_params: Dict[str, List[str]],
        body: Optional[Any],
        response_status: int,
        response_headers: Dict[str, str],
        response_body: Any,
        timestamp: Optional[float] = None,
        duration_ms: Optional[float] = None
    ):
        self.method = method
        self.path = path
        self.headers = headers
        self.query_params = query_params
        self.body = body
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_body = response_body
        self.timestamp = timestamp or time.time()
        self.duration_ms = duration_ms or 0.0
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique record ID"""
        timestamp_str = datetime.fromtimestamp(self.timestamp).strftime("%Y%m%d%H%M%S")
        return f"req_{timestamp_str}_{int(self.timestamp * 1000) % 1000}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "method": self.method,
            "path": self.path,
            "query_params": self.query_params,
            "headers": self.headers,
            "body": self.body,
            "response": {
                "status": self.response_status,
                "headers": self.response_headers,
                "body": self.response_body
            },
            "duration_ms": self.duration_ms
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecordedRequest":
        """Create from dictionary"""
        return cls(
            method=data["method"],
            path=data["path"],
            headers=data.get("headers", {}),
            query_params=data.get("query_params", {}),
            body=data.get("body"),
            response_status=data["response"]["status"],
            response_headers=data["response"].get("headers", {}),
            response_body=data["response"].get("body"),
            timestamp=data.get("timestamp"),
            duration_ms=data.get("duration_ms")
        )


class RequestRecorder:
    """Records and manages API requests and responses"""
    
    def __init__(self, recording_dir: str = "./recordings"):
        self.recording_dir = Path(recording_dir)
        self.recording_dir.mkdir(parents=True, exist_ok=True)
        self.records: List[RecordedRequest] = []
        self.enabled = True
        self.max_records = 1000  # Maximum records to keep in memory
    
    def record(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[Any],
        response_status: int,
        response_headers: Dict[str, str],
        response_body: Any,
        duration_ms: Optional[float] = None
    ) -> RecordedRequest:
        """Record a request/response pair"""
        if not self.enabled:
            return None
        
        # Parse query parameters
        parsed_url = urlparse(path)
        query_params = parse_qs(parsed_url.query)
        clean_path = parsed_url.path
        
        record = RecordedRequest(
            method=method,
            path=clean_path,
            headers=dict(headers),
            query_params=query_params,
            body=body,
            response_status=response_status,
            response_headers=dict(response_headers),
            response_body=response_body,
            duration_ms=duration_ms
        )
        
        self.records.append(record)
        
        # Trim records if exceeding max
        if len(self.records) > self.max_records:
            self.records = self.records[-self.max_records:]
        
        # Auto-save to file
        self._save_record(record)
        
        return record
    
    def _save_record(self, record: RecordedRequest):
        """Save a single record to file"""
        date_str = datetime.fromtimestamp(record.timestamp).strftime("%Y-%m-%d")
        daily_file = self.recording_dir / f"recordings_{date_str}.jsonl"
        
        with open(daily_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + '\n')
    
    def get_records(
        self,
        method: Optional[str] = None,
        path: Optional[str] = None,
        status_code: Optional[int] = None,
        limit: int = 100
    ) -> List[RecordedRequest]:
        """Get filtered records"""
        filtered = self.records
        
        if method:
            filtered = [r for r in filtered if r.method.upper() == method.upper()]
        
        if path:
            filtered = [r for r in filtered if path in r.path]
        
        if status_code:
            filtered = [r for r in filtered if r.response_status == status_code]
        
        return filtered[-limit:]
    
    def get_record_by_id(self, record_id: str) -> Optional[RecordedRequest]:
        """Get a specific record by ID"""
        for record in self.records:
            if record.id == record_id:
                return record
        return None
    
    def clear_records(self):
        """Clear all in-memory records"""
        self.records = []
    
    def load_records(self, date_str: Optional[str] = None):
        """Load records from file"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        daily_file = self.recording_dir / f"recordings_{date_str}.jsonl"
        
        if not daily_file.exists():
            return
        
        with open(daily_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        record = RecordedRequest.from_dict(data)
                        self.records.append(record)
                    except (json.JSONDecodeError, KeyError):
                        continue
    
    def generate_mock_config(self, endpoint_pattern: Optional[str] = None) -> Dict[str, Any]:
        """Generate mock configuration from recorded requests"""
        config = {
            "server": {
                "host": "127.0.0.1",
                "port": 8080,
                "cors_enabled": True
            },
            "endpoints": []
        }
        
        # Group records by path and method
        endpoint_map = {}
        for record in self.records:
            key = (record.path, record.method)
            if key not in endpoint_map:
                endpoint_map[key] = []
            endpoint_map[key].append(record)
        
        # Generate endpoint configurations
        for (path, method), records in endpoint_map.items():
            if endpoint_pattern and endpoint_pattern not in path:
                continue
            
            # Use the most recent successful response as default
            successful = [r for r in records if 200 <= r.response_status < 300]
            if successful:
                default_record = successful[-1]
            else:
                default_record = records[-1]
            
            # Collect different response scenarios
            scenarios = {}
            for record in records:
                scenario_name = f"status_{record.response_status}"
                if scenario_name not in scenarios:
                    scenarios[scenario_name] = record.response_body
            
            endpoint_config = {
                "path": path,
                "method": method,
                "status_code": default_record.response_status,
                "content_type": default_record.response_headers.get("Content-Type", "application/json"),
                "response": default_record.response_body,
                "scenarios": scenarios
            }
            
            config["endpoints"].append(endpoint_config)
        
        return config
    
    def export_to_json(self, filepath: str, endpoint_pattern: Optional[str] = None):
        """Export recorded data to JSON file"""
        config = self.generate_mock_config(endpoint_pattern)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get recording statistics"""
        if not self.records:
            return {
                "total_requests": 0,
                "unique_endpoints": 0,
                "methods": {},
                "status_codes": {},
                "average_response_time_ms": 0
            }
        
        methods = {}
        status_codes = {}
        endpoints = set()
        total_duration = 0
        
        for record in self.records:
            methods[record.method] = methods.get(record.method, 0) + 1
            status_codes[record.response_status] = status_codes.get(record.response_status, 0) + 1
            endpoints.add((record.path, record.method))
            total_duration += record.duration_ms
        
        return {
            "total_requests": len(self.records),
            "unique_endpoints": len(endpoints),
            "methods": methods,
            "status_codes": status_codes,
            "average_response_time_ms": round(total_duration / len(self.records), 2)
        }