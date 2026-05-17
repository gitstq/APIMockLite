"""
Command Line Interface for APIMockLite
"""

import argparse
import sys
import os
from pathlib import Path

from .server import MockServer, create_server_from_config
from .config import Config, EndpointConfig, ServerConfig
from .generator import ResponseGenerator
from .recorder import RequestRecorder
from .tui import run_dashboard


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog="apimocklite",
        description="🚀 APIMockLite - Lightweight AI-Powered API Mock Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  apimocklite start                           # Start with default config
  apimocklite start --config config.yaml      # Start with custom config
  apimocklite start --port 3000 --ai          # Start on port 3000 with AI generation
  apimocklite init                            # Create sample configuration
  apimocklite generate --endpoint /users      # Generate mock response
  apimocklite record --export mocks.json      # Export recorded requests
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Start command
    start_parser = subparsers.add_parser(
        "start",
        help="Start the mock server",
        description="Start the APIMockLite server"
    )
    start_parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to configuration file (YAML or JSON)"
    )
    start_parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    start_parser.add_argument(
        "--port", "-p",
        type=int,
        default=8080,
        help="Port to listen on (default: 8080)"
    )
    start_parser.add_argument(
        "--ai",
        action="store_true",
        help="Enable AI-powered response generation"
    )
    start_parser.add_argument(
        "--record",
        action="store_true",
        help="Enable request recording"
    )
    start_parser.add_argument(
        "--no-cors",
        action="store_true",
        help="Disable CORS"
    )
    start_parser.add_argument(
        "--dashboard", "-d",
        action="store_true",
        help="Enable TUI dashboard"
    )
    
    # Init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize sample configuration",
        description="Create a sample configuration file"
    )
    init_parser.add_argument(
        "--output", "-o",
        type=str,
        default="apimocklite.yaml",
        help="Output file path (default: apimocklite.yaml)"
    )
    init_parser.add_argument(
        "--format",
        type=str,
        choices=["yaml", "json"],
        default="yaml",
        help="Configuration format (default: yaml)"
    )
    
    # Generate command
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate mock data",
        description="Generate AI-powered mock responses"
    )
    gen_parser.add_argument(
        "--endpoint", "-e",
        type=str,
        required=True,
        help="API endpoint path"
    )
    gen_parser.add_argument(
        "--method", "-m",
        type=str,
        default="GET",
        choices=["GET", "POST", "PUT", "PATCH", "DELETE"],
        help="HTTP method (default: GET)"
    )
    gen_parser.add_argument(
        "--count", "-n",
        type=int,
        default=1,
        help="Number of items to generate (default: 1)"
    )
    gen_parser.add_argument(
        "--type", "-t",
        type=str,
        choices=["user", "product", "order", "company", "generic"],
        help="Data type to generate"
    )
    gen_parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path"
    )
    
    # Record command
    record_parser = subparsers.add_parser(
        "record",
        help="Manage recorded requests",
        description="View and export recorded API requests"
    )
    record_parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List recorded requests"
    )
    record_parser.add_argument(
        "--export", "-e",
        type=str,
        help="Export recorded requests to file"
    )
    record_parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all recorded requests"
    )
    record_parser.add_argument(
        "--stats", "-s",
        action="store_true",
        help="Show recording statistics"
    )
    record_parser.add_argument(
        "--dir",
        type=str,
        default="./recordings",
        help="Recordings directory (default: ./recordings)"
    )
    
    # Version command
    subparsers.add_parser(
        "version",
        help="Show version information"
    )
    
    return parser


def cmd_start(args):
    """Handle start command"""
    try:
        if args.config:
            # Load from configuration file
            server = create_server_from_config(args.config)
            
            # Override with command line arguments
            if args.host:
                server.config.server.host = args.host
            if args.port:
                server.config.server.port = args.port
            if args.ai:
                server.config.server.ai_generation = True
            if args.record:
                if not server.recorder:
                    server.recorder = RequestRecorder(server.config.server.recording_dir)
                server.recorder.enabled = True
            if args.no_cors:
                server.config.server.cors_enabled = False
        else:
            # Create default configuration
            config = ServerConfig(
                host=args.host,
                port=args.port,
                cors_enabled=not args.no_cors,
                ai_generation=args.ai,
                record_requests=args.record
            )
            
            server_config = Config(server=config)
            generator = ResponseGenerator()
            
            recorder = None
            if args.record:
                recorder = RequestRecorder()
            
            server = MockServer(server_config, generator, recorder)
        
        # Start server (with or without dashboard)
        if args.dashboard:
            # Start server in background thread
            import threading
            server_thread = threading.Thread(target=server.start, kwargs={'blocking': False}, daemon=True)
            server_thread.start()
            
            # Run dashboard
            run_dashboard(server, server.recorder)
        else:
            server.start(blocking=True)
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


