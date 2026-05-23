from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    jira_base_url: str | None = os.getenv("JIRA_BASE_URL")
    jira_email: str | None = os.getenv("JIRA_EMAIL")
    jira_api_token: str | None = os.getenv("JIRA_API_TOKEN")
    jira_project_key: str = os.getenv("JIRA_PROJECT_KEY", "PMI")
    jira_issue_type: str = os.getenv("JIRA_ISSUE_TYPE", "Task")

settings = Settings()
