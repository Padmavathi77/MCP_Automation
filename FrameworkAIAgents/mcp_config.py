from autogen_ext.tools.mcp import StdioServerParams, McpWorkbench
import os
from dotenv import load_dotenv
if __name__ =="__main__":
    load_dotenv()

DBUserName = os.getenv('DBUserName')
DBPwd = os.getenv('DBPwd')
class McpConfig:

    @staticmethod
    def get_mysql_workbench():
        mysql_server_params = StdioServerParams(
            command="/Library/Frameworks/Python.framework/Versions/3.13/bin/uv",
            args=[
                "--directory",
                "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages",
                "run",
                "mysql_mcp_server"
                ],
            env={
                "MYSQL_HOST": "localhost",
                "MYSQL_PORT": "3306",
                "MYSQL_USER": DBUserName,
                "MYSQL_PASSWORD": DBPwd,
                "MYSQL_DATABASE": "rahulshettyacademy"
                }
            )
        return McpWorkbench(server_params=mysql_server_params)

    @staticmethod
    def get_rest_api_workbench():
        rest_api_server_params = StdioServerParams(
            command="npx",
            args=[
                "-y",
                "dkmaker-mcp-rest-api"
            ],
            env={
                "REST_BASE_URL": "https://rahulshettyacademy.com",
                "HEADER_Accept": "application/json"
            })
        return McpWorkbench(server_params=rest_api_server_params)

    @staticmethod
    def get_excel_workbench():
        excel_server_params = StdioServerParams(
            command = "npx",
            args = ["--yes", "@negokaz/excel-mcp-server"],
            env = {
            "EXCEL_MCP_PAGING_CELLS_LIMIT": "4000"
        })
        return McpWorkbench(server_params=excel_server_params)

    @staticmethod
    def get_filesystem_workbench():
        filesystem_server_params = StdioServerParams(
            command = "npx",
            args = [
            "-y",
            "@modelcontextprotocol/server-filesystem",
            "/Users/padmavathis/Documents/MCP_Automation"],
            read_timeout_seconds=60)
        return McpWorkbench(server_params=filesystem_server_params)

