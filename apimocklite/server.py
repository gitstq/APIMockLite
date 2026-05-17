"""
HTTP Mock Server for APIMockLite

A lightweight HTTP server that serves mock API responses based on configuration.
"""

import json
import time
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, Optional, Type
from urllib.parse import parse_qs, urlparse

from .config import Config, EndpointConfig
from .generator import ResponseGenerator
from .recorder import RequestRecorder


class MockRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for mock server"""
    
    config: Config = None
    generator: ResponseGenerator = None
    recorder: Optional[RequestRecorder] = None
    
    def log_message(self, format: str, *args):
        """Override to customize logging"""
        if self.config and self.config.server.log_level == "DEBUG":
            print(f"[{self.log_date_time_string()}] {format % args}")
    
    def _send_cors_headers(self):
        """Send CORS headers if enabled"""
        if self.config and self.config.server.cors_enabled:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Scenario, Authorization")
    
    def _read_body(self) -> Optional[Any]:
        """Read and parse request body"""
        content_length = self.headers.get('Content-Length')
        if content_length:
            length = int(content_length)
            body = self.rfile.read(length).decode('utf-8')
            
            # Try to parse as JSON
            content_type = self.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                try:
                    return json.loads(body)
                except json.JSONDecodeError:
                    return body
            return body
        return None
    
    def _get_scenario(self) -> Optional[str]:
        """Get scenario from request header"""
        return self.headers.get('X-Scenario')
    
    def _send_response(
        self,
        status_code: int,
        data: Any,
        content_type: str = "application/json",
        headers: Optional[Dict[str, str]] = None
    ):
        """Send HTTP response"""
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self._send_cors_headers()
        
        if headers:
            for key, value in headers.items():
                self.send_header(key, value)
        
        self.end_headers()
        
        if data is not None:
            if isinstance(data, (dict, list)):
                response_body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            elif isinstance(data, str):
                response_body = data.encode('utf-8')
            else:
                response_body = str(data).encode('utf-8')
            
            self.wfile.write(response_body)
            return response_body.decode('utf-8')
        
        return ""
    
    def _handle_request(self, method: str):
        """Handle HTTP request"""
        start_time = time.time()
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Read request body
        body = self._read_body()
        
        # Get scenario from header
        scenario = self._get_scenario()
        
        # Find matching endpoint
        endpoint = self.config.get_endpoint(path, method)
        
        if endpoint:
            # Use configured response
            response_data = endpoint.get_response(scenario)
            status_code = endpoint.status_code
            content_type = endpoint.content_type
            
            # Apply delay if configured
            if endpoint.delay > 0:
                time.sleep(endpoint.delay)
        else:
            # Generate AI response
            if self.config.server.ai_generation:
                response_data = self.generator.generate_api_response(path, method)
                status_code = 200
                content_type = "application/json"
            else:
                # Return 404
                response_data = {
                    "error": "Not Found",
                    "message": f"No mock configured for {method} {path}",
                    "path": path,
                    "method": method
                }
                status_code = 404
                content_type = "application/json"
        
        # Send response
        response_body = self._send_response(status_code, response_data, content_type)
        
        # Record request if enabled
        if self.recorder and self.recorder.enabled:
            duration_ms = (time.time() - start_time) * 1000
            self.recorder.record(
                method=method,
                path=self.path,
                headers=dict(self.headers),
                body=body,
                response_status=status_code,
                response_headers={"Content-Type": content_type},
                response_body=response_data,
                duration_ms=duration_ms
            )
    
    def do_GET(self):
        """Handle GET requests"""
        self._handle_request("GET")
    
    def do_POST(self):
        """Handle POST requests"""
        self._handle_request("POST")
    
    def do_PUT(self):
        """Handle PUT requests"""
        self._handle_request("PUT")
    
    def do_PATCH(self):
        """Handle PATCH requests"""
        self._handle_request("PATCH")
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        self._handle_request("DELETE")
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests (CORS preflight)"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()


class MockServer:
    """Mock API Server"""
    
    def __init__(
        self,
        config: Config,
        generator: Optional[ResponseGenerator] = None,
        recorder: Optional[RequestRecorder] = None
    ):
        self.config = config
        self.generator = generator or ResponseGenerator()
        self.recorder = recorder
        self.server: Optional[HTTPServer] = None
        self.running = False
    
    def start(self, blocking: bool = True):
        """Start the mock server"""
        # Set up request handler class with configuration
        handler_class = type(
            'ConfiguredHandler',
            (MockRequestHandler,),
            {
                'config': self.config,
                'generator': self.generator,
                'recorder': self.recorder
            }
        )
        
        # Create and start server
        self.server = HTTPServer(
            (self.config.server.host, self.config.server.port),
            handler_class
        )
        
        self.running = True
        print(f"🚀 APIMockLite server started at http://{self.config.server.host}:{self.config.server.port}")
        print(f"📊 Endpoints configured: {len(self.config.endpoints)}")
        print(f"📝 Recording enabled: {self.recorder is not None and self.recorder.enabled}")
        print("Press Ctrl+C to stop\n")
        
        if blocking:
            try:
                self.server.serve_forever()
            except KeyboardInterrupt:
                self.stop()
    
    def stop(self):
        """Stop the mock server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.running = False
            print("\n✅ Server stopped")
    
    def is_running(self) -> bool:
        """Check if server is running"""
        return self.running


def create_server_from_config(config_path: str) -> MockServer:
    """Create a mock server from configuration file"""
    if config_path.endswith('.yaml') or config_path.endswith('.yml'):
        config = Config.from_yaml(config_path)
    elif config_path.endswith('.json'):
        config = Config.from_json(config_path)
    else:
        raise ValueError("Configuration file must be .yaml, .yml, or .json")
    
    generator = ResponseGenerator()
    
    recorder = None
    if config.server.record_requests:
        recorder = RequestRecorder(config.server.recording_dir)
    
    return MockServer(config, generator, recorder)