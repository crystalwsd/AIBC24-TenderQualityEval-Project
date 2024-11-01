from langchain.chains.query_constructor.base import AttributeInfo  
from langchain.retrievers.self_query.base import SelfQueryRetriever  
from langchain.retrievers.self_query.chroma import ChromaTranslator
from langchain_openai import ChatOpenAI
from helper_functions import valuelist as vl
#from langchain_chroma import Chroma
from langchain_chroma.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore


import(‘pysqlite3’)
import sys
sys.modules[‘sqlite3’] = sys.modules.pop(‘pysqlite3’)

embeddings_model = OpenAIEmbeddings(model=vl.EMBEDDING_MODEL)

def get_SelfQueryRetrieval(prompt, collectionname=vl.COLLECTIONNAME, max_tokens=2048, temperature=0):
    
    metadata_field_info = [  
        AttributeInfo(  
            name="doc_category",  
            description=f"type of document for tender evaluation. One of [{vl.doc_category.evalplan}, {vl.doc_category.proposal}, {vl.doc_category.evaljson}]",  
            type="string"
        ),  
        AttributeInfo(  
            name="doc_name",  
            description="name of document file",  
            type="string"
        ),  
        AttributeInfo(  
            name="tenderer",  
            description="the name of the tenderer company correspond to the tender proposal document",  
            type="string"
        )
    ]

    #get vectorstore from chroma DB
    vectordb = Chroma(collection_name=collectionname,
                        embedding_function=embeddings_model,
                        persist_directory=vl.VECTORDB)

    llm = ChatOpenAI(model=vl.OPENAI_MODEL,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    n=1                    
                    )
    
    document_content_description = "documents related to tender for evaluation"

    self_query_template = """
        You are an expert at formulating search queries and filters.

        Use the following format to apply filters:
        - If filtering by category, use `{"field": "value"}`
        - Combine filters using Python dictionaries, not logical operators like `and`.
        - If there are multiple filters, combine them in a dictionary like so: `{"field1": "value1", "field2": "value2"}`.

        Respond in this format:
        - Query: <the query>
        - Filter: <the filter in the correct format>
        """

    # Create a prompt for the self-query retriever
    self_query_prompt = PromptTemplate(
        input_variables=["query"], 
        template=self_query_template
    )

    retriever = SelfQueryRetriever.from_llm(
                                    llm,
                                    vectordb,
                                    document_content_description,
                                    metadata_field_info,
                                    verbose = True,
                                    prompt = self_query_prompt,
                                    structured_query_translator= ChromaTranslator()
                )

    response = retriever.invoke(prompt)
    return response

