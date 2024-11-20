import pandas as pd
import os
from helper_functions import valuelist as vl
from helper_functions import llm
from helper_functions import utility as ut
#from logics import query_handler as qh
from langchain_core.documents import Document 
from langchain.text_splitter import RecursiveCharacterTextSplitter
#-- added to overcome issue on Streamlit cloud---#
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from langchain_chroma import Chroma
#from langchain_chroma.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import JSONLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import PyMuPDFLoader
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.storage._lc_store import create_kv_docstore
import docx2txt
import json
from uuid import uuid4
import streamlit as st



embeddings_model = OpenAIEmbeddings(model=vl.EMBEDDING_MODEL)

def LoadFile(filepath, filecategory=vl.doc_category.proposal):
    try:
        # try to load the document
        
        filename = os.path.basename(filepath)
      
        filetype = os.path.splitext(filename)[1]
        if filetype == ".docx":
            loader = Docx2txtLoader(filepath)
        elif filetype == ".pdf":
            loader = PyMuPDFLoader(filepath)
        elif filetype == ".json":
            loader = JSONLoader(filepath, text_content=False, jq_schema=".Category")
        else :
            #assume to be plain text
            loader = TextLoader(filepath)
        
        # load() returns a list of Document objects
        data = loader.load()
        # Add metadata to each Document object
        docObjs = []
        for doc in data:
            doc.metadata["doc_category"] = filecategory
            doc.metadata["doc_name"] = filename
            docObjs.append(doc)


        return docObjs

    except Exception as e:
        # if there is an error loading the document, print the error and continue to the next document
        print(f"Error loading {filepath}: {e}")

def get_Splitter(chunksize=500, chunkoverlap=80):

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=chunksize,
        chunk_overlap=chunkoverlap,
        length_function=llm.count_tokens
    )
    #splitted_documents = text_splitter.split_documents(docObjs)

    return text_splitter


def get_ParentChildDocRetriever(filecategory, mode):
    try:
       
        if filecategory==vl.doc_category.evalplan:
            parent_splitter = get_Splitter(chunksize=1000, chunkoverlap=80)
            child_splitter = get_Splitter(chunksize=300, chunkoverlap=30)
        else :
            if filecategory == vl.doc_category.proposal:
                parent_splitter = get_Splitter(chunksize=600, chunkoverlap=40)
                child_splitter = get_Splitter(chunksize=200, chunkoverlap=30)
            else:
                print(f"Invalid file type : {filecategory}")


        vectordb = Chroma(
                        collection_name=vl.COLLECTIONNAME,
                        embedding_function=embeddings_model,
                        persist_directory=vl.VECTORDB,  # Where to save data locally, remove if not neccesary
                    )

        # The storage layer for the parent documents
        fs = open(os.path.join("data", vl.PARENTSTORENAME), mode)
        #store = InMemoryStore()
        store = create_kv_docstore(fs)
        # Specificy a Retriever
        retriever = ParentDocumentRetriever(
            vectorstore=vectordb,
            docstore=store,
            child_splitter=child_splitter,
            parent_splitter=parent_splitter,
            child_metadata_fields=["doc_name","doc_category"],
            search_kwargs={'k': 5}
        )
    except Exception as e:
        # if there is an error loading the document, print the error and continue to the next document
        print(f"Error in get_ParentChildDocRetriever for file category {filecategory}: {e}")

    return retriever

def put_DocToStore(retriever, filelist, filecategory):
    #filesstored = 0
    list_of_documents_loaded = []
    #ids = []
    

    try:
        for filename in filelist:
            filepath = os.path.join("data", filename)
            docObjs = LoadFile(filepath, filecategory)
            list_of_documents_loaded.extend(docObjs)
        # The splitting & embeddings happen
        retriever.add_documents(list_of_documents_loaded)


    except Exception as e:
        # if there is an error loading the document, print the error and continue to the next document
        print(f"Error in put_DocToStore for file category {filecategory}: {e}")

    return len(list_of_documents_loaded)

def get_CollectionInfo(collectionname):
    vectordb = Chroma(
                collection_name=collectionname,
                embedding_function=embeddings_model,
                persist_directory=vl.VECTORDB  # Where to save data locally, remove if not neccesary
            )
    collection_docs = vectordb.get()

    return collection_docs


