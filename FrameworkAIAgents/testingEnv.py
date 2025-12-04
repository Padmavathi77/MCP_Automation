import os
from dotenv import load_dotenv

if __name__ =="__main__":
    load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
print(f"{OPENAI_API_KEY=}")

os.environ[
    "OPENAI_API_KEY"] = OPENAI_API_KEY

OPENAI_API_KEY = "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"

DBUserName="root"
DBPwd="root1234"