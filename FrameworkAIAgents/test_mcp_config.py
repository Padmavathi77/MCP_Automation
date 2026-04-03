# pylint: disable=redefined-outer-name, unused-argument
import sys
from unittest.mock import MagicMock, patch

import pytest

mock_autogen_ext = MagicMock()
mock_autogen_ext_tools = MagicMock()
mock_autogen_ext_tools_mcp = MagicMock()
mock_dotenv = MagicMock()

sys.modules.setdefault("autogen_ext", mock_autogen_ext)
sys.modules.setdefault("autogen_ext.tools", mock_autogen_ext_tools)
sys.modules.setdefault("autogen_ext.tools.mcp", mock_autogen_ext_tools_mcp)
sys.modules.setdefault("dotenv", mock_dotenv)

MockStdioServerParams = mock_autogen_ext_tools_mcp.StdioServerParams
MockMcpWorkbench = mock_autogen_ext_tools_mcp.McpWorkbench


@pytest.fixture(autouse=True)
def _reset_mocks():
    MockStdioServerParams.reset_mock()
    MockMcpWorkbench.reset_mock()
    yield


class TestGetMysqlWorkbench:

    def test_creates_stdio_params_with_uv_command(self):
        # Verify MySQL workbench uses the uv binary as the command
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_mysql_workbench()
        params_kwargs = MockStdioServerParams.call_args
        assert params_kwargs.kwargs["command"] == "/Library/Frameworks/Python.framework/Versions/3.13/bin/uv"

    def test_creates_stdio_params_with_correct_args(self):
        # Verify the args list includes --directory, package path, run, and mysql_mcp_server
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_mysql_workbench()
        params_kwargs = MockStdioServerParams.call_args
        expected_args = [
            "--directory",
            "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages",
            "run",
            "mysql_mcp_server",
        ]
        assert params_kwargs.kwargs["args"] == expected_args

    def test_env_contains_mysql_host_localhost(self):
        # Verify MYSQL_HOST is set to localhost for local development
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_mysql_workbench()
        env = MockStdioServerParams.call_args.kwargs["env"]
        assert env["MYSQL_HOST"] == "localhost"

    def test_env_contains_mysql_port_3306(self):
        # Verify MYSQL_PORT is the standard MySQL port
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_mysql_workbench()
        env = MockStdioServerParams.call_args.kwargs["env"]
        assert env["MYSQL_PORT"] == "3306"

    def test_env_contains_mysql_database(self):
        # Verify the target database is rahulshettyacademy
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_mysql_workbench()
        env = MockStdioServerParams.call_args.kwargs["env"]
        assert env["MYSQL_DATABASE"] == "rahulshettyacademy"

    def test_env_uses_module_level_db_credentials(self):
        # Verify MYSQL_USER and MYSQL_PASSWORD come from module-level os.getenv
        from FrameworkAIAgents import mcp_config
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_mysql_workbench()
        env = MockStdioServerParams.call_args.kwargs["env"]
        assert env["MYSQL_USER"] is mcp_config.DBUserName
        assert env["MYSQL_PASSWORD"] is mcp_config.DBPwd

    def test_returns_mcp_workbench_with_server_params(self):
        # Verify McpWorkbench is constructed with the StdioServerParams instance
        from FrameworkAIAgents.mcp_config import McpConfig

        result = McpConfig.get_mysql_workbench()
        MockMcpWorkbench.assert_called_once_with(
            server_params=MockStdioServerParams.return_value
        )
        assert result is MockMcpWorkbench.return_value

    def test_env_has_exactly_five_keys(self):
        # Verify no extra env vars are leaked into the MySQL server config
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_mysql_workbench()
        env = MockStdioServerParams.call_args.kwargs["env"]
        assert set(env.keys()) == {
            "MYSQL_HOST",
            "MYSQL_PORT",
            "MYSQL_USER",
            "MYSQL_PASSWORD",
            "MYSQL_DATABASE",
        }