def get_AllFilesInCollection(collectionname=vl.COLLECTIONNAME):
    all_docs = get_CollectionInfo(collectionname)
    file_names = [mdata.get('doc_name') for mdata in all_docs['metadatas']]
    unique_filelist = list(dict.fromkeys(file_names))
    return unique_filelist

def StoreFiles(docObjs, filecategory, collectionname=vl.COLLECTIONNAME):
    #filesstored = 0
    
    try:       
        splitted_docs=[]

        if filecategory==vl.doc_category.evalplan:
            splitter = get_Splitter(chunksize=1000, chunkoverlap=100)
        elif filecategory == vl.doc_category.proposal:
            splitter = get_Splitter(chunksize=200, chunkoverlap=30)
            #splitted_docs = SplitStoreEvalPlanFile(list_of_documents_loaded)
        elif filecategory == vl.doc_category.evaljson:
            splitter = get_Splitter(chunksize=600, chunkoverlap=50)
        else:
            print(f"Invalid file type : {filecategory}")

        splitted_docs = splitter.split_documents(docObjs)

        # Generate a list of unique identifiers (UUIDs)
        uuids = [str(uuid4()) for _ in range(len(splitted_docs))]

        vector_store = Chroma.from_documents(
            collection_name=collectionname,
            documents=splitted_docs,
            ids=uuids,
            embedding=embeddings_model,
            persist_directory=vl.VECTORDB,  # Where to save data locally, remove if not neccesary
        )

        #print(splitted_docs[0])

    except Exception as e:
        # if there is an error loading the document, print the error and continue to the next document
        print(f"Error in StoreFiles for file category {filecategory}: {e}")

    return uuids


def UploadEvalFile(filehandle):
    toload = True
    try:
        if filehandle is not None:
            #check if already exist and prompt user
            if len(st.session_state[vl.METADATA_SESSIONNAME]) > 0:
                existingfile = st.session_state[vl.METADATA_SESSIONNAME]
                if filehandle.name in existingfile['doc_name'].values:
                    st.warning(f"file [{filehandle.name}] already exist.\
                            To replace file, please purge all files and re-upload.", icon="🚨")
                    toload = False
            if toload:
                localfilepath = os.path.join("data",filehandle.name)                   
                with open(localfilepath, "wb") as f:
                    f.write(filehandle.getbuffer())

                docObjs = LoadFile(localfilepath, vl.doc_category.evalplan)
                #store into vectorDB
                #localfilepath = os.path.join("data",filehandle.name)
                #Below codes are for Parent-Child Doc Retrieval- KIV
                '''
                with open(localfilepath, "wb") as f:
                    f.write(filehandle.getbuffer())        
                retriever = get_ParentChildDocRetriever(vl.doc_category.evalplan, vl.WRITEMODE)
                retriever.add_documents(docObjs)
                #st.session_state[vl.METADATA_SESSIONNAME].append(filehandle.name)
                idlist = list(retriever.docstore.yield_keys())
                '''
                idlist = StoreFiles(docObjs, vl.doc_category.evalplan)
                #Update reload meta data file and list
                put_MetadataStore(docObjs, idlist)
                get_MetadataStoreToSession()
                if os.path.exists(vl.EVALJSONFILENAME):
                    #clear in session and file content for JSON eval file
                    os.remove(vl.EVALJSONFILENAME)
                    st.session_state[vl.EVALJSON_SESSIONNAME] = {}
                st.success('Done')
    except Exception as e:
        print(f"Error in UploadEvalFile for file : {filehandle.name}: {e}")


