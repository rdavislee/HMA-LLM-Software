#!/usr/bin/env python3
"""
Simple launcher for the interactive calculator.
"""

import sys
import os

# Add the current directory to the Python path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interactive_calculator import InteractiveCalculator

if __name__ == '__main__':
    calculator = InteractiveCalculator()
    calculator.run() 