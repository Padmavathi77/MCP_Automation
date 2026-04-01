# creating a flow where DBagent will retrieve data from sql DB,
# APIAgent will use the data to register and login
# excel (filesystem) agent write data to Excel sheet

import asyncio
import os

from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from FrameworkAIAgents.agentFactory import agentFactory

from dotenv import load_dotenv


def setup_env():
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    os.environ["OPENAI_API_KEY"] = api_key
    return api_key


DB_SYSTEM_MESSAGE = (
    "You are a database specialist responsible for retrieving user registration date.\n"
    "your task:\n"
    "1. connect to mysql data base 'rahulshettyacademy'\n"
    "2. Query the 'RegistrationDetails' table to get a random record\n"
    "3. Query the 'Usernames' table to get additional user data\n"
    "4. Remove \"-\" from Phone number and use the changed phone number for registration\n"
    "5. Combine the data from both tables to create complete registration information\n"
    "6. Ensure the email is unique by adding a timestamp or random number if needed\n"
    "7. Prepare all the registration data in a structured format so that another agent can understand\n"
    'When ready, write: "DATABASE_DATA_READY - APIAgent should proceed next"'
)

API_SYSTEM_MESSAGE = (
    "You are an API testing specialist with access to both REST API tools and filesystem.\n"
    "Your task:\n"
    "1. FIRST: Extract the EXACT registration data from DatabaseAgent's REGISTRATION_DATA message\n"
    "2. Read the Postman collection to understand the API contract\n"
    "3. Before making a registration API call- construct its body field with the DatabaseAgent's data inline with below format rules:\n"
    "    Email should be unique. add timestamp/random data\n"
    "    Update Password to this format - SecurePass123\n"
    "    Mobile number format - 1234567890\n"
    "    once json body field is constructed as per above, then make registration API call with constructed body field\n"
    "4. If registration succeeds OR fails with \"user already exists\", proceed with login\n"
    "5. Make login API call with userEmail and userPassword from database data\n"
    "6. Report the actual API response status and success/failure\n"
    "7. use the following URI for registration https://rahulshettyacademy.com/api/ecom/auth/register "
    'and header parameter Content-Type: application/json, "Accept": "*/*",\n'
    "CRITICAL: You MUST use the exact data from DatabaseAgent's REGISTRATION_DATA, not the sample data from postman collection\n\n"
    'When BOTH registration attempt and login attempt are complete, write: "API_TESTING_COMPLETE - ExcelAgent should proceed next"\n'
    "Include the final login status (success/failure) in your response."
)

EXCEL_SYSTEM_MESSAGE = (
    "You are an Excel data management specialist. ONLY proceed when APIAgent has completed testing.\n"
    "Your task:\n"
    '1. Wait for APIAgent to complete with "API_TESTING_COMPLETE" message\n'
    "2. Extract the registration data from DatabaseAgent's REGISTRATION_DATA message\n"
    "3. Check APIAgent's response for actual login success/failure status\n"
    "4. Only save data if login was actually successful\n"
    "5. Open /Users/padmavathis/Documents/MCP_Automation/newdata.xlsx\n"
    "6. Add registration data to RegistrationData sheet in newdata.xlsx, header and then data in the next row\n"
    "7. Save and verify the data\n\n"
    "CRITICAL: Only save data if APIAgent reports successful login, not just attempted login.\n\n"
    'when complete, write: "REGISTRATION PROCESS COMPLETE" and stop.'
)

TASK_DESCRIPTION = (
    "Execute Sequential User Registration Process:\n\n"
    "STEP 1 - DatabaseAgent (FIRST) :\n"
    "Get Random registration data from database tables and format it clearly.\n\n"
    "STEP 2 - APIAgent: \n"
    "Read Postman collection files, then make registration followed by login APIs using the database data.\n\n"
    "STEP 3 - ExcelAgent: \n"
    "Save successful registration login details to Excel file. \n\n"
    "Each agent should complete their work fully before the next agent begins. "
    "Pass data.clearly between agents using the specified formats"
)


async def main():
    model_client = OpenAIChatCompletionClient(model="gpt-4o")
    factory = agentFactory(model_client)
    database_agent = factory.create_database_agent(system_message=DB_SYSTEM_MESSAGE)
    api_agent = factory.create_api_agent(system_message=API_SYSTEM_MESSAGE)
    excel_agent = factory.create_excel_agent(system_message=EXCEL_SYSTEM_MESSAGE)

    team = RoundRobinGroupChat(
        participants=[database_agent, api_agent, excel_agent],
        termination_condition=TextMentionTermination("REGISTRATION PROCESS COMPLETE"),
    )

    task_result = await Console(
        team.run_stream(task=TASK_DESCRIPTION)
    )
    return task_result


if __name__ == "__main__":
    setup_env()
    asyncio.run(main())
