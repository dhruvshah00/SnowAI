from langchain_openai import AzureChatOpenAI
from dotenv import dotenv_values
from langchain_community.utilities import SQLDatabase
import os


def get_llm_azure(model_temperature = 0.0, max_tokens=256):
    cfg = dotenv_values()

    deployment_name = cfg['AZURE_OPENAI_MODEL']
    azure_endpoint = cfg['AZURE_OPENAI_ENDPOINT']
    api_version = cfg['AZURE_OPENAI_API_VERSION']

    # Create LLM via Azure OpenAI Service
    return AzureChatOpenAI(azure_endpoint=azure_endpoint,deployment_name=deployment_name, temperature=model_temperature, openai_api_version=api_version, openai_api_type="azure")


def get_db():
    db = SQLDatabase.from_uri(
        f'snowflake://{os.environ.get("SNOWFLAKE_USER")}:{os.environ.get("SNOWFLAKE_PASSWORD")}@{os.environ.get("SNOWFLAKE_ACCOUNT")}/{os.environ.get("SNOWFLAKE_DATABASE")}/{os.environ.get("SNOWFLAKE_SCHEMA")}?warehouse={os.environ.get("SNOWFLAKE_WAREHOUSE")}&role={os.environ.get("SNOWFLAKE_ROLE")}',
        view_support=True
    )

    return db
