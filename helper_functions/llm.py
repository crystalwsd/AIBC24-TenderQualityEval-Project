import os
from dotenv import load_dotenv
from openai import OpenAI
from helper_functions import valuelist
import tiktoken

#---to overcome issue of streamlit cloud runtime error---#
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

#from litellm import embedding
from langchain_chroma import Chroma
#from langchain_chroma.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever


# Pass the API Key to the OpenAI Client
'''
client = OpenAI(
    api_key=valuelist.AMP_API_KEY,
    base_url=valuelist.AMP_URL,
    default_headers={"user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0"},
)
'''
client = OpenAI(api_key=valuelist.OPENAI_API_KEY)
embeddings_model = OpenAIEmbeddings(model=valuelist.EMBEDDING_MODEL)

def get_embedding(input, model=valuelist.EMBEDDING_MODEL):
    '''
    response = client.embeddings.create(
        input=input,
        model=f"openai/{model}",
        api_base = valuelist.AMP_URL
    )

    response = embedding(
        model=f"openai/{model}",
        input=input,
        api_key=valuelist.AMP_API_KEY,
        api_base=valuelist.AMP_URL
    )    
    '''
    response = client.embeddings.create(
        input=input,
        model=model
    )    

    return [x.embedding for x in response.data]

# This is the "Updated" helper function for calling LLM
def get_completion_from_messages(messages, prompt, model=valuelist.OPENAI_MODEL, temperature=0, top_p=1.0, max_tokens=1024, n=1, json_output=False):
    if json_output == True:
      output_json_structure = {"type": "json_object"}
    else:
      output_json_structure = None

    #messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create( #originally was openai.chat.completions
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=1,
        response_format=output_json_structure,
    )
    return response.choices[0].message.content

# This is the "Updated" helper function for calling LLM
def get_completion(prompt, model=valuelist.OPENAI_MODEL, temperature=0, top_p=1.0, max_tokens=1024, n=1, json_output=False):
    if json_output == True:
      output_json_structure = {"type": "json_object"}
    else:
      output_json_structure = None

    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create( #originally was openai.chat.completions
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=1,
        response_format=output_json_structure,
    )
    return response.choices[0].message.content


# This function is for calculating the tokens given the "message"
# ⚠️ This is simplified implementation that is good enough for a rough estimation

def count_tokens(text):
    #encoding = tiktoken.encoding_for_model('gpt-4o-mini')
    encoding = tiktoken.encoding_for_model(valuelist.OPENAI_MODEL)
    return len(encoding.encode(text))


def count_tokens_from_message(messages):
    #encoding = tiktoken.encoding_for_model('gpt-4o-mini')
    encoding = tiktoken.encoding_for_model(valuelist.OPENAI_MODEL)
    value = ' '.join([x.get('content') for x in messages])
    return len(encoding.encode(value))


def get_RAGChainResponse(prompt, context="", retriever="", collectionname=valuelist.COLLECTIONNAME, max_tokens=3000, temperature=0):
    try:

        template = """
            Use the following pieces of context if any, as well as the context given in question to answer the question at the end.
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            context: {context}
            Question: {question}
            Answer:"""


        QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

        llm = ChatOpenAI(model=valuelist.OPENAI_MODEL,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        n=1                    
                        )
                        #top_p=1,
        if retriever=="":
            #get vectorstore from chroma DB
            vectordb = Chroma(collection_name=collectionname,
                                embedding_function=embeddings_model,
                                persist_directory=valuelist.VECTORDB)
            
            retriever = vectordb.as_retriever(k=10)
            #retriever = vectordb.as_retriever(k=6, search_type="similarity_score_threshold",
            #                                  search_kwargs={"score_threshold":0.2})

        # Run chain
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=retriever,
            return_source_documents=False, # Make inspection of document possible
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
        )
    
        response = qa_chain.invoke(prompt)
        
    except Exception as e:
       print(f"Error in get_RAGChainResponse for prompt [ {prompt} ] : {e}")

    return response


def get_MultiQueryRetrieval(prompt, context="", collectionname=valuelist.COLLECTIONNAME, max_tokens=1024, temperature=0):
    try:
        #get vectorstore from chroma DB
        vectordb = Chroma(collection_name=collectionname,
                            embedding_function=embeddings_model,
                            persist_directory=valuelist.VECTORDB)

        llm = ChatOpenAI(model=valuelist.OPENAI_MODEL,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        n=1                    
                        )
        
        retriever_multiquery = MultiQueryRetriever.from_llm(
                                retriever=vectordb.as_retriever(), llm=llm,
                                )
        
        qa_chain_multiquery= RetrievalQA.from_llm(
                            retriever=retriever_multiquery, llm=llm,
                            return_source_documents=True
                            )
        
        response = qa_chain_multiquery.invoke(prompt)
    except Exception as e:
       print(f"Error in get_MultiQueryRetrieval for prompt [ {prompt} ] : {e}")

    return response

def get_SimilaritySearch(prompt, doc_category=valuelist.doc_category.evalplan, collectionname=valuelist.COLLECTIONNAME):
        #get vectorstore from chroma DB
        vectordb = Chroma(collection_name=collectionname,
                            embedding_function=embeddings_model,
                            persist_directory=valuelist.VECTORDB)
        
        #results = vectordb.similarity_search_with_score(prompt, k=1, filter={"doc_name":"ABCCo Proposal(strong).docx"})
        #results = vectordb.similarity_search_with_score(prompt, k=6, filter={"doc_category":doc_category})
        #results = vectordb.similarity_search_with_relevance_scores(prompt, k=10)
        results = vectordb.similarity_search(prompt, k=10)
        '''
        for res, score in results:
            print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]")
        '''
        return results