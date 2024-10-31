import streamlit as st
from helper_functions import valuelist as vl
from helper_functions import utility as ut
import os



st.set_page_config(
    layout="centered",
    page_title="About Us"
)

# Do not continue if check_password is not True.  
if not ut.check_password():  
    st.stop()


st.title("About Us")
st.write("""This is a Tender Quality Evaluation application that demonstrates how to use the OpenAI API to help in quality evaluation of proposals.\n
Click below for more information.""")


with st.expander("How to use this App"):
    st.write("""
            1. Upload Tender Evaluation Plan (limited to 1 file only) :\n
             - 'Browse' to select file from your local store \n
             - Click 'Confirm Upload Evaluation File' button \n
             - Successfully uploaded evaluation file will appear in the top table \n
             
            2. Upload 1 or more Proposal files \n
             - Steps similar to above \n
             - Note that upon load, you may return back to the Tender Evaluation Plan File tab. \n
               Click back 'Proposal' tab to continue with any proposal file upload. \n
             
            3. Go to Evaluate Tender Proposals, click on 'Generate Evaluation Plan JSON file' button. \n
             - this will take a couple of minutes to generate evaluation plan into a JSON file\n
             - You may view the JSON file format by clicking on 'View Evaluation Plan Extraction (JSON format)'\n
             
            4. Under Evaluate Tender Proposals -> Evaluate Proposal, click on "Evaluate proposal by JSON file"\n
             - this will take serveral minutes to return LLM response on the assessment and score achieved in proposal\n
             - if you decide that the proposal is to be shortlisted for further evaluation, click on 'Shortlist Proposal'\n
               This will save the response result and to be further evaluate under 'Evaluate Shortlisted Tender Proposals"\n
             
            5. You may carry out evaluation through Chatbot conversation with OpenAI under 'Evaluate by Chatbot' option. \n
             - Only your last response in conversation thread is remembered by the LLM. Do keep your prompt concise and specific.\n

            6. Go to 'Evaluate Shortlisted Tender Proposals', where you'll see a list of shortlisted proposals and their evaluation result content.\n
             - Click on 'Evaluate all proposals', which will compare and provide a summarized evaluation results among the shortlisted proposals.\n

            Note:
             - In event you want to redo your evaluation or make changes to the documents, you will need to purge all files under the document upload module.\n
               After purge, redo your files uploading and evaluation.\n
             - Your evaluation plan has to follow certain format. Refer to the 'About the Application' for details.

             """)
    
with st.expander("Disclaimer"):
    disclaim_text = """

IMPORTANT NOTICE: This web application is developed as a proof-of-concept prototype. The information provided here is NOT intended for actual usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.

Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.

Always consult with qualified professionals for accurate and personalized advice.

"""
    st.write(disclaim_text)

with st.expander("About the Application"):
    st.image(os.path.join(vl.IMAGELOCATION, "Slide2.JPG"))
    st.image(os.path.join(vl.IMAGELOCATION, "Slide6.JPG"))
    st.image(os.path.join(vl.IMAGELOCATION, "Slide3.JPG"))
    st.image(os.path.join(vl.IMAGELOCATION, "Slide4.JPG"))
    st.image(os.path.join(vl.IMAGELOCATION, "Slide5.JPG"))
