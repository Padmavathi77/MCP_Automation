# pylint: disable=redefined-outer-name, unused-argument
import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

mock_autogen_agentchat = MagicMock()
mock_autogen_ext = MagicMock()
mock_dotenv = MagicMock()

sys.modules["autogen_agentchat"] = mock_autogen_agentchat
sys.modules["autogen_agentchat.agents"] = mock_autogen_agentchat.agents
sys.modules["autogen_agentchat.conditions"] = mock_autogen_agentchat.conditions
sys.modules["autogen_agentchat.teams"] = mock_autogen_agentchat.teams
sys.modules["autogen_agentchat.ui"] = mock_autogen_agentchat.ui
sys.modules["autogen_ext"] = mock_autogen_ext
sys.modules["autogen_ext.models"] = mock_autogen_ext.models
sys.modules["autogen_ext.models.openai"] = mock_autogen_ext.models.openai
sys.modules["autogen_ext.tools"] = mock_autogen_ext.tools
sys.modules["autogen_ext.tools.mcp"] = mock_autogen_ext.tools.mcp
sys.modules["dotenv"] = mock_dotenv

from FrameworkAIAgents import Scenario  # noqa: E402


class TestSetupEnv:
    def test_setup_env_sets_key_when_present(self, monkeypatch):
        # Verify that a valid OPENAI_API_KEY is loaded and set in os.environ
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
        with patch.object(Scenario, "load_dotenv") as mock_ld:
            result = Scenario.setup_env()
        mock_ld.assert_called_once()
        assert result == "test-key-123"
        assert os.environ["OPENAI_API_KEY"] == "test-key-123"

    def test_setup_env_raises_when_key_missing(self, monkeypatch):
        # Missing OPENAI_API_KEY should raise ValueError, not TypeError from os.environ[None]
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with patch.object(Scenario, "load_dotenv"):
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set"):
                Scenario.setup_env()

    def test_setup_env_raises_when_key_empty_string(self, monkeypatch):
        # Empty string is falsy and should be rejected just like None
        monkeypatch.setenv("OPENAI_API_KEY", "")
        with patch.object(Scenario, "load_dotenv"):
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set"):
                Scenario.setup_env()

    def test_setup_env_calls_load_dotenv(self, monkeypatch):
        # Ensure load_dotenv is called to load .env file before reading env vars
        monkeypatch.setenv("OPENAI_API_KEY", "some-key")
        with patch.object(Scenario, "load_dotenv") as mock_ld:
            Scenario.setup_env()
        mock_ld.assert_called_once()

    def test_setup_env_with_whitespace_only_key(self, monkeypatch):
        # Whitespace-only key is truthy so it passes validation (documents current behavior)
        monkeypatch.setenv("OPENAI_API_KEY", "   ")
        with patch.object(Scenario, "load_dotenv"):
            result = Scenario.setup_env()
        assert result == "   "

    def test_setup_env_with_special_characters_in_key(self, monkeypatch):
        # API keys can contain special characters; verify they pass through correctly
        key = "sk-proj_abc123!@#$%^&*()"
        monkeypatch.setenv("OPENAI_API_KEY", key)
        with patch.object(Scenario, "load_dotenv"):
            result = Scenario.setup_env()
        assert result == key
        assert os.environ["OPENAI_API_KEY"] == key


class TestConstants:
    def test_db_system_message_contains_database_instructions(self):
        # DB agent message must reference the correct database and table names
        assert "rahulshettyacademy" in Scenario.DB_SYSTEM_MESSAGE
        assert "RegistrationDetails" in Scenario.DB_SYSTEM_MESSAGE
        assert "Usernames" in Scenario.DB_SYSTEM_MESSAGE
        assert "DATABASE_DATA_READY" in Scenario.DB_SYSTEM_MESSAGE

    def test_api_system_message_contains_api_instructions(self):
        # API agent message must reference the registration endpoint and completion signal
        assert "rahulshettyacademy.com/api/ecom/auth/register" in Scenario.API_SYSTEM_MESSAGE
        assert "API_TESTING_COMPLETE" in Scenario.API_SYSTEM_MESSAGE
        assert "Content-Type: application/json" in Scenario.API_SYSTEM_MESSAGE

    def test_excel_system_message_contains_excel_instructions(self):
        # Excel agent message must reference the output file and completion signal
        assert "newdata.xlsx" in Scenario.EXCEL_SYSTEM_MESSAGE
        assert "REGISTRATION PROCESS COMPLETE" in Scenario.EXCEL_SYSTEM_MESSAGE
        assert "RegistrationData" in Scenario.EXCEL_SYSTEM_MESSAGE

    def test_task_description_references_all_steps(self):
        # Task description must mention all three agents' steps in order
        assert "DatabaseAgent" in Scenario.TASK_DESCRIPTION
        assert "APIAgent" in Scenario.TASK_DESCRIPTION
        assert "ExcelAgent" in Scenario.TASK_DESCRIPTION
        assert "STEP 1" in Scenario.TASK_DESCRIPTION
        assert "STEP 2" in Scenario.TASK_DESCRIPTION
        assert "STEP 3" in Scenario.TASK_DESCRIPTION

    def test_constants_are_strings(self):
        # All system message constants must be str type
        assert isinstance(Scenario.DB_SYSTEM_MESSAGE, str)
        assert isinstance(Scenario.API_SYSTEM_MESSAGE, str)
        assert isinstance(Scenario.EXCEL_SYSTEM_MESSAGE, str)
        assert isinstance(Scenario.TASK_DESCRIPTION, str)

    def test_all_system_messages_are_nonempty(self):
        # Guard against accidentally emptying a system message constant
        assert len(Scenario.DB_SYSTEM_MESSAGE) > 50
        assert len(Scenario.API_SYSTEM_MESSAGE) > 50
        assert len(Scenario.EXCEL_SYSTEM_MESSAGE) > 50
        assert len(Scenario.TASK_DESCRIPTION) > 50


