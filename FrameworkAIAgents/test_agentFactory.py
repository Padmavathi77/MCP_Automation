# pylint: disable=redefined-outer-name, unused-argument
import sys
from unittest.mock import MagicMock, patch

import pytest

mock_autogen_agentchat = MagicMock()
mock_autogen_agentchat_agents = MagicMock()
mock_autogen_ext = MagicMock()
mock_autogen_ext_tools = MagicMock()
mock_autogen_ext_tools_mcp = MagicMock()
mock_autogen_ext_models = MagicMock()
mock_autogen_ext_models_openai = MagicMock()
mock_dotenv = MagicMock()

sys.modules.setdefault("autogen_agentchat", mock_autogen_agentchat)
sys.modules.setdefault("autogen_agentchat.agents", mock_autogen_agentchat_agents)
sys.modules.setdefault("autogen_agentchat.conditions", MagicMock())
sys.modules.setdefault("autogen_agentchat.teams", MagicMock())
sys.modules.setdefault("autogen_agentchat.ui", MagicMock())
sys.modules.setdefault("autogen_ext", mock_autogen_ext)
sys.modules.setdefault("autogen_ext.tools", mock_autogen_ext_tools)
sys.modules.setdefault("autogen_ext.tools.mcp", mock_autogen_ext_tools_mcp)
sys.modules.setdefault("autogen_ext.models", mock_autogen_ext_models)
sys.modules.setdefault("autogen_ext.models.openai", mock_autogen_ext_models_openai)
sys.modules.setdefault("dotenv", mock_dotenv)

from FrameworkAIAgents.agentFactory import agentFactory


@pytest.fixture
def mock_model_client():
    return MagicMock(name="mock_model_client")


@pytest.fixture
def mock_mcp_config():
    with patch("FrameworkAIAgents.agentFactory.McpConfig") as MockMcpConfig:
        instance = MockMcpConfig.return_value
        instance.get_mysql_workbench.return_value = MagicMock(name="mysql_wb")
        instance.get_rest_api_workbench.return_value = MagicMock(name="rest_api_wb")
        instance.get_filesystem_workbench.return_value = MagicMock(name="filesystem_wb")
        instance.get_excel_workbench.return_value = MagicMock(name="excel_wb")
        yield instance


@pytest.fixture
def mock_assistant_agent():
    with patch("FrameworkAIAgents.agentFactory.AssistantAgent") as MockAgent:
        yield MockAgent


@pytest.fixture
def factory(mock_model_client, mock_mcp_config):
    return agentFactory(mock_model_client)


class TestAgentFactoryInit:
    def test_stores_model_client(self, mock_model_client, mock_mcp_config):
        # Verify constructor stores the model_client for later use by factory methods
        factory = agentFactory(mock_model_client)
        assert factory.model_client is mock_model_client

    def test_creates_mcp_config(self, mock_model_client, mock_mcp_config):
        # Verify constructor creates an McpConfig instance for workbench access
        factory = agentFactory(mock_model_client)
        assert factory.mcp_config is mock_mcp_config

    def test_none_model_client_stored(self, mock_mcp_config):
        # Verify None model_client is accepted (validation deferred to AssistantAgent)
        factory = agentFactory(None)
        assert factory.model_client is None