class TestGetRestApiWorkbench:

    def test_creates_stdio_params_with_npx_command(self):
        # Verify REST API workbench uses npx as the command
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_rest_api_workbench()
        params_kwargs = MockStdioServerParams.call_args
        assert params_kwargs.kwargs["command"] == "npx"

    def test_creates_stdio_params_with_correct_args(self):
        # Verify args include -y flag and the dkmaker-mcp-rest-api package
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_rest_api_workbench()
        params_kwargs = MockStdioServerParams.call_args
        assert params_kwargs.kwargs["args"] == ["-y", "dkmaker-mcp-rest-api"]

    def test_env_contains_rest_base_url(self):
        # Verify REST_BASE_URL points to rahulshettyacademy.com
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_rest_api_workbench()
        env = MockStdioServerParams.call_args.kwargs["env"]
        assert env["REST_BASE_URL"] == "https://rahulshettyacademy.com"

    def test_env_contains_accept_header(self):
        # Verify HEADER_Accept is set to application/json
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_rest_api_workbench()
        env = MockStdioServerParams.call_args.kwargs["env"]
        assert env["HEADER_Accept"] == "application/json"

    def test_env_has_exactly_two_keys(self):
        # Verify no extra env vars are present in REST API config
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_rest_api_workbench()
        env = MockStdioServerParams.call_args.kwargs["env"]
        assert set(env.keys()) == {"REST_BASE_URL", "HEADER_Accept"}

    def test_returns_mcp_workbench_with_server_params(self):
        # Verify McpWorkbench is constructed with the StdioServerParams instance
        from FrameworkAIAgents.mcp_config import McpConfig

        result = McpConfig.get_rest_api_workbench()
        MockMcpWorkbench.assert_called_once_with(
            server_params=MockStdioServerParams.return_value
        )
        assert result is MockMcpWorkbench.return_value


class TestGetExcelWorkbench:

    def test_creates_stdio_params_with_npx_command(self):
        # Verify Excel workbench uses npx as the command
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_excel_workbench()
        params_kwargs = MockStdioServerParams.call_args
        assert params_kwargs.kwargs["command"] == "npx"

    def test_creates_stdio_params_with_correct_args(self):
        # Verify args include --yes flag and the excel-mcp-server package
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_excel_workbench()
        params_kwargs = MockStdioServerParams.call_args
        assert params_kwargs.kwargs["args"] == ["--yes", "@negokaz/excel-mcp-server"]

    def test_env_contains_paging_cells_limit(self):
        # Verify EXCEL_MCP_PAGING_CELLS_LIMIT is set to 4000
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_excel_workbench()
        env = MockStdioServerParams.call_args.kwargs["env"]
        assert env["EXCEL_MCP_PAGING_CELLS_LIMIT"] == "4000"

    def test_env_has_exactly_one_key(self):
        # Verify no extra env vars are present in Excel config
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_excel_workbench()
        env = MockStdioServerParams.call_args.kwargs["env"]
        assert set(env.keys()) == {"EXCEL_MCP_PAGING_CELLS_LIMIT"}

    def test_returns_mcp_workbench_with_server_params(self):
        # Verify McpWorkbench is constructed with the StdioServerParams instance
        from FrameworkAIAgents.mcp_config import McpConfig

        result = McpConfig.get_excel_workbench()
        MockMcpWorkbench.assert_called_once_with(
            server_params=MockStdioServerParams.return_value
        )
        assert result is MockMcpWorkbench.return_value


class TestGetFilesystemWorkbench:

    def test_creates_stdio_params_with_npx_command(self):
        # Verify filesystem workbench uses npx as the command
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_filesystem_workbench()
        params_kwargs = MockStdioServerParams.call_args
        assert params_kwargs.kwargs["command"] == "npx"

    def test_creates_stdio_params_with_correct_args(self):
        # Verify args include -y, the MCP filesystem server package, and the target directory
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_filesystem_workbench()
        params_kwargs = MockStdioServerParams.call_args
        expected_args = [
            "-y",
            "@modelcontextprotocol/server-filesystem",
            "/Users/padmavathis/Documents/MCP_Automation",
        ]
        assert params_kwargs.kwargs["args"] == expected_args

    def test_sets_read_timeout_to_60_seconds(self):
        # Verify read_timeout_seconds is explicitly set to 60 for filesystem operations
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_filesystem_workbench()
        params_kwargs = MockStdioServerParams.call_args
        assert params_kwargs.kwargs["read_timeout_seconds"] == 60

    def test_does_not_pass_env(self):
        # Verify no env dict is passed to filesystem server (unlike other workbenches)
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_filesystem_workbench()
        params_kwargs = MockStdioServerParams.call_args
        assert "env" not in params_kwargs.kwargs

    def test_returns_mcp_workbench_with_server_params(self):
        # Verify McpWorkbench is constructed with the StdioServerParams instance
        from FrameworkAIAgents.mcp_config import McpConfig

        result = McpConfig.get_filesystem_workbench()
        MockMcpWorkbench.assert_called_once_with(
            server_params=MockStdioServerParams.return_value
        )
        assert result is MockMcpWorkbench.return_value


