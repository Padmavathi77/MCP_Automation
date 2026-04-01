# pylint: disable=redefined-outer-name, unused-argument
import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock external dependencies that may not be installed in CI
_mock_modules = {
    "autogen_agentchat": MagicMock(),
    "autogen_agentchat.agents": MagicMock(),
    "autogen_agentchat.conditions": MagicMock(),
    "autogen_agentchat.teams": MagicMock(),
    "autogen_agentchat.ui": MagicMock(),
    "autogen_ext": MagicMock(),
    "autogen_ext.models": MagicMock(),
    "autogen_ext.models.openai": MagicMock(),
    "autogen_ext.tools": MagicMock(),
    "autogen_ext.tools.mcp": MagicMock(),
    "dotenv": MagicMock(),
}

for mod_name, mock_mod in _mock_modules.items():
    if mod_name not in sys.modules:
        sys.modules[mod_name] = mock_mod


def _make_console_mock(return_value="result"):
    mock = AsyncMock()
    mock.return_value = return_value
    return mock


class TestLoadApiKey:

    def test_returns_key_when_env_var_is_set(self, monkeypatch):
        # _load_api_key should read OPENAI_API_KEY from env and return it
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-123")
        from FrameworkAIAgents.Scenario import _load_api_key

        result = _load_api_key()
        assert result == "sk-test-key-123"
        assert os.environ["OPENAI_API_KEY"] == "sk-test-key-123"

    def test_sets_os_environ_with_key_value(self, monkeypatch):
        # Verify the key is written back to os.environ for downstream consumers
        monkeypatch.setenv("OPENAI_API_KEY", "sk-another-key")
        from FrameworkAIAgents.Scenario import _load_api_key

        _load_api_key()
        assert os.environ["OPENAI_API_KEY"] == "sk-another-key"

    def test_raises_value_error_when_env_var_missing(self, monkeypatch):
        # Missing OPENAI_API_KEY should raise ValueError, not crash with TypeError
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        from FrameworkAIAgents.Scenario import _load_api_key

        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set"):
            _load_api_key()

    def test_raises_value_error_when_env_var_is_empty_string(self, monkeypatch):
        # Empty string is falsy and should be treated as missing
        monkeypatch.setenv("OPENAI_API_KEY", "")
        from FrameworkAIAgents.Scenario import _load_api_key

        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set"):
            _load_api_key()

    def test_handles_whitespace_only_api_key(self, monkeypatch):
        # Whitespace-only key is technically truthy but still set in os.environ
        monkeypatch.setenv("OPENAI_API_KEY", "   ")
        from FrameworkAIAgents.Scenario import _load_api_key

        result = _load_api_key()
        assert result == "   "
        assert os.environ["OPENAI_API_KEY"] == "   "