def put_MetadataStore(docObjs, idlist):
    try:
        
        #Save to add file meta data into JSON file
        #idlist = list(store.yield_keys())
        idcnt = 0
        fileexist = os.path.exists(vl.METADATAFILEPATH)
        with open(vl.METADATAFILEPATH, 'a') as f:
            if not fileexist:
                f.write(f"id,doc_name,doc_category\n")
                st.session_state[vl.METADATA_SESSIONNAME] = {
                    'id':[],
                    'doc_name':[],
                    'doc_category':[]
                }
            for doc in docObjs:
                doc_name = doc.metadata.get('doc_name')  # Get 'doc_name' from metadata
                doc_category = doc.metadata.get('doc_category')
                if doc_name and doc_category:  # Ensure doc_name exists
                    f.write(f"{idlist[idcnt]},{doc_name},{doc_category}\n")
                    #add row into the metadata session dictionary
                    st.session_state[vl.METADATA_SESSIONNAME]['id'].append(idlist[idcnt])
                    st.session_state[vl.METADATA_SESSIONNAME]['doc_name'].append(doc_name)
                    st.session_state[vl.METADATA_SESSIONNAME]['doc_category'].append(doc_category)
                    #newrow = [idlist[idcnt],doc_name,doc_category]
                    #st.session_state[vl.METADATA_SESSIONNAME].concat([st.session_state[vl.METADATA_SESSIONNAME], newrow], ignore_index=True)
                    #st.session_state[vl.METADATA_SESSIONNAME].loc[len(st.session_state[vl.METADATA_SESSIONNAME].index)] = newrow
                    idcnt += 1

    except Exception as e:
        print(f"Error in put_MetadataStore : {e}")
    
def get_MetadataStoreToSession():
    
    if os.path.exists(vl.METADATAFILEPATH):
        meta_df = pd.read_csv(vl.METADATAFILEPATH)
    else:
        meta_df = pd.DataFrame(columns=vl.METADATACOLUMNS)

    st.session_state[vl.METADATA_SESSIONNAME]= meta_df

def UploadProposalFile(filehandle):
    list_of_documents_loaded=[]
    #toload = True
    try:
        st.session_state['selected_tab'] = 'tab_proposal'
        if filehandle is not None:
            for upfile in filehandle:
                #check if already exist and prompt user
                if len(st.session_state[vl.METADATA_SESSIONNAME]) > 0:
                    existingfile = st.session_state[vl.METADATA_SESSIONNAME]                   
                    if upfile.name in existingfile['doc_name'].values:
                        st.warning(f"file [{upfile.name}] already exist. Unable to upload", icon="🚨")
                        continue

                localfilepath = os.path.join("data",upfile.name)                   
                with open(localfilepath, "wb") as f:
                    f.write(upfile.getbuffer())

                docObjs = LoadFile(localfilepath, vl.doc_category.proposal)
                list_of_documents_loaded.extend(docObjs)

            #store into vectorDB
            #Below codes are for Parent-Child Doc Retrieval- KIV
            
            #retriever = get_ParentChildDocRetriever(vl.doc_category.proposal, vl.WRITEMODE)
            #retriever.add_documents(list_of_documents_loaded)
            #idlist = list(retriever.docstore.yield_keys())
            
            if len(list_of_documents_loaded) > 0:
                idlist = StoreFiles(list_of_documents_loaded, vl.doc_category.proposal)
                put_MetadataStore(list_of_documents_loaded, idlist)
                get_MetadataStoreToSession()
                st.success('Proposal files successfully uploaded')
    except Exception as e:
        print(f"Error in UploadEvalFile for file : {filehandle.name}: {e}")


def Purge_Collection(collectionname):

    existingfile = st.session_state[vl.METADATA_SESSIONNAME]
    for dfile in existingfile['doc_name'].values:
        filetoremove = os.path.join("data", dfile)
        if os.path.exists(filetoremove):
            os.remove(os.path.join("data", dfile))

    vectordb = Chroma(
                collection_name=collectionname,
                embedding_function=embeddings_model,
                persist_directory=vl.VECTORDB,  # Where to save data locally, remove if not neccesary
            )
    vectordb.delete_collection()

    #also purge the shortlisting collection
    resultfiles = get_AllFilesInCollection(vl.COLLECTIONNAME_RESULT)
    for dfile in resultfiles:
        filetoremove = os.path.join("data", dfile)
        if os.path.exists(filetoremove):
            os.remove(os.path.join("data", dfile))

    vectordb1 = Chroma(
                collection_name=vl.COLLECTIONNAME_RESULT,
                embedding_function=embeddings_model,
                persist_directory=vl.VECTORDB,  # Where to save data locally, remove if not neccesary
            )
    vectordb1.delete_collection()

    #Clear session state and respective work files
    if os.path.exists(vl.METADATAFILEPATH):
        os.remove(vl.METADATAFILEPATH)
        st.session_state[vl.METADATA_SESSIONNAME]={}

    if os.path.exists(vl.EVALJSONFILENAME):
        os.remove(vl.EVALJSONFILENAME)
        st.session_state[vl.EVALJSON_SESSIONNAME]={}

    return True


