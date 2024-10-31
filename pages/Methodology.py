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

st.title("Methodlogy")
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