class TestCreateDatabaseAgent:
    def test_passes_correct_name(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify the database agent is created with name "DataBaseAgent"
        factory.create_database_agent(system_message="db instructions")
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["name"] == "DataBaseAgent"

    def test_passes_model_client(self, factory, mock_assistant_agent, mock_mcp_config, mock_model_client):
        # Verify the factory's model_client is forwarded to AssistantAgent
        factory.create_database_agent(system_message="db instructions")
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["model_client"] is mock_model_client

    def test_passes_mysql_workbench(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify MySQL workbench from McpConfig is wired as the agent's workbench
        factory.create_database_agent(system_message="db instructions")
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["workbench"] is mock_mcp_config.get_mysql_workbench.return_value

    def test_passes_system_message(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify the system_message argument is forwarded exactly
        msg = "You are a database specialist."
        factory.create_database_agent(system_message=msg)
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["system_message"] == msg

    def test_returns_assistant_agent_instance(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify the method returns whatever AssistantAgent() produces
        result = factory.create_database_agent(system_message="test")
        assert result is mock_assistant_agent.return_value

    def test_empty_system_message(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify empty string system_message is passed through without modification
        factory.create_database_agent(system_message="")
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["system_message"] == ""

    def test_multiline_system_message(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify multiline system messages with special chars are preserved
        msg = "Line 1\nLine 2\n\tIndented\nUnicode: 日本語 émojis 🎉"
        factory.create_database_agent(system_message=msg)
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["system_message"] == msg


class TestCreateApiAgent:
    def test_passes_correct_name(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify the API agent is created with name "APIAgent"
        factory.create_api_agent(system_message="api instructions")
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["name"] == "APIAgent"

    def test_passes_model_client(self, factory, mock_assistant_agent, mock_mcp_config, mock_model_client):
        # Verify the factory's model_client is forwarded to the API agent
        factory.create_api_agent(system_message="api instructions")
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["model_client"] is mock_model_client

    def test_passes_workbench_as_list_of_two(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify workbench is a list containing both REST API and filesystem workbenches
        factory.create_api_agent(system_message="api instructions")
        _, kwargs = mock_assistant_agent.call_args
        workbench = kwargs["workbench"]
        assert isinstance(workbench, list)
        assert len(workbench) == 2

    def test_workbench_contains_rest_api_first(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify REST API workbench is the first element (order matters for agent behavior)
        factory.create_api_agent(system_message="api instructions")
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["workbench"][0] is mock_mcp_config.get_rest_api_workbench.return_value

    def test_workbench_contains_filesystem_second(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify filesystem workbench is the second element
        factory.create_api_agent(system_message="api instructions")
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["workbench"][1] is mock_mcp_config.get_filesystem_workbench.return_value

    def test_passes_system_message(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify system_message is forwarded exactly to the API agent
        msg = "You are an API testing specialist."
        factory.create_api_agent(system_message=msg)
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["system_message"] == msg

    def test_returns_assistant_agent_instance(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify the method returns the constructed AssistantAgent
        result = factory.create_api_agent(system_message="test")
        assert result is mock_assistant_agent.return_value


class TestCreateExcelAgent:
    def test_passes_correct_name(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify the Excel agent is created with name "ExcelAgent"
        factory.create_excel_agent(system_message="excel instructions")
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["name"] == "ExcelAgent"

    def test_passes_model_client(self, factory, mock_assistant_agent, mock_mcp_config, mock_model_client):
        # Verify the factory's model_client is forwarded to the Excel agent
        factory.create_excel_agent(system_message="excel instructions")
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["model_client"] is mock_model_client

    def test_passes_excel_workbench(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify Excel workbench from McpConfig is wired as the agent's workbench
        factory.create_excel_agent(system_message="excel instructions")
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["workbench"] is mock_mcp_config.get_excel_workbench.return_value

    def test_passes_system_message(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify explicit system_message is forwarded to the Excel agent
        msg = "You are an Excel specialist."
        factory.create_excel_agent(system_message=msg)
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["system_message"] == msg

    def test_default_system_message_is_none(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify system_message defaults to None when not provided
        factory.create_excel_agent()
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["system_message"] is None

    def test_returns_assistant_agent_instance(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify the method returns the constructed AssistantAgent
        result = factory.create_excel_agent(system_message="test")
        assert result is mock_assistant_agent.return_value


class TestMultipleAgentCreation:
    def test_each_call_creates_new_agent(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify each factory method invocation calls AssistantAgent separately
        factory.create_database_agent(system_message="db")
        factory.create_api_agent(system_message="api")
        factory.create_excel_agent(system_message="excel")
        assert mock_assistant_agent.call_count == 3

    def test_agents_have_distinct_names(self, factory, mock_assistant_agent, mock_mcp_config):
        # Verify all three agent types get different names to avoid identity conflicts
        factory.create_database_agent(system_message="db")
        factory.create_api_agent(system_message="api")
        factory.create_excel_agent(system_message="excel")
        names = [c.kwargs["name"] for c in mock_assistant_agent.call_args_list]
        assert names == ["DataBaseAgent", "APIAgent", "ExcelAgent"]

    def test_separate_factories_use_own_model_client(self, mock_assistant_agent, mock_mcp_config):
        # Verify two factories with different model_clients pass their own client
        client_a = MagicMock(name="client_a")
        client_b = MagicMock(name="client_b")
        factory_a = agentFactory(client_a)
        factory_b = agentFactory(client_b)
        factory_a.create_database_agent(system_message="a")
        factory_b.create_database_agent(system_message="b")
        calls = mock_assistant_agent.call_args_list
        assert calls[0].kwargs["model_client"] is client_a
        assert calls[1].kwargs["model_client"] is client_b


class TestAgentFactoryInitEdgeCases:
    def test_non_standard_model_client_types(self, mock_mcp_config):
        # Verify factory accepts arbitrary types as model_client (duck typing)
        for client in ["string_client", 42, {"key": "value"}, [1, 2, 3]]:
            f = agentFactory(client)
            assert f.model_client is client

    def test_mcp_config_exception_propagates(self):
        # Verify McpConfig() failure during init propagates to caller
        with patch(
            "FrameworkAIAgents.agentFactory.McpConfig",
            side_effect=RuntimeError("config broken"),
        ):
            with pytest.raises(RuntimeError, match="config broken"):
                agentFactory(MagicMock())


class TestCreateDatabaseAgentEdgeCases:
    def test_assistant_agent_exception_propagates(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify AssistantAgent construction failure propagates to caller
        mock_assistant_agent.side_effect = TypeError("bad args")
        with pytest.raises(TypeError, match="bad args"):
            factory.create_database_agent(system_message="test")

    def test_workbench_exception_propagates(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify get_mysql_workbench() failure propagates before AssistantAgent is called
        mock_mcp_config.get_mysql_workbench.side_effect = ConnectionError("db down")
        with pytest.raises(ConnectionError, match="db down"):
            factory.create_database_agent(system_message="test")

    def test_calls_get_mysql_workbench_exactly_once(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify get_mysql_workbench is called once per create_database_agent call
        factory.create_database_agent(system_message="test")
        mock_mcp_config.get_mysql_workbench.assert_called_once()

    def test_non_string_system_message(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify non-string system_message (dict) is passed through without validation
        msg = {"role": "system", "content": "structured"}
        factory.create_database_agent(system_message=msg)
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["system_message"] is msg

    def test_repeated_calls_create_separate_agents(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify calling create_database_agent twice produces two separate calls
        r1 = factory.create_database_agent(system_message="first")
        r2 = factory.create_database_agent(system_message="second")
        assert mock_assistant_agent.call_count == 2
        calls = mock_assistant_agent.call_args_list
        assert calls[0].kwargs["system_message"] == "first"
        assert calls[1].kwargs["system_message"] == "second"

    def test_very_large_system_message(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify a very large system_message is passed through without truncation
        msg = "x" * 100_000
        factory.create_database_agent(system_message=msg)
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["system_message"] == msg
        assert len(kwargs["system_message"]) == 100_000


class TestCreateApiAgentEdgeCases:
    def test_assistant_agent_exception_propagates(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify AssistantAgent construction failure propagates to caller
        mock_assistant_agent.side_effect = ValueError("invalid config")
        with pytest.raises(ValueError, match="invalid config"):
            factory.create_api_agent(system_message="test")

    def test_rest_api_workbench_exception_propagates(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify get_rest_api_workbench() failure propagates
        mock_mcp_config.get_rest_api_workbench.side_effect = OSError("network error")
        with pytest.raises(OSError, match="network error"):
            factory.create_api_agent(system_message="test")

    def test_filesystem_workbench_exception_propagates(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify get_filesystem_workbench() failure propagates
        mock_mcp_config.get_filesystem_workbench.side_effect = PermissionError("denied")
        with pytest.raises(PermissionError, match="denied"):
            factory.create_api_agent(system_message="test")

    def test_calls_both_workbench_methods_exactly_once(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify both workbench getters are called once per create_api_agent call
        factory.create_api_agent(system_message="test")
        mock_mcp_config.get_rest_api_workbench.assert_called_once()
        mock_mcp_config.get_filesystem_workbench.assert_called_once()

    def test_empty_system_message(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify empty string system_message is passed through for API agent
        factory.create_api_agent(system_message="")
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["system_message"] == ""

    def test_non_string_system_message(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify non-string system_message (list) is passed through without validation
        msg = ["step1", "step2"]
        factory.create_api_agent(system_message=msg)
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["system_message"] is msg


class TestCreateExcelAgentEdgeCases:
    def test_assistant_agent_exception_propagates(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify AssistantAgent construction failure propagates to caller
        mock_assistant_agent.side_effect = RuntimeError("agent init failed")
        with pytest.raises(RuntimeError, match="agent init failed"):
            factory.create_excel_agent(system_message="test")

    def test_excel_workbench_exception_propagates(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify get_excel_workbench() failure propagates
        mock_mcp_config.get_excel_workbench.side_effect = FileNotFoundError("no excel")
        with pytest.raises(FileNotFoundError, match="no excel"):
            factory.create_excel_agent(system_message="test")

    def test_calls_get_excel_workbench_exactly_once(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify get_excel_workbench is called once per create_excel_agent call
        factory.create_excel_agent(system_message="test")
        mock_mcp_config.get_excel_workbench.assert_called_once()

    def test_empty_system_message(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify empty string system_message is passed through for Excel agent
        factory.create_excel_agent(system_message="")
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["system_message"] == ""

    def test_non_string_system_message(
        self, factory, mock_assistant_agent, mock_mcp_config
    ):
        # Verify non-string system_message (int) is passed through without validation
        factory.create_excel_agent(system_message=999)
        _, kwargs = mock_assistant_agent.call_args
        assert kwargs["system_message"] == 999