# Recursive function to loop through nested JSON structure and find 'Area of Assessment','Weightage'
def Find_ContentInDictionary(data, keylist=['Quality Factors'], matchedkey=False):
    # If the data is a dictionary, loop through its keys
    if isinstance(data, dict):
        for key, value in data.items():
            # If the key in list is found, print them
            for findkey in keylist:
                if key == findkey:
                    if isinstance(value, list):
                        matchedkey = True
                    else:
                        st.text(f"{findkey} : {data[key]}")
                elif key == "name" and matchedkey:
                    st.text(f"{findkey} : {data[key]}")
                    matchedkey = False
            #st.text("\n\n")
            # Recursively check if the value is another dictionary or list
            Find_ContentInDictionary(value, keylist, matchedkey)
    
    # If the data is a list, loop through its items
    elif isinstance(data, list):
        for item in data:
            # Recursively check if the value is another dictionary or list
            Find_ContentInDictionary(item, keylist, matchedkey)

def get_EvalFileLoading():
    evalcriteria_dict = {}
    if os.path.exists(vl.EVALJSONFILENAME):
        with open(vl.EVALJSONFILENAME, vl.READMODE) as fr:
            evalcriteria_string = fr.read()
            evalcriteria_dict = json.loads(evalcriteria_string)
    return evalcriteria_dict


def get_RAGEvalCriteriaJSON():
  #THis is only if use Parent-Child Document Retrieval
  #retriever_eval = th.get_ParentChildDocRetriever(vl.doc_category.evalplan, vl.READMODE)

  prompt_prefix = """Base on each category and the corresponding table of the category in tender evaluation plan, generate the quality factor, area of assessment, assessment criteria or condition with the respective quality level rating and score.
  Only refer to all content, sections and tables after the text 'Detailed Evaluation Approach'.
  Also include any other category and criteria in subsequent sections and the corresponding table of content to evaluate.
  Strictly output in the format given below enclosed in <myformat>, content are defined in < >.
  """

  sample_jsonformat = """
  Strictly output in JSON format. 
  The JSON should have the following format as shown in example, where category can be more than 1 set :
  <myformat>
  {
    "Category": {
      "name": "Category 8B",
      "SN": 1,
      "Quality Factors": [
        {
        "name": "Hiring Practices",
        "SN": 1.3,
        "weightage": "15%",
        "Areas of Assessment": [
          {
          "name": "Attraction to maintain a constant pipeline of resources",
          "weightage": "5%",
          "Assessment Criteria": [
            {
              "Level": "Weak",
              "Score": 1,
              "Criteria": "Limited focus on attracting candidates through online advertisements without utilizing other sources or outreach methods."
            },
            {...}
          ]
        },
  ....
  }
  </myformat>

  The information above Assessment Criteria list can be either Area of Assessment or Score Assessment under the Area of Assessment.
  For such table data, the format in Area of Assessment shall be as below illustrated:
  <myformat>

        "Areas of Assessment": [      
        {
        "name": "Selection methods to shortlist candidates",
        "weightage": "5%",
        "Score Assessment": [
          {
            "Assessment Criteria": "Relevance of Selection Criteria",
            "Level": [
              {"type": "Weak", "Score": 1, "Criteria": "Selection criteria are vague and not directly related to the job requirements."},
              {"type": "Basic", "Score": 2, "Criteria": "Selection criteria are somewhat aligned with the job requirements."},
              {"type": "Average", "Score": 3, "Criteria": "Selection criteria are clearly defined and somewhat aligned with the job requirements."},
              {"type": "Strong", "Score": 4, "Criteria": "Selection criteria are clearly defined and closely aligned with the skills and attributes needed for the role."}
            ]
          },
          {...}
  </myformat>

  Ensure proper closure characters are included according to JSON format.
  """

  ending_instruction = """
  \n content must be citation from evaluation plan document.
  Each set of information should be unique and not repeated.
  Do not include any other character or backticks or the delimiter <myformat> in your response.
  """
  prompt_eval = prompt_prefix + sample_jsonformat + ending_instruction
  response_eval = llm.get_RAGChainResponse(prompt_eval, max_tokens=5000)
  #Below is for Parent-Child Document Retrieval - KIV
  #response_eval = llm.get_RAGChainResponse(prompt_eval, retriever=retriever_eval)

  #Update Eval JSON file and session state
  jsonstring = response_eval['result']
  #--- temporary added when void StoreJSONFile ---
  '''
  with open(vl.EVALJSONFILENAME, vl.WRITEMODE) as f:
        f.write(jsonstring)
  evalcriteria_dict = json.loads(jsonstring)
  st.session_state[vl.EVALJSON_SESSIONNAME] = evalcriteria_dict
  '''

  StoreJSONFile(jsonstring)
  #th.Find_ContentInDictionary(evalcriteria_dict)

