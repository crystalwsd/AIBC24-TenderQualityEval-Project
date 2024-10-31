import json
import pandas as pd
import numpy as np
import streamlit as st
from logics import tender_files_handler as th
from logics import shortlisting_handler as sh
from helper_functions import valuelist as vl
from helper_functions import utility as ut
import os

#-- Set up page layout ---#
st.set_page_config(
    layout="centered",
    page_title="Evaluate Tender Shortlisted Proposal"
)

# Do not continue if check_password is not True.  
if not ut.check_password():  
    st.stop()
    
#set session variable
if vl.RESULTCONTENT_SESSIONNAME not in st.session_state:
  st.session_state[vl.RESULTCONTENT_SESSIONNAME] = ""


st.header("Shortlisted Tender Proposal Evaluation")
st.write("Below list the tender proposal(s) which are shortlisted in Tender Proposal Evaluation.")

#Display all document name of shortlisted proposal
shortlistdocs = th.get_AllFilesInCollection(vl.COLLECTIONNAME_RESULT)
df_shortlistdocs = pd.DataFrame(shortlistdocs, columns=['Shortlisted Proposal'])
st.table(df_shortlistdocs)

#to evaluate all proposals shortlisted and derive a conclusion
results = ""
if st.button("Evaluate all proposals"):
    results = sh.get_ShortlistProposalEvaluation()
    st.subheader("Evaluation Results", divider=True)
    #st.write(results)
    st.session_state[vl.RESULTCONTENT_SESSIONNAME] = results

#default shows all content of all evaluation results of shortlist proposals
if len(results) == 0:
    sproposal_content = ""
    st.subheader("Content of Evaluation Result of Proposals", divider=True)
    for doc in shortlistdocs:
        #st.subheader(f"Evaluation Result of Proposal : {doc}", divider=True)
        sproposal_content = f"{sproposal_content}\n\nEvaluation Result of Proposal : {doc}\n\n"
        docfilepath = os.path.join("data", doc)
        with open(docfilepath, vl.READMODE) as f:
            sproposal_content = sproposal_content + f.read() + "\n"
            sproposal_content = sproposal_content + "\n=====================================================================================\n"
    st.session_state[vl.RESULTCONTENT_SESSIONNAME] = sproposal_content

st.write(st.session_state[vl.RESULTCONTENT_SESSIONNAME])
