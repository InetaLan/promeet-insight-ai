from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

def get_secret(name: str, default=None):
    try:
        import streamlit as st
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)

@dataclass
class Settings:
    openai_api_key: str | None = get_secret("OPENAI_API_KEY")
    openai_model: str = get_secret("OPENAI_MODEL", "gpt-4o")
    jira_base_url: str | None = get_secret("JIRA_BASE_URL")
    jira_email: str | None = get_secret("JIRA_EMAIL")
    jira_api_token: str | None = get_secret("JIRA_API_TOKEN")
    jira_project_key: str = get_secret("JIRA_PROJECT_KEY", "PMI")
    jira_issue_type: str = get_secret("JIRA_ISSUE_TYPE", "Task")

settings = Settings()