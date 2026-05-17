"""
Terminal User Interface for APIMockLite

Provides a beautiful terminal dashboard for monitoring and managing the mock server.
"""

import os
import sys
import time
import threading
from typing import Optional, List, Dict, Any
from datetime import datetime


class Colors:
    """ANSI color codes"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class TUI:
    """Terminal User Interface for APIMockLite"""
    
    def __init__(self, server=None, recorder=None):
        self.server = server
        self.recorder = recorder
        self.running = False
        self.refresh_rate = 1.0  # seconds
        self._screen_lock = threading.Lock()
        self._stop_event = threading.Event()
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def move_cursor(self, row: int, col: int = 0):
        """Move cursor to specific position"""
        print(f"\033[{row};{col}H", end='')
    
    def hide_cursor(self):
        """Hide the cursor"""
        print("\033[?25l", end='')
    
    def show_cursor(self):
        """Show the cursor"""
        print("\033[?25h", end='')
    
    def draw_box(self, x: int, y: int, width: int, height: int, title: str = ""):
        """Draw a box with optional title"""
        # Top border
        self.move_cursor(y, x)
        print(f"{Colors.BRIGHT_BLACK}┌{'─' * (width - 2)}┐{Colors.RESET}")
        
        # Title
        if title:
            title_str = f" {title} "
            title_pos = (width - len(title_str)) // 2
            self.move_cursor(y, x + title_pos)
            print(f"{Colors.BRIGHT_CYAN}{title_str}{Colors.RESET}")
        
        # Side borders
        for i in range(1, height - 1):
            self.move_cursor(y + i, x)
            print(f"{Colors.BRIGHT_BLACK}│{' ' * (width - 2)}│{Colors.RESET}")
        
        # Bottom border
        self.move_cursor(y + height - 1, x)
        print(f"{Colors.BRIGHT_BLACK}└{'─' * (width - 2)}┘{Colors.RESET}")
    
    def draw_header(self, width: int):
        """Draw the header section"""
        header = "🚀 APIMockLite Dashboard"
        subtitle = "AI-Powered API Mock Server"
        
        # Center the header
        header_x = (width - len(header)) // 2
        self.move_cursor(1, header_x)
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{header}{Colors.RESET}")
        
        subtitle_x = (width - len(subtitle)) // 2
        self.move_cursor(2, subtitle_x)
        print(f"{Colors.DIM}{subtitle}{Colors.RESET}")
        
        # Separator line
        self.move_cursor(3, 0)
        print(f"{Colors.BRIGHT_BLACK}{'─' * width}{Colors.RESET}")
    
    def draw_server_status(self, x: int, y: int, width: int):
        """Draw server status panel"""
        self.draw_box(x, y, width, 8, "Server Status")
        
        if self.server and self.server.running:
            status = f"{Colors.BRIGHT_GREEN}● RUNNING{Colors.RESET}"
            host = self.server.config.server.host
            port = self.server.config.server.port
            url = f"http://{host}:{port}"
        else:
            status = f"{Colors.BRIGHT_RED}● STOPPED{Colors.RESET}"
            url = "N/A"
        
        self.move_cursor(y + 2, x + 2)
        print(f"Status: {status}")
        
        self.move_cursor(y + 3, x + 2)
        print(f"URL: {Colors.BRIGHT_YELLOW}{url}{Colors.RESET}")
        
        self.move_cursor(y + 4, x + 2)
        print(f"Time: {Colors.BRIGHT_WHITE}{datetime.now().strftime('%H:%M:%S')}{Colors.RESET}")
        
        self.move_cursor(y + 5, x + 2)
        cors_status = "Enabled" if (self.server and self.server.config.server.cors_enabled) else "Disabled"
        print(f"CORS: {Colors.BRIGHT_GREEN if cors_status == 'Enabled' else Colors.BRIGHT_RED}{cors_status}{Colors.RESET}")
        
        self.move_cursor(y + 6, x + 2)
        ai_status = "Enabled" if (self.server and self.server.config.server.ai_generation) else "Disabled"
        print(f"AI Gen: {Colors.BRIGHT_GREEN if ai_status == 'Enabled' else Colors.BRIGHT_RED}{ai_status}{Colors.RESET}")
    
    def draw_endpoints(self, x: int, y: int, width: int):
        """Draw endpoints panel"""
        if not self.server:
            return
        
        endpoints = self.server.config.endpoints
        height = min(len(endpoints) + 4, 15)
        
        self.draw_box(x, y, width, height, f"Endpoints ({len(endpoints)})")
        
        for i, endpoint in enumerate(endpoints[:10]):  # Show max 10 endpoints
            method_color = {
                "GET": Colors.BRIGHT_GREEN,
                "POST": Colors.BRIGHT_BLUE,
                "PUT": Colors.BRIGHT_YELLOW,
                "PATCH": Colors.BRIGHT_MAGENTA,
                "DELETE": Colors.BRIGHT_RED
            }.get(endpoint.method.upper(), Colors.BRIGHT_WHITE)
            
            self.move_cursor(y + 2 + i, x + 2)
            print(f"{method_color}{endpoint.method.upper():<6}{Colors.RESET} {endpoint.path}")
    
    def draw_statistics(self, x: int, y: int, width: int):
        """Draw statistics panel"""
        self.draw_box(x, y, width, 8, "Statistics")
        
        if self.recorder:
            stats = self.recorder.get_statistics()
            
            self.move_cursor(y + 2, x + 2)
            print(f"Total Requests: {Colors.BRIGHT_CYAN}{stats['total_requests']}{Colors.RESET}")
            
            self.move_cursor(y + 3, x + 2)
            print(f"Unique Endpoints: {Colors.BRIGHT_CYAN}{stats['unique_endpoints']}{Colors.RESET}")
            
            self.move_cursor(y + 4, x + 2)
            methods_str = ", ".join([f"{k}:{v}" for k, v in stats['methods'].items()])
            print(f"Methods: {Colors.BRIGHT_YELLOW}{methods_str or 'None'}{Colors.RESET}")
            
            self.move_cursor(y + 5, x + 2)
            status_str = ", ".join([f"{k}:{v}" for k, v in list(stats['status_codes'].items())[:3]])
            print(f"Status: {Colors.BRIGHT_MAGENTA}{status_str or 'None'}{Colors.RESET}")
            
            self.move_cursor(y + 6, x + 2)
            print(f"Avg Response: {Colors.BRIGHT_GREEN}{stats['average_response_time_ms']}ms{Colors.RESET}")
        else:
            self.move_cursor(y + 2, x + 2)
            print(f"{Colors.DIM}Recording not enabled{Colors.RESET}")
    
    def draw_recent_requests(self, x: int, y: int, width: int):
        """Draw recent requests panel"""
        self.draw_box(x, y, width, 12, "Recent Requests")
        
        if self.recorder:
            recent = self.recorder.get_records(limit=8)
            
            for i, record in enumerate(reversed(recent)):
                method_color = {
                    "GET": Colors.GREEN,
                    "POST": Colors.BLUE,
                    "PUT": Colors.YELLOW,
                    "PATCH": Colors.MAGENTA,
                    "DELETE": Colors.RED
                }.get(record.method.upper(), Colors.WHITE)
                
                status_color = Colors.GREEN if record.response_status < 300 else Colors.YELLOW if record.response_status < 400 else Colors.RED
                
                time_str = datetime.fromtimestamp(record.timestamp).strftime('%H:%M:%S')
                
                self.move_cursor(y + 2 + i, x + 2)
                print(f"{Colors.DIM}{time_str}{Colors.RESET} {method_color}{record.method.upper():<5}{Colors.RESET} {record.path[:25]:<25} {status_color}{record.response_status}{Colors.RESET}")
        else:
            self.move_cursor(y + 2, x + 2)
            print(f"{Colors.DIM}No recorded requests{Colors.RESET}")
    
    def draw_help(self, x: int, y: int, width: int):
        """Draw help panel"""
        self.draw_box(x, y, width, 5, "Commands")
        
        self.move_cursor(y + 2, x + 2)
        print(f"{Colors.BRIGHT_YELLOW}Ctrl+C{Colors.RESET} Stop server  {Colors.BRIGHT_YELLOW}r{Colors.RESET} Refresh  {Colors.BRIGHT_YELLOW}q{Colors.RESET} Quit TUI")
    
    def render(self):
        """Render the full TUI"""
        with self._screen_lock:
            # Get terminal size
            try:
                import shutil
                term_width, term_height = shutil.get_terminal_size()
            except:
                term_width, term_height = 80, 24
            
            self.clear_screen()
            
            # Draw header
            self.draw_header(term_width)
            
            # Calculate panel positions
            panel_width = (term_width - 3) // 2
            left_x = 1
            right_x = left_x + panel_width + 1
            
            # Draw panels
            self.draw_server_status(left_x, 5, panel_width)
            self.draw_statistics(right_x, 5, panel_width)
            
            self.draw_endpoints(left_x, 14, panel_width)
            self.draw_recent_requests(right_x, 14, panel_width)
            
            # Draw help at bottom
            self.draw_help(left_x, term_height - 5, term_width - 2)
            
            # Position cursor at bottom
            self.move_cursor(term_height, 0)
    
    def start(self):
        """Start the TUI"""
        self.running = True
        self.hide_cursor()
        
        def refresh_loop():
            while not self._stop_event.is_set():
                self.render()
                time.sleep(self.refresh_rate)
        
        # Start refresh thread
        refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        refresh_thread.start()
        
        # Handle keyboard input
        try:
            while self.running:
                if os.name == 'nt':
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8', errors='ignore')
                        if key.lower() == 'q':
                            self.running = False
                        elif key.lower() == 'r':
                            self.render()
                else:
                    import select
                    import tty
                    import termios
                    
                    # Set terminal to raw mode
                    old_settings = termios.tcgetattr(sys.stdin)
                    try:
                        tty.setcbreak(sys.stdin.fileno())
                        if select.select([sys.stdin], [], [], self.refresh_rate)[0]:
                            key = sys.stdin.read(1)
                            if key.lower() == 'q':
                                self.running = False
                            elif key.lower() == 'r':
                                self.render()
                    finally:
                        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def stop(self):
        """Stop the TUI"""
        self.running = False
        self._stop_event.set()
        self.show_cursor()
        self.clear_screen()
        print("TUI stopped. Server may still be running.")


def run_dashboard(server=None, recorder=None):
    """Run the TUI dashboard"""
    tui = TUI(server, recorder)
    tui.start()