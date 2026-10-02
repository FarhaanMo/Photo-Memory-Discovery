import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def get_groq_api_key() -> Optional[str]:
    """Return GROQ_API_KEY from the environment or Streamlit secrets.

    Never logs or returns a usable empty string. Missing key is None.
    """
    env_key = os.environ.get("GROQ_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    try:
        import streamlit as st

        secret = st.secrets.get("GROQ_API_KEY")
    except Exception:
        return None

    if secret and str(secret).strip():
        return str(secret).strip()
    return None
