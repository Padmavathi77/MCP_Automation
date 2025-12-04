# MCP_Automation

Building multi-agent workflows using AutoGen Framework by Microsoft
MCP - https://modelcontextprotocol.io/docs/getting-started/intro
MCP servers are programs that expose specific capabilities to AI applications through standardized protocol interfaces.
MCP clients are instantiated by host applications to communicate with particular MCP servers. The host application, like Claude.ai or an IDE, manages the overall user experience and coordinates multiple clients.
Agentic AI - refers to AI systems that can automatically take actions and make decisions to achieve goals rather than just responding to prompts.
Python MCP SDK 1.2.0 or higher
LLM+Tools(via MCP)+ decision autonomy = AI Agent
Multiple AI agents + coordination = Multi Agent System
Multi Agent System + goal oriented design = Agentic AI
https://microsoft.github.io/autogen/stable//index.html

setup:
1. while creating the project, create virtual env, so that all tools can be installed in the virtual env 
In Terminal: 
2. pip3 install -U "autogen-agentchat"
3. pip3 install "autogen-ext[openai]"
4. pip3 install -U "autogen-ext[mcp]"
OPENAI_API_KEY - get your own OPENAI_API_KEY


Scenario-Connect to the database and retrieve necessary information from multiple tables.
Read API contract files to understand the required structure for API calls.
Use the data fetched from the database to construct a Registration API POST call.
Validate the data submission by triggering a Login API GET call.
Finally, store the successfully registered user data into an Excel sheet.

Execution plan -
• Database Agent
A dedicated agent capable of connecting to any database and retrieving data from multiple tables. This agent is responsible for structuring the gathered data and passing it to the downstream agents.
• API + File System Agent
This agent reads API contract definitions from the local file system and prepares itself to make API calls based on the specifications. It consumes the structured data provided by the Database Agent to perform the Registration POST and Login GET calls.
• Excel Agent
Responsible for writing the final, successfully registered user data into an Excel tracker.