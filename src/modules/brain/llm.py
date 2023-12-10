
import httpx
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings

from src import settings

chat_model = ChatOpenAI(
    max_retries=1,
    http_client=settings.PROXY and httpx.Client(proxies=settings.PROXY)
)
embeddings = OpenAIEmbeddings(
    max_retries=1,
    http_client=settings.PROXY and httpx.Client(proxies=settings.PROXY)
)
