import os
from dotenv import load_dotenv
from collections import namedtuple
import streamlit as st

if load_dotenv('.env'):

    '''
    AMP_API_KEY = os.getenv("AMP_API_KEY")
    AMP_MODEL_NAME=os.getenv("AMP_MODEL_NAME")
    AMP_URL=os.getenv("AMP_URL")
    '''
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL=os.getenv("OPENAI_MODEL_NAME")
else:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    OPENAI_MODEL= st.secrets["OPENAI_MODEL_NAME"]

#EMBEDDING_MODEL='text-embedding-3-small-prd-gcc2-lb'
EMBEDDING_MODEL='text-embedding-3-small'
VECTORDB=os.path.join("data","chroma_langchain_db")
COLLECTIONNAME="tender_eval_documents"
COLLECTIONNAME_RESULT="tender_proposal_eval_results"
PARENTSTORENAME="parentdoc_store"
READMODE="r"
WRITEMODE="w"

# Define a named tuple
DocCategory = namedtuple('DocCategory', ['evalplan', 'proposal', 'evaljson'])

# Create an instance of the named tuple
doc_category = DocCategory(evalplan="Evaluation Plan", proposal="Tender Proposal", evaljson="JSON format evaluation plan")

#file name path of file list stored in vector db
METADATAFILEPATH = os.path.join("data", "docmetadata.txt")
METADATACOLUMNS = ['doc_id', 'doc_name','doc_category']
METADATA_SESSIONNAME = "DOC_METADATA"

#session specific variable names
LASTPROPOSALOPTION = "Last Proposal Option"
LASTCHATCONTEXT = "Last Chat Context"

#file names of JSON working file
EVALJSONFILENAME = os.path.join("data","evalcriteria.json")
EVALJSON_SESSIONNAME = "EvalCriteria"

EVALRESULT_SESSIONNAME="Eval_result"

#for shortlisted proposal
RESULTCONTENT_SESSIONNAME="Shortlisted proposal content"

#image folder location
IMAGELOCATION=".\images"