import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path for testing imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test partitions:
# - GUI Launch: Verify that the MainWindow is instantiated and mainloop is called.
# - Import Integrity: Ensure main.py can correctly import its dependencies.

def test_main_application_launch_and_mainloop_call():
    """
    Covers GUI Launch partition.
    Tests that main.py correctly initializes the MainWindow and calls its mainloop method.
    Mocks mainloop to prevent the actual Tkinter window from opening during tests.
    """
    with patch('src.ui.main_window.MainWindow') as MockMainWindow:
        # Create a mock instance for the mocked MainWindow
        mock_instance = MagicMock()
        MockMainWindow.return_value = mock_instance

        # Import main.py within the patch context
        # This reloads the module if it was already imported, ensuring the patch applies
        if 'src.main' in sys.modules:
            del sys.modules['src.main']
        import src.main

        # Assert that MainWindow was instantiated
        MockMainWindow.assert_called_once()

        # Assert that mainloop was called on the instance
        mock_instance.mainloop.assert_called_once()

def test_main_imports_correctly():
    """
    Covers Import Integrity partition.
    Tests that main.py can be imported without immediate import errors,
    ensuring its initial dependency resolution is correct.
    This implicitly checks if src.ui.main_window can be found.
    """
    try:
        # Attempt to import main.py
        # If already imported, reload to ensure fresh import check
        if 'src.main' in sys.modules:
            del sys.modules['src.main']
        import src.main
        # If no ImportError occurs, the test passes
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import src.main: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred during import of src.main: {e}")
