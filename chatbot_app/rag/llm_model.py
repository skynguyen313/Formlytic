from langchain_openai import ChatOpenAI
from django.conf import settings

def get_openai_llm(model_name: str = "gpt-4o-mini",
                   max_tokens=600,
                   temp=0.3):
    llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY,
                     model_name=model_name,
                     max_tokens=max_tokens,
                     temperature=temp,
                     max_retries=2)
    return llm