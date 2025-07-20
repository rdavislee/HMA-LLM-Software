import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src import set_root_dir
from src.languages.tester_language.interpreter import execute_directive


class StubTesterAgent:
    def __init__(self, personal_file: Path):
        self.personal_file = personal_file
        self.prompt_queue = []
        self.prompts = []
        self.parent = None
        self.active_task = None
        self.stall = False

    async def api_call(self):
        while self.prompt_queue:
            self.prompts.append(self.prompt_queue.pop(0))


@pytest.fixture()
def workspace(tmp_path):
    set_root_dir(str(tmp_path))
    (tmp_path / "requirements.txt").write_text("# marker")
    return tmp_path


@pytest.fixture(autouse=True)
def patch_async(monkeypatch):
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
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
                asyncio.set_event_loop(None)
    monkeypatch.setattr("asyncio.create_task", sync_create_task)


class TestTesterTripleQuotes:
    def test_change_triple_quoted(self, workspace):
        scratch = workspace / "scratch_pads" / "tester_scratch.py"
        agent = StubTesterAgent(scratch)
        content = """print('hello')\nprint('world')\n"""
        directive = f'CHANGE CONTENT="""{content}"""'
        execute_directive(directive, agent=agent)
        assert scratch.exists()
        assert scratch.read_text() == content
        assert any("CHANGE succeeded" in p for p in agent.prompts)

    def test_replace_triple_quoted(self, workspace):
        scratch = workspace / "scratch_pads" / "scratch.txt"
        scratch.parent.mkdir(parents=True, exist_ok=True)
        scratch.write_text("foo bar baz")
        agent = StubTesterAgent(scratch)
        directive = 'REPLACE FROM="""bar""" TO="""qux"""'
        execute_directive(directive, agent=agent)
        assert scratch.read_text() == "foo qux baz"
        assert any("REPLACE succeeded" in p for p in agent.prompts) 