class TestMain:

    @pytest.fixture(autouse=True)
    def _set_api_key(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-main-key")

    @patch("FrameworkAIAgents.Scenario.RoundRobinGroupChat")
    @patch("FrameworkAIAgents.Scenario.agentFactory")
    @patch("FrameworkAIAgents.Scenario.OpenAIChatCompletionClient")
    def test_creates_model_client_with_gpt4o(
        self, mock_client_cls, mock_factory_cls, mock_team_cls
    ):
        # main() should instantiate OpenAIChatCompletionClient with model="gpt-4o"
        mock_team_cls.return_value = MagicMock()

        from FrameworkAIAgents.Scenario import main

        with patch("FrameworkAIAgents.Scenario.Console", new=_make_console_mock()):
            asyncio.run(main())
        mock_client_cls.assert_called_once_with(model="gpt-4o")

    @patch("FrameworkAIAgents.Scenario.RoundRobinGroupChat")
    @patch("FrameworkAIAgents.Scenario.agentFactory")
    @patch("FrameworkAIAgents.Scenario.OpenAIChatCompletionClient")
    def test_creates_agent_factory_with_model_client(
        self, mock_client_cls, mock_factory_cls, mock_team_cls
    ):
        # agentFactory should receive the model_client instance
        mock_client_instance = MagicMock()
        mock_client_cls.return_value = mock_client_instance
        mock_team_cls.return_value = MagicMock()

        from FrameworkAIAgents.Scenario import main

        with patch("FrameworkAIAgents.Scenario.Console", new=_make_console_mock()):
            asyncio.run(main())
        mock_factory_cls.assert_called_once_with(mock_client_instance)

    @patch("FrameworkAIAgents.Scenario.RoundRobinGroupChat")
    @patch("FrameworkAIAgents.Scenario.agentFactory")
    @patch("FrameworkAIAgents.Scenario.OpenAIChatCompletionClient")
    def test_creates_three_agents_with_system_messages(
        self, mock_client_cls, mock_factory_cls, mock_team_cls
    ):
        # main() should create exactly 3 agents: database, api, and excel
        mock_factory_instance = MagicMock()
        mock_factory_cls.return_value = mock_factory_instance
        mock_team_cls.return_value = MagicMock()

        from FrameworkAIAgents.Scenario import main

        with patch("FrameworkAIAgents.Scenario.Console", new=_make_console_mock()):
            asyncio.run(main())
        mock_factory_instance.create_database_agent.assert_called_once()
        mock_factory_instance.create_api_agent.assert_called_once()
        mock_factory_instance.create_excel_agent.assert_called_once()

    @patch("FrameworkAIAgents.Scenario.RoundRobinGroupChat")
    @patch("FrameworkAIAgents.Scenario.agentFactory")
    @patch("FrameworkAIAgents.Scenario.OpenAIChatCompletionClient")
    def test_database_agent_system_message_contains_key_instructions(
        self, mock_client_cls, mock_factory_cls, mock_team_cls
    ):
        # Database agent prompt must mention the target DB and tables
        mock_factory_instance = MagicMock()
        mock_factory_cls.return_value = mock_factory_instance
        mock_team_cls.return_value = MagicMock()

        from FrameworkAIAgents.Scenario import main

        with patch("FrameworkAIAgents.Scenario.Console", new=_make_console_mock()):
            asyncio.run(main())
        call_kwargs = mock_factory_instance.create_database_agent.call_args
        system_msg = call_kwargs.kwargs.get(
            "system_message", call_kwargs[1].get("system_message", "")
        )
        assert "rahulshettyacademy" in system_msg
        assert "RegistrationDetails" in system_msg
        assert "Usernames" in system_msg
        assert "DATABASE_DATA_READY" in system_msg

    @patch("FrameworkAIAgents.Scenario.RoundRobinGroupChat")
    @patch("FrameworkAIAgents.Scenario.agentFactory")
    @patch("FrameworkAIAgents.Scenario.OpenAIChatCompletionClient")
    def test_api_agent_system_message_contains_key_instructions(
        self, mock_client_cls, mock_factory_cls, mock_team_cls
    ):
        # API agent prompt must reference the registration endpoint and completion signal
        mock_factory_instance = MagicMock()
        mock_factory_cls.return_value = mock_factory_instance
        mock_team_cls.return_value = MagicMock()

        from FrameworkAIAgents.Scenario import main

        with patch("FrameworkAIAgents.Scenario.Console", new=_make_console_mock()):
            asyncio.run(main())
        call_kwargs = mock_factory_instance.create_api_agent.call_args
        system_msg = call_kwargs.kwargs.get(
            "system_message", call_kwargs[1].get("system_message", "")
        )
        assert "rahulshettyacademy.com/api/ecom/auth/register" in system_msg
        assert "API_TESTING_COMPLETE" in system_msg

    @patch("FrameworkAIAgents.Scenario.RoundRobinGroupChat")
    @patch("FrameworkAIAgents.Scenario.agentFactory")
    @patch("FrameworkAIAgents.Scenario.OpenAIChatCompletionClient")
    def test_excel_agent_system_message_contains_key_instructions(
        self, mock_client_cls, mock_factory_cls, mock_team_cls
    ):
        # Excel agent prompt must reference the output file and completion signal
        mock_factory_instance = MagicMock()
        mock_factory_cls.return_value = mock_factory_instance
        mock_team_cls.return_value = MagicMock()

        from FrameworkAIAgents.Scenario import main

        with patch("FrameworkAIAgents.Scenario.Console", new=_make_console_mock()):
            asyncio.run(main())
        call_kwargs = mock_factory_instance.create_excel_agent.call_args
        system_msg = call_kwargs.kwargs.get(
            "system_message", call_kwargs[1].get("system_message", "")
        )
        assert "newdata.xlsx" in system_msg
        assert "REGISTRATION PROCESS COMPLETE" in system_msg

    @patch("FrameworkAIAgents.Scenario.TextMentionTermination")
    @patch("FrameworkAIAgents.Scenario.RoundRobinGroupChat")
    @patch("FrameworkAIAgents.Scenario.agentFactory")
    @patch("FrameworkAIAgents.Scenario.OpenAIChatCompletionClient")
    def test_team_uses_round_robin_with_three_agents_and_termination(
        self,
        mock_client_cls,
        mock_factory_cls,
        mock_team_cls,
        mock_termination_cls,
    ):
        # RoundRobinGroupChat should receive all 3 agents and the termination condition
        mock_factory_instance = MagicMock()
        mock_factory_cls.return_value = mock_factory_instance
        mock_team_instance = MagicMock()
        mock_team_cls.return_value = mock_team_instance

        db_agent = MagicMock(name="db_agent")
        api_agent = MagicMock(name="api_agent")
        excel_agent = MagicMock(name="excel_agent")
        mock_factory_instance.create_database_agent.return_value = db_agent
        mock_factory_instance.create_api_agent.return_value = api_agent
        mock_factory_instance.create_excel_agent.return_value = excel_agent

        mock_termination = MagicMock()
        mock_termination_cls.return_value = mock_termination

        from FrameworkAIAgents.Scenario import main

        with patch("FrameworkAIAgents.Scenario.Console", new=_make_console_mock()):
            asyncio.run(main())
        mock_termination_cls.assert_called_once_with("REGISTRATION PROCESS COMPLETE")
        mock_team_cls.assert_called_once_with(
            participants=[db_agent, api_agent, excel_agent],
            termination_condition=mock_termination,
        )

    @patch("FrameworkAIAgents.Scenario.RoundRobinGroupChat")
    @patch("FrameworkAIAgents.Scenario.agentFactory")
    @patch("FrameworkAIAgents.Scenario.OpenAIChatCompletionClient")
    def test_main_returns_task_result_from_console(
        self, mock_client_cls, mock_factory_cls, mock_team_cls
    ):
        # main() should return whatever Console() resolves to
        expected_result = MagicMock(name="task_result")
        mock_team_cls.return_value = MagicMock()

        from FrameworkAIAgents.Scenario import main

        with patch("FrameworkAIAgents.Scenario.Console", new=_make_console_mock(expected_result)):
            result = asyncio.run(main())
        assert result is expected_result

    @patch("FrameworkAIAgents.Scenario.RoundRobinGroupChat")
    @patch("FrameworkAIAgents.Scenario.agentFactory")
    @patch("FrameworkAIAgents.Scenario.OpenAIChatCompletionClient")
    def test_console_receives_team_run_stream(
        self, mock_client_cls, mock_factory_cls, mock_team_cls
    ):
        # Console should be awaited with team.run_stream() output
        mock_team_instance = MagicMock()
        mock_team_cls.return_value = mock_team_instance
        mock_stream = MagicMock(name="stream")
        mock_team_instance.run_stream.return_value = mock_stream

        from FrameworkAIAgents.Scenario import main

        mock_console = _make_console_mock()
        with patch("FrameworkAIAgents.Scenario.Console", new=mock_console):
            asyncio.run(main())
        mock_team_instance.run_stream.assert_called_once()
        task_arg = mock_team_instance.run_stream.call_args.kwargs.get(
            "task", mock_team_instance.run_stream.call_args[1].get("task", "")
        )
        assert "Execute Sequential User Registration Process" in task_arg
        mock_console.assert_awaited_once_with(mock_stream)

    def test_main_raises_when_api_key_missing(self, monkeypatch):
        # If OPENAI_API_KEY is not set, main() should propagate ValueError
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        from FrameworkAIAgents.Scenario import main

        with pytest.raises(
            ValueError, match="OPENAI_API_KEY environment variable is not set"
        ):
            asyncio.run(main())

    @patch("FrameworkAIAgents.Scenario.RoundRobinGroupChat")
    @patch("FrameworkAIAgents.Scenario.agentFactory")
    @patch("FrameworkAIAgents.Scenario.OpenAIChatCompletionClient")
    def test_task_message_contains_all_three_steps(
        self, mock_client_cls, mock_factory_cls, mock_team_cls
    ):
        # The task string passed to run_stream must describe all 3 sequential steps
        mock_team_instance = MagicMock()
        mock_team_cls.return_value = mock_team_instance

        from FrameworkAIAgents.Scenario import main

        with patch("FrameworkAIAgents.Scenario.Console", new=_make_console_mock()):
            asyncio.run(main())
        task_arg = mock_team_instance.run_stream.call_args.kwargs.get(
            "task", mock_team_instance.run_stream.call_args[1].get("task", "")
        )
        assert "STEP 1 - DatabaseAgent" in task_arg
        assert "STEP 2 - APIAgent" in task_arg
        assert "STEP 3 - ExcelAgent" in task_arg
        assert "Pass data.clearly between agents" in task_arg

    @patch("FrameworkAIAgents.Scenario.RoundRobinGroupChat")
    @patch("FrameworkAIAgents.Scenario.agentFactory")
    @patch("FrameworkAIAgents.Scenario.OpenAIChatCompletionClient")
    def test_agents_created_in_correct_order(
        self, mock_client_cls, mock_factory_cls, mock_team_cls
    ):
        # Agents must be created in order: database -> api -> excel for RoundRobin
        call_order = []
        mock_factory_instance = MagicMock()
        mock_factory_cls.return_value = mock_factory_instance
        mock_team_cls.return_value = MagicMock()

        mock_factory_instance.create_database_agent.side_effect = (
            lambda **kw: call_order.append("database") or MagicMock()
        )
        mock_factory_instance.create_api_agent.side_effect = (
            lambda **kw: call_order.append("api") or MagicMock()
        )
        mock_factory_instance.create_excel_agent.side_effect = (
            lambda **kw: call_order.append("excel") or MagicMock()
        )

        from FrameworkAIAgents.Scenario import main

        with patch("FrameworkAIAgents.Scenario.Console", new=_make_console_mock()):
            asyncio.run(main())
        assert call_order == ["database", "api", "excel"]
