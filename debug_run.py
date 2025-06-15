#!/usr/bin/env python3

import sys
import os
import tempfile
import shutil
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from manager_language.interpreter import ManagerLanguageInterpreter
from manager_language.parser import ManagerLanguageParser

def test_run_directive():
    print("Testing RUN directive parsing and execution...")
    
    # Set up like the test
    temp_dir = tempfile.mkdtemp()
    interpreter = ManagerLanguageInterpreter(base_path=temp_dir)
    
    try:
        # Test the parser first
        parser = ManagerLanguageParser()
        
        directive_text = 'RUN "echo \\"Complex command with quotes\\""'
        print(f"Testing directive: {directive_text}")
        
        try:
            parsed = parser.parse(directive_text)
            print(f"Parsed successfully: {parsed}")
            print(f"Type: {type(parsed)}")
            if hasattr(parsed, 'command'):
                print(f"Command: {parsed.command}")
        except Exception as e:
            print(f"Parser error: {e}")
            return
        
        # Test the interpreter
        try:
            result = interpreter.execute(directive_text)
            print(f"Execution result: {result}")
            
            if 'error' in result:
                print(f"Error in result: {result['error']}")
            
            if 'commands' in result:
                print(f"Commands: {result['commands']}")
                print(f"Number of commands: {len(result['commands'])}")
            else:
                print("No 'commands' key in result")
                
        except Exception as e:
            print(f"Interpreter error: {e}")
    
    finally:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_run_directive() 