def StoreJSONFile(jsonstring):
    try:
        with open(vl.EVALJSONFILENAME, vl.WRITEMODE) as f:
            f.write(jsonstring)

        docObjs = LoadFile(vl.EVALJSONFILENAME, vl.doc_category.evaljson)
        StoreFiles(docObjs, vl.doc_category.evaljson)

        evalcriteria_dict = json.loads(jsonstring)
        st.session_state[vl.EVALJSON_SESSIONNAME] = evalcriteria_dict

    except Exception as e:
        print(f"Error in StoreJSONFile for file : {e}")
    



def get_RAGProposalEvaluation(proposal_docname):

    try:
        prompt = f"""
        Do the following to evaluate proposal base on criteria in evaluation plan for evaluator.
        You must only rely on the criteria information in the evaluation plan to assess and evaluate.
        Base on each quality assessment criteria with quality score in tender evaluation plan, and only for all content or tables after 'Detailed Evaluation Approach', determine which criteria score is met by {proposal_docname}.
        Also include any other category in subsequent sections and the corresponding table of content to evaluate.
        Format results of assessment for the tender proposal with the below structure.
                <For each Category and it's Quality Factor, present result in below format>
                Category : , Quality Factor:
                Weightage (Quality Factor): <the weightage allocated to the Quality Factor>
                    Area of Assessment: <Area of Assessment on proposal quality, which has a corresponding Weightage>
                    Weightage (Area of Assessment): <the weightage allocated to the Area of Assessment>
                    <For each Area of Assessment of the Quality Factor, present result in below format>
                        Assessment factor: <a assessment criteria group under Area of Assessment, which does not have a corresponding Score in table.>
                            Criteria: <criteria of the score level present in evaluation plan, which the proposal had met.>
                            Level:
                            Score:
                            Summary: <Your response should be comprehensive and informative to help evalulator understand reason and justification for the score met by the proposal.>
                            Citation: 

        State citation of maximum 5 to support the reason for the quality level.

        """

        prompt1 = f"""
        You are an expert to evaluate tender proposals against specific tender proposal for the user.
        Do the following to help user to evaluate proposal.

        You must only rely on the criteria information in the evaluation plan to assess and evaluate.
        base on each assessment criteria with quality score in tender evaluation plan, for all content or tables after 'Detailed Evaluation Approach', determine which criteria score is met by {proposal_docname}.
        Also include any other category in subsequent sections and the corresponding table of content to evaluate.
        format results of assessment for the tender proposal quality with the above structure. State citation of maximum 5 to support the reason for the quality level.

                <for each Area of Assessment of the Quality Factor, present result in below format>
                Category : , Quality Factor:
                    Area of Assessment: 
                            Criteria: <criteria of Area of Assessment or Assessment factor defined in evaluation plan that is met by proposal>
                            Score: <correspond to the criteria met>
                            Level: <correspond to the score, include definition text cite in evaluation plan>
                            Summary: <Your response should be comprehensive and informative to help evalulator understand reason and justification for the score met by the proposal. \
                                    State what the proposal is lacking or excel in with relevance to the area of assessment and criteria>
                            Citation:

        Do step by step to derive result of evaluation.
        """
        #Only draw evaluation response base on the proposal {proposal_docname} and no other proposal.

        #State citation of maximum 5 to support the reason for the quality level achieved.

        ending_instruction = """
            Response in professional manner.
            Make sure the statements are factually accurate.
            State only information in evaluation plan and only use all content or tables after 'Detailed Evaluation Approach' in document.
        """

        finalprompt = prompt1 + ending_instruction
        response = llm.get_RAGChainResponse(finalprompt, max_tokens=5000)
        st.session_state[vl.EVALRESULT_SESSIONNAME] = response['result']

    except Exception as e:
        print(f"Error in get_RAGProposalEvaluation for file : {proposal_docname}: {e}")