@patch("FrameworkAIAgents.Scenario.Console", new_callable=AsyncMock)
@patch("FrameworkAIAgents.Scenario.RoundRobinGroupChat")
@patch("FrameworkAIAgents.Scenario.TextMentionTermination")
@patch("FrameworkAIAgents.Scenario.agentFactory")
@patch("FrameworkAIAgents.Scenario.OpenAIChatCompletionClient")
class TestMain:
    def test_main_creates_model_client_with_gpt4o(
        self, mock_client_cls, mock_factory_cls, mock_term, mock_team_cls, mock_console
    ):
        # Verify the correct model name is passed to OpenAIChatCompletionClient
        mock_team_instance = MagicMock()
        mock_team_instance.run_stream = MagicMock(return_value=AsyncMock())
        mock_team_cls.return_value = mock_team_instance
        mock_console.return_value = "result"

        asyncio.run(Scenario.main())
        mock_client_cls.assert_called_once_with(model="gpt-4o")

    def test_main_creates_three_agents_via_factory(
        self, mock_client_cls, mock_factory_cls, mock_term, mock_team_cls, mock_console
    ):
        # Verify all three agents (DB, API, Excel) are created with correct system messages
        mock_factory = MagicMock()
        mock_factory_cls.return_value = mock_factory
        mock_team_instance = MagicMock()
        mock_team_instance.run_stream = MagicMock(return_value=AsyncMock())
        mock_team_cls.return_value = mock_team_instance
        mock_console.return_value = "result"

        asyncio.run(Scenario.main())

        mock_factory.create_database_agent.assert_called_once_with(
            system_message=Scenario.DB_SYSTEM_MESSAGE
        )
        mock_factory.create_api_agent.assert_called_once_with(
            system_message=Scenario.API_SYSTEM_MESSAGE
        )
        mock_factory.create_excel_agent.assert_called_once_with(
            system_message=Scenario.EXCEL_SYSTEM_MESSAGE
        )

    def test_main_creates_round_robin_team_with_correct_participants(
        self, mock_client_cls, mock_factory_cls, mock_term, mock_team_cls, mock_console
    ):
        # Verify team is created with all 3 agents in correct order and termination condition
        mock_factory = MagicMock()
        mock_factory_cls.return_value = mock_factory
        db_agent = MagicMock(name="db_agent")
        api_agent = MagicMock(name="api_agent")
        excel_agent = MagicMock(name="excel_agent")
        mock_factory.create_database_agent.return_value = db_agent
        mock_factory.create_api_agent.return_value = api_agent
        mock_factory.create_excel_agent.return_value = excel_agent

        mock_term_instance = MagicMock()
        mock_term.return_value = mock_term_instance

        mock_team_instance = MagicMock()
        mock_team_instance.run_stream = MagicMock(return_value=AsyncMock())
        mock_team_cls.return_value = mock_team_instance
        mock_console.return_value = "result"

        asyncio.run(Scenario.main())

        mock_term.assert_called_once_with("REGISTRATION PROCESS COMPLETE")
        mock_team_cls.assert_called_once_with(
            participants=[db_agent, api_agent, excel_agent],
            termination_condition=mock_term_instance,
        )

    def test_main_runs_team_stream_with_task_description(
        self, mock_client_cls, mock_factory_cls, mock_term, mock_team_cls, mock_console
    ):
        # Verify run_stream is called with the correct task description
        mock_factory = MagicMock()
        mock_factory_cls.return_value = mock_factory
        mock_team_instance = MagicMock()
        mock_stream = AsyncMock()
        mock_team_instance.run_stream.return_value = mock_stream
        mock_team_cls.return_value = mock_team_instance
        mock_console.return_value = "task_result"

        result = asyncio.run(Scenario.main())

        mock_team_instance.run_stream.assert_called_once_with(task=Scenario.TASK_DESCRIPTION)
        mock_console.assert_called_once_with(mock_stream)
        assert result == "task_result"

    def test_main_returns_task_result(
        self, mock_client_cls, mock_factory_cls, mock_term, mock_team_cls, mock_console
    ):
        # Verify main() returns the Console output (the task result)
        mock_team_instance = MagicMock()
        mock_team_instance.run_stream = MagicMock(return_value=AsyncMock())
        mock_team_cls.return_value = mock_team_instance
        expected = {"status": "complete", "messages": ["done"]}
        mock_console.return_value = expected

        result = asyncio.run(Scenario.main())
        assert result == expected

    def test_main_propagates_model_client_error(
        self, mock_client_cls, mock_factory_cls, mock_term, mock_team_cls, mock_console
    ):
        # If OpenAIChatCompletionClient raises, main() should propagate the error
        mock_client_cls.side_effect = RuntimeError("Invalid API key")
        with pytest.raises(RuntimeError, match="Invalid API key"):
            asyncio.run(Scenario.main())

    def test_main_propagates_factory_error(
        self, mock_client_cls, mock_factory_cls, mock_term, mock_team_cls, mock_console
    ):
        # If agentFactory raises during agent creation, main() should propagate
        mock_factory = MagicMock()
        mock_factory_cls.return_value = mock_factory
        mock_factory.create_database_agent.side_effect = ConnectionError("DB unavailable")
        with pytest.raises(ConnectionError, match="DB unavailable"):
            asyncio.run(Scenario.main())

    def test_main_propagates_api_agent_creation_error(
        self, mock_client_cls, mock_factory_cls, mock_term, mock_team_cls, mock_console
    ):
        # If API agent creation fails, main() should propagate the error
        mock_factory = MagicMock()
        mock_factory_cls.return_value = mock_factory
        mock_factory.create_api_agent.side_effect = ValueError("Bad config")
        with pytest.raises(ValueError, match="Bad config"):
            asyncio.run(Scenario.main())

    def test_main_propagates_excel_agent_creation_error(
        self, mock_client_cls, mock_factory_cls, mock_term, mock_team_cls, mock_console
    ):
        # If Excel agent creation fails, main() should propagate the error
        mock_factory = MagicMock()
        mock_factory_cls.return_value = mock_factory
        mock_factory.create_excel_agent.side_effect = OSError("Workbench unavailable")
        with pytest.raises(OSError, match="Workbench unavailable"):
            asyncio.run(Scenario.main())

    def test_main_propagates_console_error(
        self, mock_client_cls, mock_factory_cls, mock_term, mock_team_cls, mock_console
    ):
        # If Console raises (e.g., stream failure), main() should propagate
        mock_team_instance = MagicMock()
        mock_team_instance.run_stream = MagicMock(return_value=AsyncMock())
        mock_team_cls.return_value = mock_team_instance
        mock_console.side_effect = IOError("Stream broken")
        with pytest.raises(IOError, match="Stream broken"):
            asyncio.run(Scenario.main())

    def test_main_propagates_team_creation_error(
        self, mock_client_cls, mock_factory_cls, mock_term, mock_team_cls, mock_console
    ):
        # If RoundRobinGroupChat constructor raises, main() should propagate
        mock_team_cls.side_effect = TypeError("Invalid participants")
        with pytest.raises(TypeError, match="Invalid participants"):
            asyncio.run(Scenario.main())

    def test_main_passes_model_client_to_factory(
        self, mock_client_cls, mock_factory_cls, mock_term, mock_team_cls, mock_console
    ):
        # Verify the model_client instance is passed to agentFactory constructor
        mock_model = MagicMock()
        mock_client_cls.return_value = mock_model
        mock_team_instance = MagicMock()
        mock_team_instance.run_stream = MagicMock(return_value=AsyncMock())
        mock_team_cls.return_value = mock_team_instance
        mock_console.return_value = "result"

        asyncio.run(Scenario.main())
        mock_factory_cls.assert_called_once_with(mock_model)


class TestModuleStructure:
    def test_module_has_main_function(self):
        # Verify main is an async function exposed at module level
        assert hasattr(Scenario, "main")
        assert asyncio.iscoroutinefunction(Scenario.main)

    def test_module_has_setup_env_function(self):
        # Verify setup_env is a regular function exposed at module level
        assert hasattr(Scenario, "setup_env")
        assert callable(Scenario.setup_env)
        assert not asyncio.iscoroutinefunction(Scenario.setup_env)
