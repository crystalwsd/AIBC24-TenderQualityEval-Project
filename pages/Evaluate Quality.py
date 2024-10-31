import json
import pandas as pd
import numpy as np
import streamlit as st
from logics import tender_files_handler as th
from logics import query_handler as qh
from helper_functions import valuelist as vl
from helper_functions import utility as ut
import os
#from logics import crewai_handler as ch

#--- function to derive JSON file content into session ---#
def GenerateJSONEvalFile():
    #if len(st.session_state[vl.EVALJSON_SESSIONNAME]) == 0:
      if len(st.session_state[vl.METADATA_SESSIONNAME]) > 0:
        if vl.doc_category.evalplan in st.session_state[vl.METADATA_SESSIONNAME]['doc_category'].values:
          th.get_RAGEvalCriteriaJSON()
        else:
          st.warning("No tender evaluation plan document. Please go to Document Upload to upload document for evaluation", icon="🚨")
    #st.json(st.session_state[vl.EVALJSON_SESSIONNAME])



#-- Set up page layout ---#
st.set_page_config(
    layout="centered",
    page_title="Evaluate Tender Proposal"
)

# Do not continue if check_password is not True.  
if not ut.check_password():  
    st.stop()

st.header("Tender Proposal Evaluation")


# Initialize Session Names
if vl.METADATA_SESSIONNAME not in st.session_state:
  th.get_MetadataStoreToSession()

if vl.EVALJSON_SESSIONNAME not in st.session_state:
  if os.path.exists(vl.EVALJSONFILENAME):
    st.session_state[vl.EVALJSON_SESSIONNAME] = th.get_EvalFileLoading()
  else:
    st.session_state[vl.EVALJSON_SESSIONNAME] = {}

if vl.EVALRESULT_SESSIONNAME not in st.session_state:
  st.session_state[vl.EVALRESULT_SESSIONNAME] = ""

if vl.LASTPROPOSALOPTION not in st.session_state:
  st.session_state[vl.LASTPROPOSALOPTION] = ""

if vl.LASTCHATCONTEXT not in st.session_state:
  st.session_state[vl.LASTCHATCONTEXT] = ""

#--- button to start generate JSON evaluation file--#

if len(st.session_state[vl.EVALJSON_SESSIONNAME]) == 0 and \
    len(st.session_state[vl.METADATA_SESSIONNAME]) > 0:
  st.write("""Please click below to generate an Evaluation Plan JSON file, which will be used for evaluation.\
           This provide enhanced accuracy and improve consistency in evaluation outcome. \
           Note that the generation would take couple of minutes to run.""")
  st.button("Generate Evaluation Plan JSON file", on_click=GenerateJSONEvalFile)
else:
  st.write("""Tender evaluation plan document is loaded as JSON file format to enhance \
         the accuracy of evaluation for proposals. Below are the options available to perform evaluation.
         """)

with st.expander("View Evaluation Plan Extraction (JSON format)"):
  st.json(st.session_state[vl.EVALJSON_SESSIONNAME])

# Allow user to choose which proposal file to evaluate
proposal_option = ""
if len(st.session_state[vl.METADATA_SESSIONNAME]) > 0 and \
    len(st.session_state[vl.EVALJSON_SESSIONNAME]) > 0:
  with st.expander("Evaluate Proposal"):
    df_metadata = st.session_state[vl.METADATA_SESSIONNAME]
    plist = df_metadata.loc[df_metadata['doc_category']==vl.doc_category.proposal, 'doc_name']
    selection_text = """Select the proposal to evaluate: """
    proposal_option = st.selectbox(selection_text, plist)
    if st.session_state[vl.LASTPROPOSALOPTION] != proposal_option:
      st.session_state[vl.LASTPROPOSALOPTION] = proposal_option
      st.session_state[vl.EVALRESULT_SESSIONNAME] = ""

    #st.button("Evaluate proposal in Summary", on_click=th.get_RAGProposalEvaluation,
    #                                            args=[proposal_option])
    st.write("""Click here to run evaluation process for above selected proposal.\
             Note that this will take serveral minutes to generate results.""")
    st.button("Evaluate proposal by JSON file", on_click=th.get_ProposalEvaluationByJSON,
                                                args=[proposal_option])
    #---temporary to test ---#
    #st.button("Evaluate proposal by Similarity Search", on_click=th.get_EvalBySimilaritySearch,
    #                                            args=[proposal_option])
    #st.button("Evaluate proposal by CrewAI", on_click=ch.CrewAIEvaluation,
    #                                            args=[proposal_option])

    st.subheader(f"Evaluation Summary for {proposal_option}", divider=True)
    st.write(st.session_state[vl.EVALRESULT_SESSIONNAME])
    if st.session_state[vl.EVALRESULT_SESSIONNAME] != "":
      st.write("click to save the result and shortlist the proposal for further evaluation")
      st.button("Shortlist Proposal", on_click=th.SaveProposalEvalResult, args=[proposal_option])



with st.expander("Evaluate by Chatbot"):

  # Insert a chat message container.
  user_prompt = ""
  cmsg = st.chat_message("user")
  cmsg.write("Hello 👋 How may I help you?")
      
# Display a chat input widget.
  user_prompt = st.chat_input("Say something")
  if user_prompt is not None:
    cmsg.write(user_prompt)
    th.ProcessChatBotPrompt(user_prompt)
    #botresponse = qh.SelfQueryRetriever(user_prompt)
    botresponse = st.session_state[vl.LASTCHATCONTEXT]
    cmsg.write(botresponse)