def get_RAGProposalEvaluationByJSON(proposal_docname):

    try:

        prompt1 = f"""
        You must only rely on the criteria information in the {vl.doc_category.evaljson} to assess and evaluate.
        base on each assessment criteria with quality score in tender evaluation plan, determine which criteria score is met by document {proposal_docname}.
        format results of assessment for the tender proposal quality with the below structure. State citation of maximum 5 to support the reason for the quality level achieved.
            <for each Area of Assessment of the Quality Factor, evaluate the proposal and present result in below format>
                Category : , Quality Factor:
                    Area of Assessment: <name of Area of Assessment and if any, Assessment Criteria under Area of Assessment>            
                            Criteria: <the condition for the Level to achieve>
                            Score: <Score correspond to the criteria which is met by the proposal>
                            Level: <Level or type of Level met by proposal>
                            Summary: <Your response should be comprehensive and informative to help evalulator understand reason and justification for the score met by the proposal. \
                                    State what the proposal is lacking or excel in with relevance to the area of assessment and criteria. \
                                        give example on how proposal is determined as the Level>
                            Citation: <citation from proposal that support the reasons in summary>

        """

        prompt = f"""
            You are an expert to evaluate tender proposals against specific tender proposal for the user.
            Do the following to help user to evaluate proposal.

            step 1: Loop through on each quality factor and assessment criteria listed in {vl.doc_category.evaljson}
            step 2: Determine which assessment criteria of the respective score level is met by the proposal document {proposal_docname}
            step 3: Summarize the reason and justification for the score level achieved for the proposal document to enable the user to understand why is the score is met.
                    Make response as comprehensive and informative as possible, including stating what is lacking or done well with examples from proposal.
            step 4: state citation from proposal that support the reason in summary. State up to maximum 5 citation.
            step 5: Complete results of assessment for the tender proposal quality with the below structure.

            <for each Area of Assessment of the Quality Factor, evaluate the proposal and present result in below format>
                Category : , Quality Factor:
                    Area of Assessment: <name of Area of Assessment and if any, Assessment Criteria under Area of Assessment>            
                            Criteria: <the condition for the Level to achieve>
                            Score: <Score correspond to the criteria which is met by the proposal>
                            Level: <Level or type of Level met by proposal>
                            Summary: <Your response should be comprehensive and informative to help evalulator understand reason and justification for the score met by the proposal. \
                                    State what the proposal is lacking or excel in with relevance to the area of assessment and criteria. \
                                        give example on how proposal is determined as the Level>
                            Citation: <citation from proposal that support the reasons in summary>

            Do step by step to derive the results of evaluation.
        """

        ending_instruction = """
            Response in professional manner.
            Make sure the statements are factually accurate and evaluation is only done against the proposal stated.

        """
        #        Evaluation shall include all categories in the {vl.doc_category.evaljson}.
            #If you do not know, state no answer.
        finalprompt = prompt + ending_instruction
        
        #query = f"evaluate tender proposal {proposal_docname} document against the tender evaluation plan"
        response = llm.get_RAGChainResponse(finalprompt, max_tokens=5000)
        #response = llm.get_RAGChainResponse(query, max_tokens=5000)
        st.session_state[vl.EVALRESULT_SESSIONNAME] = response['result']

    except Exception as e:
        print(f"Error in get_RAGProposalEvaluationByJSON for file : {proposal_docname}: {e}")