def cmd_init(args):
    """Handle init command"""
    sample_config = {
        "server": {
            "host": "127.0.0.1",
            "port": 8080,
            "cors_enabled": True,
            "cors_origins": ["*"],
            "log_level": "INFO",
            "record_requests": False,
            "recording_dir": "./recordings",
            "ai_generation": True
        },
        "endpoints": [
            {
                "path": "/api/users",
                "method": "GET",
                "status_code": 200,
                "content_type": "application/json",
                "response": {
                    "users": [
                        {"id": 1, "name": "John Doe", "email": "john@example.com"},
                        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
                    ]
                },
                "scenarios": {
                    "empty": {"users": []},
                    "error": {"error": "Failed to fetch users"}
                }
            },
            {
                "path": "/api/users",
                "method": "POST",
                "status_code": 201,
                "content_type": "application/json",
                "response": {
                    "id": 3,
                    "name": "New User",
                    "email": "newuser@example.com",
                    "created": True
                }
            },
            {
                "path": "/api/users/:id",
                "method": "GET",
                "status_code": 200,
                "content_type": "application/json",
                "response": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "admin"
                },
                "scenarios": {
                    "not_found": {
                        "error": "User not found",
                        "code": 404
                    }
                }
            },
            {
                "path": "/api/health",
                "method": "GET",
                "status_code": 200,
                "content_type": "application/json",
                "response": {
                    "status": "healthy",
                    "timestamp": "2025-01-01T00:00:00Z",
                    "version": "1.0.0"
                }
            }
        ],
        "global_headers": {
            "X-API-Version": "1.0.0",
            "X-Mock-Server": "APIMockLite"
        }
    }
    
    output_path = Path(args.output)
    
    try:
        if args.format == "yaml":
            try:
                import yaml
                with open(output_path, 'w', encoding='utf-8') as f:
                    yaml.dump(sample_config, f, default_flow_style=False, allow_unicode=True)
            except ImportError:
                print("⚠️ PyYAML not installed, falling back to JSON format")
                output_path = output_path.with_suffix('.json')
                with open(output_path, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(sample_config, f, indent=2, ensure_ascii=False)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(sample_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created sample configuration: {output_path.absolute()}")
        print(f"\nNext steps:")
        print(f"  1. Edit {output_path.name} to customize your mock endpoints")
        print(f"  2. Run: apimocklite start --config {output_path.name}")
    
    except Exception as e:
        print(f"❌ Error creating configuration: {e}")
        sys.exit(1)


def cmd_generate(args):
    """Handle generate command"""
    generator = ResponseGenerator()
    
    # Determine data type from endpoint
    data_type = args.type
    if not data_type:
        endpoint_lower = args.endpoint.lower()
        if "user" in endpoint_lower:
            data_type = "user"
        elif "product" in endpoint_lower:
            data_type = "product"
        elif "order" in endpoint_lower:
            data_type = "order"
        else:
            data_type = "generic"
    
    # Generate response
    if args.count > 1 and args.method == "GET":
        # Generate list
        if data_type == "user":
            items = generator.generate_list(generator.generate_user, args.count)
        elif data_type == "product":
            items = generator.generate_list(generator.generate_product, args.count)
        elif data_type == "order":
            items = generator.generate_list(generator.generate_order, args.count)
        else:
            items = [{"id": i, "name": f"Item {i}"} for i in range(args.count)]
        
        result = generator.generate_paginated_response(items, page=1, per_page=args.count, total=args.count)
    else:
        # Generate single item
        result = generator.generate_api_response(args.endpoint, args.method, data_type)
    
    # Output result
    import json
    output = json.dumps(result, indent=2, ensure_ascii=False)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"✅ Generated mock data saved to: {args.output}")
    else:
        print(output)


def cmd_record(args):
    """Handle record command"""
    recorder = RequestRecorder(args.dir)
    
    if args.list:
        # List recent records
        records = recorder.get_records(limit=20)
        if not records:
            print("No recorded requests found.")
            return
        
        print(f"\n{'Time':<12} {'Method':<8} {'Path':<30} {'Status':<8}")
        print("-" * 60)
        
        for record in reversed(records):
            time_str = __import__('datetime').datetime.fromtimestamp(record.timestamp).strftime('%H:%M:%S')
            print(f"{time_str:<12} {record.method:<8} {record.path[:30]:<30} {record.response_status:<8}")
    
    elif args.export:
        # Export to file
        recorder.load_records()
        recorder.export_to_json(args.export)
        print(f"✅ Exported recorded requests to: {args.export}")
    
    elif args.clear:
        # Clear records
        import shutil
        if Path(args.dir).exists():
            shutil.rmtree(args.dir)
            print(f"✅ Cleared all recorded requests from: {args.dir}")
        else:
            print("No recordings to clear.")
    
    elif args.stats:
        # Show statistics
        recorder.load_records()
        stats = recorder.get_statistics()
        
        print("\n📊 Recording Statistics")
        print("-" * 30)
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Unique Endpoints: {stats['unique_endpoints']}")
        print(f"Average Response Time: {stats['average_response_time_ms']}ms")
        
        if stats['methods']:
            print(f"\nMethods:")
            for method, count in stats['methods'].items():
                print(f"  {method}: {count}")
        
        if stats['status_codes']:
            print(f"\nStatus Codes:")
            for status, count in sorted(stats['status_codes'].items()):
                print(f"  {status}: {count}")
    
    else:
        print("Use --list, --export, --clear, or --stats to manage recordings")


def cmd_version():
    """Handle version command"""
    from . import __version__, __author__
    print(f"🚀 APIMockLite v{__version__}")
    print(f"Author: {__author__}")
    print("License: MIT")
    print("\nA lightweight, AI-powered API mock server with zero dependencies")


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "start":
        cmd_start(args)
    elif args.command == "init":
        cmd_init(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "record":
        cmd_record(args)
    elif args.command == "version":
        cmd_version()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()