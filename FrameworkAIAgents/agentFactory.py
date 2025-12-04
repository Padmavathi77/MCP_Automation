from autogen_agentchat.agents import AssistantAgent
from FrameworkAIAgents.mcp_config import McpConfig


class agentFactory :
    def __init__(self, model_client):
        self.model_client=model_client
        self.mcp_config = McpConfig()

    def create_database_agent(self, system_message):
        DBAgent = AssistantAgent(name="DataBaseAgent",
                                 model_client=self.model_client,
                                 workbench=self.mcp_config.get_mysql_workbench(),
                                 system_message=system_message)

        return DBAgent;

    def create_api_agent(self,system_message):
        api_agent = AssistantAgent(name="APIAgent",
                                 model_client=self.model_client,
                                 workbench=[self.mcp_config.get_rest_api_workbench(),
                                            self.mcp_config.get_filesystem_workbench()],
                                 system_message=system_message)
        return api_agent;

    def create_excel_agent(self,system_message=None):
        excel_agent = AssistantAgent(name="ExcelAgent",
                                   model_client=self.model_client,
                                   workbench=self.mcp_config.get_excel_workbench(),
                                   system_message=system_message)
        return excel_agent;