def get_ProposalEvaluationByJSON(proposal_docname):

    try:

        prompt1 = f"""
        You must only rely on the criteria information in the {vl.doc_category.evaljson} to assess and evaluate.
        base on each assessment criteria with quality score in tender evaluation plan, determine which criteria score is met by document {proposal_docname}.
        format results of assessment for the tender proposal quality with the below structure. State citation of maximum 5 to support the reason for the quality level achieved.
            <for each Area of Assessment of the Quality Factor, evaluate the proposal and present result in below format>
                Category : , Quality Factor:
                    Area of Assessment: <name of Area of Assessment and if any, Assessment Criteria under Area of Assessment>            
                            Criteria: <the condition for the Level to achieve>
                            Score: <Score correspond to the criteria which is met by the proposal>
                            Level: <Level or type of Level met by proposal>
                            Summary: <Your response should be comprehensive and informative to help evalulator understand reason and justification for the score met by the proposal. \
                                    State what the proposal is lacking or excel in with relevance to the area of assessment and criteria. \
                                        give example on how proposal is determined as the Level>
                            Citation: <citation from proposal that support the reasons in summary>

        """
        delimiter = "####"

        prompt = f"""
            You are an expert to evaluate tender proposals against specific tender proposal for the user.
            Do the following to help user to evaluate proposal.
            The user query will be delimited with a pair {delimiter}.

            step 1: {delimiter}Loop through and list out each quality factor, area of assessment and all Assessment Criteria listed in {vl.doc_category.evaljson} document.
            step 2: {delimiter}Determine which assessment criteria of the respective score level is met by the proposal document {proposal_docname}
            step 3: {delimiter}Summarize the reason and justification for each score level achieved under the assessment criteria for the proposal document to enable the user to understand why is the score is met.
                    Make response as comprehensive and informative as possible, including stating what is lacking or done well with examples from proposal.
            step 4: {delimiter}state citation from proposal that support the reason in summary. State up to maximum 5 citation.
            step 5: {delimiter}Complete results of assessment for the tender proposal quality with the below structure.

            <for each Area of Assessment of the Quality Factor, evaluate the proposal and present result in below format>
                Category : , Quality Factor:
                    Area of Assessment: <name of Area of Assessment and including if any, Assessment Criteria of Score Assessment under Area of Assessment>            
                            Criteria: <the condition for the Level to achieve>
                            Score: <Score correspond to the criteria which is met by the proposal>
                            Level: <Level or type of Level met by proposal>
                            Summary: <Your response should be comprehensive and informative to help evalulator understand reason and justification for the score met by the proposal. \
                                    State what the proposal is lacking or excel in with relevance to the area of assessment and criteria. \
                                        give example on how proposal is determined as the Level>
                            Citation: <citation from proposal that support the reasons in summary>

            Do step by step to derive the results.
            Make sure to include {delimiter} to separate every step, but no {delimiter} at the end
        """


        ending_instruction = """
            Response in professional manner.
            Make sure the statements are factually accurate and evaluation is only done against the proposal stated.

        """
        #        Evaluation shall include all categories in the {vl.doc_category.evaljson}.
            #If you do not know, state no answer.

        #prepare relevant document as context
        doc_response = llm.get_SimilaritySearch(prompt)
        context = "\n".join([doc.page_content for doc in doc_response])

        system_prompt = f"""
            Use the following pieces of context if any, as well as the context given in question to answer the question at the end.
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            context: {doc_response}
        """

        #get LLM response
        finalprompt = system_prompt + prompt + ending_instruction
        response = llm.get_completion(finalprompt, max_tokens=3000) 
        #query = f"evaluate tender proposal {proposal_docname} document against the tender evaluation plan"
        #response = llm.get.get_RAGChainResponse(finalprompt, context=context, max_tokens=5000)
        #response = llm.get_RAGChainResponse(query, max_tokens=5000)
        st.session_state[vl.EVALRESULT_SESSIONNAME] = response.split(delimiter)[-1]

    except Exception as e:
        print(f"Error in get_ProposalEvaluationByJSON for file : {proposal_docname}: {e}")


