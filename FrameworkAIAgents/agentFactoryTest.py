# pylint: disable=redefined-outer-name, unused-argument
from unittest.mock import MagicMock, patch

from FrameworkAIAgents.agentFactory import agentFactory

import pytest


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
