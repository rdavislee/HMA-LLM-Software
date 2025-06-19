#!/usr/bin/env python3
"""
Test runner script for the HMA-LLM-Software project.

This script provides an easy way to run the test suite with proper configuration
and reporting.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def main():
    """Run the test suite with the specified options."""
    parser = argparse.ArgumentParser(description="Run the HMA-LLM-Software test suite")
    parser.add_argument(
        "--test-path", 
        default="test/agents/base_agent_test.py",
        help="Specific test file or directory to run (default: test/agents/base_agent_test.py)"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--html", 
        action="store_true",
        help="Generate HTML coverage report"
    )
    parser.add_argument(
        "--markers", 
        nargs="+",
        help="Run only tests with specific markers"
    )
    parser.add_argument(
        "--exclude", 
        nargs="+",
        help="Exclude tests with specific markers"
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.coverage:
        cmd.extend(["--cov=src", "--cov-report=term-missing"])
        
        if args.html:
            cmd.append("--cov-report=html")
    
    if args.markers:
        for marker in args.markers:
            cmd.extend(["-m", marker])
    
    if args.exclude:
        for marker in args.exclude:
            cmd.extend(["-m", f"not {marker}"])
    
    cmd.append(args.test_path)
    
    # Run the tests
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("❌ Some tests failed!")
        return e.returncode


if __name__ == "__main__":
    sys.exit(main()) 