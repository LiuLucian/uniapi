#!/usr/bin/env python3
"""
Instagram API Comprehensive Test Suite Runner
Provides unified interface to test all Instagram API features
"""
import subprocess
import sys
import os

# ANSI color codes for better output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.END}\n")

def print_section(text):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'-' * len(text)}{Colors.END}")

def run_test_script(script_name, description):
    """Run a test script"""
    print_section(f"📋 {description}")
    print(f"Running: {Colors.BOLD}{script_name}{Colors.END}\n")

    try:
        subprocess.run([sys.executable, script_name], check=False)
        return True
    except FileNotFoundError:
        print(f"{Colors.RED}❌ Test script not found: {script_name}{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Error running test: {e}{Colors.END}")
        return False

def check_servers():
    """Check if required servers are running"""
    print_section("🔍 Checking Server Status")

    import requests

    # Check FastAPI server
    try:
        response = requests.get("http://localhost:8000/api/v1/instagram/health", timeout=5)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ FastAPI Server (port 8000): Running{Colors.END}")
            fastapi_ok = True
        else:
            print(f"{Colors.YELLOW}⚠️  FastAPI Server (port 8000): Responding but unhealthy{Colors.END}")
            fastapi_ok = False
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}❌ FastAPI Server (port 8000): Not running{Colors.END}")
        fastapi_ok = False
    except Exception as e:
        print(f"{Colors.RED}❌ FastAPI Server check failed: {e}{Colors.END}")
        fastapi_ok = False

    # Check Instagram Bridge Server
    try:
        response = requests.get("http://localhost:5002/health", timeout=5)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ Instagram Bridge Server (port 5002): Running{Colors.END}")
            bridge_ok = True
        else:
            print(f"{Colors.YELLOW}⚠️  Instagram Bridge Server (port 5002): Responding but unhealthy{Colors.END}")
            bridge_ok = False
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}❌ Instagram Bridge Server (port 5002): Not running{Colors.END}")
        bridge_ok = False
    except Exception as e:
        print(f"{Colors.RED}❌ Bridge Server check failed: {e}{Colors.END}")
        bridge_ok = False

    if not fastapi_ok or not bridge_ok:
        print(f"\n{Colors.RED}⚠️  Some servers are not running. Tests may fail.{Colors.END}")
        print(f"\n{Colors.YELLOW}To start servers:{Colors.END}")
        if not fastapi_ok:
            print(f"  FastAPI: cd /Users/l.u.c/my-app/uniapi/backend && uvicorn main:app --reload")
        if not bridge_ok:
            print(f"  Bridge: cd /Users/l.u.c/my-app/uniapi/backend && python3 platforms/instagram/instagram_bridge_server.py")

        choice = input(f"\n{Colors.BOLD}Continue anyway? (y/n): {Colors.END}").strip().lower()
        if choice != 'y':
            return False

    return True

def show_menu():
    """Display main test menu"""
    print_header("Instagram API Comprehensive Test Suite")

    print(f"{Colors.BOLD}📊 Available Test Suites:{Colors.END}\n")
    print(f"  {Colors.GREEN}1{Colors.END}. Like/Unlike Tests       - {Colors.CYAN}test_instagram_like.py{Colors.END}")
    print(f"  {Colors.GREEN}2{Colors.END}. Follow/Unfollow Tests  - {Colors.CYAN}test_instagram_follow.py{Colors.END}")
    print(f"  {Colors.GREEN}3{Colors.END}. Comment Tests          - {Colors.CYAN}test_instagram_comment.py{Colors.END}")
    print(f"  {Colors.GREEN}4{Colors.END}. Data Retrieval Tests   - {Colors.CYAN}test_instagram_data.py{Colors.END}")
    print(f"  {Colors.GREEN}5{Colors.END}. Direct Message Tests   - {Colors.CYAN}test_dm_real.py{Colors.END}")
    print()
    print(f"  {Colors.YELLOW}9{Colors.END}. Check Server Status")
    print(f"  {Colors.YELLOW}0{Colors.END}. Exit")
    print()

def main():
    """Main test suite runner"""

    # Check if we're in the correct directory
    if not os.path.exists('test_instagram_like.py'):
        print(f"{Colors.RED}❌ Error: Test scripts not found in current directory{Colors.END}")
        print(f"Please run this script from: {Colors.BOLD}/Users/l.u.c/my-app/uniapi/backend/{Colors.END}")
        sys.exit(1)

    # Initial server check
    print_header("Instagram API Test Suite - Server Check")
    servers_ok = check_servers()

    if not servers_ok:
        print(f"\n{Colors.RED}Exiting due to server issues.{Colors.END}")
        sys.exit(1)

    # Main menu loop
    while True:
        show_menu()

        choice = input(f"{Colors.BOLD}👉 Select test suite (0-9): {Colors.END}").strip()

        if choice == '0':
            print(f"\n{Colors.GREEN}👋 Exiting test suite. Goodbye!{Colors.END}\n")
            break

        elif choice == '1':
            run_test_script('test_instagram_like.py', 'Like/Unlike Functionality Tests')

        elif choice == '2':
            run_test_script('test_instagram_follow.py', 'Follow/Unfollow Functionality Tests')

        elif choice == '3':
            run_test_script('test_instagram_comment.py', 'Comment Functionality Tests')

        elif choice == '4':
            run_test_script('test_instagram_data.py', 'Data Retrieval Tests')

        elif choice == '5':
            run_test_script('test_dm_real.py', 'Direct Message Tests')

        elif choice == '9':
            check_servers()

        else:
            print(f"{Colors.RED}❌ Invalid choice. Please select 0-9{Colors.END}")

        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.END}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test suite interrupted by user{Colors.END}")
        sys.exit(0)