def ProcessChatBotPrompt(user_query=""):
    prompt = f"""
        You are an expert to answer queries for user related to the evaluation plan and tender proposals.
        You must only rely on the evaluation criteria information in the {vl.doc_category.evaljson} to assess and evaluate.

        Do the followings step by step:

        step 1: Determine if the query is asking about tender evaluation plan or tender proposals.
        step 2: Only reply on query related to these based on the relevant documents and base on information in tender evaluation plan or proposals.
        step 3: for query on specific proposal, only draw evaluation response base on the proposal and no other proposal.
        step 4: Your response should be as detail as possible and \
                include information that is useful for user to better understand the evaluation result
        step 5: Answer the user in a friendly tone.
                Make sure the statements are factually accurate.
                Your response should be comprehensive and informative to help the \
                the user to make their decision.
                Complete with details such the reason for the quality score, criteria etc in evaluation plan as well as any details in proposals to enable the user to evaluate against proposal.
                Use Neural Linguistic Programming to construct your response.

        <user query>
    """

    finalprompt = prompt + user_query
    response = llm.get_RAGChainResponse(finalprompt, context=st.session_state[vl.LASTCHATCONTEXT], max_tokens=5000)
    st.session_state[vl.LASTCHATCONTEXT] = response['result']

def get_EvalBySimilaritySearch(proposal_docname):
    prompt1 = f"""
            You are an expert to evaluate tender proposals against specific tender proposal for the user.
            Do the following step by step:

            step 1: Loop through on each quality factor and assessment criteria listed in {vl.doc_category.evaljson}
            step 2: Determine which assessment criteria of the respective score level is met by the proposal document {proposal_docname}
            """
    prompt = f"""
        base on each assessment criteria with quality score in tender evaluation plan, for all content or tables after 'Detailed Evaluation Approach', determine which criteria score is met by {proposal_docname}.
        Also include any other category in subsequent sections and the corresponding table of content to evaluate.
        format results of assessment for the tender proposal quality with the above structure. State citation of maximum 5 to support the reason for the quality level.

                <for each Area of Assessment of the Quality Factor, present result in below format>
                Category : , Quality Factor:
                    Area of Assessment: 
                            Criteria: <criteria of Area of Assessment or Assessment factor defined in evaluation plan that is met by proposal>
                            Score: <correspond to the criteria met>
                            Level: <correspond to the score, include definition text cite in evaluation plan>
                            Summary: <Your response should be comprehensive and informative to help evalulator understand reason and justification for the score met by the proposal. \
                                    State what the proposal is lacking or excel in with relevance to the area of assessment and criteria>
                            Citation:

        """
    prompt2 = "evaluate proposal document given below against the tender evaluation plan : {proposal_docname}"
    #prompt2 = prompt2 + proposal_docname
    
    response = llm.get_SimilaritySearch(prompt2)
    st.session_state[vl.EVALRESULT_SESSIONNAME] = response

def SaveProposalEvalResult(proposal_docname):
    try:
        resultfilename = f"result_{os.path.splitext(proposal_docname)[0]}.txt"
        existingresultfiles = get_AllFilesInCollection(vl.COLLECTIONNAME_RESULT)
        if resultfilename in existingresultfiles:
            warn_msg = f"file [{resultfilename}] already exist.\
                    To replace file, please purge all files and re-upload to evaluate."
            st.warning(warn_msg, icon="🚨")
            st.toast(warn_msg, icon="🚨")
        else:
            
            proposalfilepath = os.path.join("data", resultfilename)
            with open(proposalfilepath, vl.WRITEMODE) as f:
                f.write(st.session_state[vl.EVALRESULT_SESSIONNAME])

            docObjs = LoadFile(proposalfilepath, vl.doc_category.proposal)
            StoreFiles(docObjs, vl.doc_category.proposal, vl.COLLECTIONNAME_RESULT)
            st.toast('Save shortlisted proposal successfully')
    except Exception as e:
        print(f"Error in SaveProposalEvalResult for file : {proposal_docname}: {e}")
