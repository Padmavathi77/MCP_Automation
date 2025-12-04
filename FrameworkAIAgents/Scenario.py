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

os.environ[
    "OPENAI_API_KEY"] = "sk-proj-_u_z3oDYUuXp898y_tYf4emQk0C32BfgQ4my-fOc4eGK8dEI-8KzHIYwd_EGIfE_0nBCUWlDOrT3BlbkFJyVLa_W64BtAqiJJFVi0uVTOtNW4YCZWL6oIgZWcYQ2h0OPei6lYFc69F6I38uZPIlz8eYT0bg"


async def main():
    model_client = OpenAIChatCompletionClient(model="gpt-4o")
    factory = agentFactory(model_client)
    database_agent = factory.create_database_agent(system_message=("""
            You are a database specialist responsible for retrieving user registration date.
            your task:
            1. connect to mysql data base 'rahulshettyacademy'           
            2. Query the 'RegistrationDetails' table to get a random record 
            3. Query the 'Usernames' table to get additional user data
            4. Remove "-" from Phone number and use the changed phone number for registration
            5. Combine the data from both tables to create complete registration information
            6. Ensure the email is unique by adding a timestamp or random number if needed
            7. Prepare all the registration data in a structured format so that another agent can understand
            When ready, write: "DATABASE_DATA_READY - APIAgent should proceed next"
            """))
    api_agent = factory.create_api_agent(system_message=("""
            You are an API testing specialist with access to both REST API tools and filesystem.
            Your task:
            1. FIRST: Extract the EXACT registration data from DatabaseAgent's REGISTRATION_DATA message
            2. Read the Postman collection to understand the API contract
            3. Before making a registration API call- construct its body field with the DatabaseAgent's data inline with below format rules:
                Email should be unique. add timestamp/random data
                Update Password to this format - SecurePass123
                Mobile number format - 1234567890
                once json body field is constructed as per above, then make registration API call with constructed body field
            4. If registration succeeds OR fails with "user already exists", proceed with login
            5. Make login API call with userEmail and userPassword from database data
            6. Report the actual API response status and success/failure
            7. use the following URI for registration https://rahulshettyacademy.com/api/ecom/auth/register and header parameter Content-Type: application/json, "Accept": "*/*",
            CRITICAL: You MUST use the exact data from DatabaseAgent's REGISTRATION_DATA, not the sample data from postman collection

            When BOTH registration attempt and login attempt are complete, write: "API_TESTING_COMPLETE - ExcelAgent should proceed next"
            Include the final login status (success/failure) in your response.
            """))
    excel_agent = factory.create_excel_agent(system_message=("""
            You are an Excel data management specialist. ONLY proceed when APIAgent has completed testing.
            Your task:
            1. Wait for APIAgent to complete with "API_TESTING_COMPLETE" message
            2. Extract the registration data from DatabaseAgent's REGISTRATION_DATA message
            3. Check APIAgent's response for actual login success/failure status
            4. Only save data if login was actually successful
            5. Open /Users/padmavathis/Documents/MCP_Automation/newdata.xlsx
            6. Add registration data to RegistrationData sheet in newdata.xlsx, header and then data in the next row 
            7. Save and verify the data

            CRITICAL: Only save data if APIAgent reports successful login, not just attempted login.

            when complete, write: "REGISTRATION PROCESS COMPLETE" and stop.
            """))

    team = RoundRobinGroupChat(participants=[database_agent, api_agent, excel_agent],
                               termination_condition=TextMentionTermination("REGISTRATION PROCESS COMPLETE")
                               )

    task_result = await Console(team.run_stream(task="Execute Sequential User Registration Process:\n\n"
                                                     "STEP 1 - DatabaseAgent (FIRST) :\n"
                                                     "Get Random registration data from database tables and format it clearly.\n\n"

                                                     "STEP 2 - APIAgent: \n"
                                                     "Read Postman collection files, then make registration followed by login APIs using the database data.\n\n"

                                                     "STEP 3 - ExcelAgent: \n"
                                                     "Save successful registration login details to Excel file. \n\n"

                                                     "Each agent should complete their work fully before the next agent begins. "
                                                     "Pass data.clearly between agents using the specified formats"))


asyncio.run(main())