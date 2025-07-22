import pytest
from pathlib import Path
import sys

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src import set_root_dir
from src.languages.coder_language.interpreter import execute_directive


class StubAgent:
    """Minimal agent for testing interpreter interactions."""

    def __init__(self):
        self.prompts = []
        self.prompt_queue = []
        self.deactivated = False

    async def api_call(self):
        while self.prompt_queue:
            self.prompts.append(self.prompt_queue.pop(0))


@pytest.fixture()
def workspace(tmp_path):
    """Set up isolated workspace and project root marker."""
    set_root_dir(str(tmp_path))
    (tmp_path / "requirements.txt").write_text("# marker")
    return tmp_path


@pytest.fixture(autouse=True)
def patch_async(monkeypatch):
    """Run asyncio.create_task synchronously for deterministic tests."""
    def sync_create_task(coro):
        import asyncio, concurrent.futures
        try:
            loop = asyncio.get_running_loop()
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()
                    asyncio.set_event_loop(None)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                return executor.submit(run_in_thread).result()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
                asyncio.set_event_loop(None)
    monkeypatch.setattr("asyncio.create_task", sync_create_task)


class TestTripleQuotedDirectives:
    def test_change_triple_quoted(self, workspace):
        agent = StubAgent()
        target_file = workspace / "hello.py"
        content = """def hello():\n    return 'world'\n"""
        directive = f'CHANGE CONTENT="""{content}"""'
        execute_directive(directive, base_path=str(workspace), agent=agent, own_file="hello.py")
        assert target_file.exists()
        assert target_file.read_text() == content
        assert any("CHANGE succeeded" in p for p in agent.prompts)

    def test_replace_triple_quoted(self, workspace):
        agent = StubAgent()
        target_file = workspace / "data.txt"
        original = "old\nvalue\n"
        target_file.write_text(original)
        directive = 'REPLACE FROM="""old""" TO="""new"""'
        execute_directive(directive, base_path=str(workspace), agent=agent, own_file="data.txt")
        assert target_file.read_text() == "new\nvalue\n"
        assert any("REPLACE succeeded" in p for p in agent.prompts) 