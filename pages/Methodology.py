import streamlit as st
from helper_functions import valuelist as vl
from helper_functions import utility as ut
import os



st.set_page_config(
    layout="centered",
    page_title="Methodology"
)

# Do not continue if check_password is not True.  
if not ut.check_password():  
    st.stop()

st.title("Methodology")
st.write("""Below show the detailed methodology in flow chart. Data information used in this project are mocked up, although the format of evaluation plan is taken from the
        Official-Closed evaluation plan document of old tender published.""")

with st.expander("Screen Structure"):
    st.image(os.path.join(vl.IMAGELOCATION, "Slide7.JPG"))

with st.expander("Documents Uploading"):
    st.image(os.path.join(vl.IMAGELOCATION, "Slide8.JPG"))

with st.expander("Evaluate Proposal"):    
    st.image(os.path.join(vl.IMAGELOCATION, "Slide9.JPG"))
    st.image(os.path.join(vl.IMAGELOCATION, "Slide10.JPG"))
    st.image(os.path.join(vl.IMAGELOCATION, "Slide11.JPG"))
    st.image(os.path.join(vl.IMAGELOCATION, "Slide13.JPG"))

with st.expander("Evaluate Shortlisted Proposals"):
    st.image(os.path.join(vl.IMAGELOCATION, "Slide12.JPG"))

with st.expander("Screenshots of Application"):
    st.write("Document Upload Screenshots: ")
    st.image(os.path.join(vl.SCREENSHOTLOCATION, "Document Upload-Tender Evaluation File.jpg"))
    st.image(os.path.join(vl.SCREENSHOTLOCATION, "Document Upload-Tender Proposal Files.jpg"))

    st.write("Evaluate Tender Proposal Screenshots: ")
    st.image(os.path.join(vl.SCREENSHOTLOCATION, "Evaluate Tender Proposal-View JSON Format.jpg"))
    st.image(os.path.join(vl.SCREENSHOTLOCATION, "Evaluate Tender Proposal-Evaluate proposal by JSON file.jpg"))
    st.image(os.path.join(vl.SCREENSHOTLOCATION, "Evaluate Tender Proposal-Save Shortlist Proposal.jpg"))
    st.image(os.path.join(vl.SCREENSHOTLOCATION, "Evaluate Tender Proposal-Chatbot.jpg"))

    st.write("Evaluate Shortlisted Proposals Screenshots: ")
    st.write("Default Landing Page:")
    st.image(os.path.join(vl.SCREENSHOTLOCATION, "Shortlisted Tender Proposal Evaluation-Landing Page.jpg"))
    st.write("Final Evaluation of Shortlisted Proposals :")
    st.image(os.path.join(vl.SCREENSHOTLOCATION, "Shortlisted Tender Proposal Evaluation-Final Results.jpg"))
