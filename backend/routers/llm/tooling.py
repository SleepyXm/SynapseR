#from langchain.vectorstores import Chroma
#from langchain.embeddings.openai import OpenAIEmbeddings
#from langchain.chat_models import ChatOpenAI
#from langchain.chains import RetrievalQA
from search import get_top_paragraphs, should_search
from typing import List
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import PyPDF2


class VectorDB:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.index = {}

    def add_document(self, text, metadata=None):
        embedding = self.embedding_model.embed(text)
        self.index[text] = {"embedding": embedding, "metadata": metadata}

    def query(self, query_text, top_k=3):
        query_embedding = self.embedding_model.embed(query_text)
        return self._nearest_neighbors(query_embedding, top_k)

class RAGPipeline:
    def __init__(self, vector_db, llm):
        self.vector_db = vector_db
        self.llm = llm

    def answer_query(self, query):
        relevant_docs = self.vector_db.query(query)
        context = "\n".join([doc for doc, _ in relevant_docs])
        prompt = f"Context: {context}\n\nQuestion: {query}\nAnswer:"
        response = self.llm.generate(prompt)
        return response
    

class LLMTool:
    name = None
    trigger = None  # function that returns bool

    async def run(self, user_input: str):
        raise NotImplementedError
    
class SearchTool(LLMTool):
    name = "search"
    trigger = staticmethod(should_search)

    async def run(self, user_input: str):
        paragraphs = get_top_paragraphs(user_input)
        if isinstance(paragraphs, list):
            return "\n\n".join(paragraphs)
        return paragraphs

class LLMTooling:
    def __init__(self):
        # automatically find subclasses of LLMTool
        self.tools = {t.name: t() for t in LLMTool.__subclasses__()}

    async def handle_input(self, user_input: str):
        for tool in self.tools.values():
            if tool.trigger and tool.trigger(user_input):
                return await tool.run(user_input)
        return None
    


#embeddings_model = OpenAIEmbeddings()

#def read_pdf(file):
#    reader = PyPDF2.PdfReader(file)
#    text = ""
#    for page in reader.pages:
#        text += page.extract_text() + "\n"
#    return text

#def chunk_and_embed(text, chunk_size=500, chunk_overlap=50):
#    splitter = RecursiveCharacterTextSplitter(
#        chunk_size=chunk_size,
#        chunk_overlap=chunk_overlap
#    )
#    chunks = splitter.split_text(text)
#    return [(chunk, embeddings_model.embed(chunk)) for chunk in chunks]