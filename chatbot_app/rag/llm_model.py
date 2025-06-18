from langchain_openai import ChatOpenAI
from django.conf import settings

api_key = "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"

def get_openai_llm(model_name: str = "gpt-4o",
                   max_tokens=512,
                   temp=0.2):
    llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY,
                     model_name=model_name,
                     max_tokens=max_tokens,
                     temperature=temp,
                     max_retries=2)
    return llm