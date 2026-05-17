"""
Configuration management for APIMockLite
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict


@dataclass
class EndpointConfig:
    """Configuration for a single API endpoint"""
    path: str
    method: str = "GET"
    status_code: int = 200
    content_type: str = "application/json"
    response: Any = None
    response_file: Optional[str] = None
    delay: float = 0.0
    headers: Dict[str, str] = field(default_factory=dict)
    scenarios: Dict[str, Any] = field(default_factory=dict)
    dynamic: bool = False
    template: Optional[str] = None
    
    def get_response(self, scenario: Optional[str] = None) -> Any:
        """Get response for endpoint, optionally using scenario"""
        if scenario and scenario in self.scenarios:
            return self.scenarios[scenario]
        return self.response


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "127.0.0.1"
    port: int = 8080
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    log_level: str = "INFO"
    record_requests: bool = False
    recording_dir: str = "./recordings"
    ai_generation: bool = False
    ai_endpoint_description: Optional[str] = None


@dataclass
class Config:
    """Main configuration class"""
    server: ServerConfig = field(default_factory=ServerConfig)
    endpoints: List[EndpointConfig] = field(default_factory=list)
    global_headers: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create configuration from dictionary"""
        server_data = data.get("server", {})
        server = ServerConfig(**server_data)
        
        endpoints = []
        for ep_data in data.get("endpoints", []):
            endpoints.append(EndpointConfig(**ep_data))
        
        return cls(
            server=server,
            endpoints=endpoints,
            global_headers=data.get("global_headers", {})
        )
    
    @classmethod
    def from_yaml(cls, filepath: str) -> "Config":
        """Load configuration from YAML file"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def from_json(cls, filepath: str) -> "Config":
        """Load configuration from JSON file"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "server": asdict(self.server),
            "endpoints": [asdict(ep) for ep in self.endpoints],
            "global_headers": self.global_headers
        }
    
    def save_yaml(self, filepath: str):
        """Save configuration to YAML file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, allow_unicode=True)
    
    def save_json(self, filepath: str):
        """Save configuration to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    def get_endpoint(self, path: str, method: str = "GET") -> Optional[EndpointConfig]:
        """Get endpoint configuration by path and method"""
        for endpoint in self.endpoints:
            if endpoint.path == path and endpoint.method.upper() == method.upper():
                return endpoint
        return None
    
    def add_endpoint(self, endpoint: EndpointConfig):
        """Add a new endpoint configuration"""
        self.endpoints.append(endpoint)
    
    def remove_endpoint(self, path: str, method: str = "GET") -> bool:
        """Remove an endpoint configuration"""
        for i, endpoint in enumerate(self.endpoints):
            if endpoint.path == path and endpoint.method.upper() == method.upper():
                self.endpoints.pop(i)
                return True
        return False