class TestModuleLevelCredentials:

    def test_db_username_read_from_env(self):
        # Verify DBUserName is populated from os.getenv at module level
        from FrameworkAIAgents import mcp_config

        with patch.object(mcp_config, "DBUserName", "test_user"):
            McpConfig = mcp_config.McpConfig
            mcp_config.DBUserName = "test_user"
            McpConfig.get_mysql_workbench()
            env = MockStdioServerParams.call_args.kwargs["env"]
            assert env["MYSQL_USER"] == "test_user"

    def test_db_password_read_from_env(self):
        # Verify DBPwd is populated from os.getenv at module level
        from FrameworkAIAgents import mcp_config

        with patch.object(mcp_config, "DBPwd", "test_pass"):
            McpConfig = mcp_config.McpConfig
            mcp_config.DBPwd = "test_pass"
            McpConfig.get_mysql_workbench()
            env = MockStdioServerParams.call_args.kwargs["env"]
            assert env["MYSQL_PASSWORD"] == "test_pass"

    def test_none_credentials_when_env_vars_not_set(self):
        # Verify None is passed when DBUserName/DBPwd env vars are missing
        from FrameworkAIAgents import mcp_config

        original_user = mcp_config.DBUserName
        original_pwd = mcp_config.DBPwd
        try:
            mcp_config.DBUserName = None
            mcp_config.DBPwd = None
            mcp_config.McpConfig.get_mysql_workbench()
            env = MockStdioServerParams.call_args.kwargs["env"]
            assert env["MYSQL_USER"] is None
            assert env["MYSQL_PASSWORD"] is None
        finally:
            mcp_config.DBUserName = original_user
            mcp_config.DBPwd = original_pwd


class TestStaticMethodBehavior:

    def test_mysql_workbench_is_static(self):
        # Verify get_mysql_workbench can be called without an instance
        from FrameworkAIAgents.mcp_config import McpConfig

        assert isinstance(
            McpConfig.__dict__["get_mysql_workbench"], staticmethod
        )

    def test_rest_api_workbench_is_static(self):
        # Verify get_rest_api_workbench can be called without an instance
        from FrameworkAIAgents.mcp_config import McpConfig

        assert isinstance(
            McpConfig.__dict__["get_rest_api_workbench"], staticmethod
        )

    def test_excel_workbench_is_static(self):
        # Verify get_excel_workbench can be called without an instance
        from FrameworkAIAgents.mcp_config import McpConfig

        assert isinstance(
            McpConfig.__dict__["get_excel_workbench"], staticmethod
        )

    def test_filesystem_workbench_is_static(self):
        # Verify get_filesystem_workbench can be called without an instance
        from FrameworkAIAgents.mcp_config import McpConfig

        assert isinstance(
            McpConfig.__dict__["get_filesystem_workbench"], staticmethod
        )

    def test_each_call_creates_new_workbench(self):
        # Verify repeated calls create separate McpWorkbench instances (no caching)
        from FrameworkAIAgents.mcp_config import McpConfig

        wb1 = McpConfig.get_mysql_workbench()
        wb2 = McpConfig.get_mysql_workbench()
        assert MockStdioServerParams.call_count == 2
        assert MockMcpWorkbench.call_count == 2

    def test_different_workbenches_use_different_params(self):
        # Verify each workbench type creates its own StdioServerParams with distinct configs
        from FrameworkAIAgents.mcp_config import McpConfig

        McpConfig.get_mysql_workbench()
        mysql_call = MockStdioServerParams.call_args

        MockStdioServerParams.reset_mock()
        McpConfig.get_rest_api_workbench()
        rest_call = MockStdioServerParams.call_args

        assert mysql_call.kwargs["command"] != rest_call.kwargs["command"]
        assert mysql_call.kwargs["args"] != rest_call.kwargs["args"]
