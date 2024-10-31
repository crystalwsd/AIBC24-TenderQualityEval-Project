import streamlit as st
#test --to remove
from helper_functions import llm
from helper_functions import valuelist as vl
from helper_functions import utility as ut
from logics import tender_files_handler as th
import os
import docx2txt


st.set_page_config(
    layout="centered",
    page_title="About Us"
)

# Do not continue if check_password is not True.  
if not ut.check_password():  
    st.stop()

st.title("About Us")
st.text("This is a Streamlit App that demonstrates how to use the OpenAI API to generate text completions.")

with st.expander("How to use this App"):
    st.write("""
            1. Enter your prompt in the text area \n
            2. Click the 'Submit' button \n
            3. The app will generate a text completion based on your prompt
             """)
    
#testing code
if os.path.exists(vl.EVALJSONFILENAME):
    with open(vl.EVALJSONFILENAME, vl.READMODE) as f:
        filecontent = f.read()
        cnt = llm.count_tokens(filecontent)
        st.write(f"token counts in eval json file : {cnt}")


filelist = th.get_AllFilesInCollection()
filelist

for file in filelist:
    filepath = os.path.join("data", file)
    if os.path.exists(filepath):
        filetype = os.path.splitext(filepath)[1]
        if filetype == ".docx":
            doc = docx2txt.process(filepath)
            cnt = llm.count_tokens(doc)
        else:
            with open(filepath, vl.READMODE) as f:
                filecontent = f.read()
                cnt = llm.count_tokens(filecontent)
        st.write(f"token counts in {file} : {cnt}")

st.write("METADATA SESSION VAR:")
st.write(st.session_state[vl.METADATA_SESSIONNAME])