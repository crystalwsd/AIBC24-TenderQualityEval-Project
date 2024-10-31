# filename: utility.py
import streamlit as st  
import random  
import hmac  
import json
#from docx import Document
  
# """  
# This file contains the common components used in the Streamlit App.  
# This includes the sidebar, the title, the footer, and the password check.  
# """  
  
  
def check_password():  
    """Returns `True` if the user had the correct password."""  
    def password_entered():  
        """Checks whether a password entered by the user is correct."""  
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):  
            st.session_state["password_correct"] = True  
            del st.session_state["password"]  # Don't store the password.  
        else:  
            st.session_state["password_correct"] = False  
    # Return True if the passward is validated.  
    if st.session_state.get("password_correct", False):  
        return True  
    # Show input for password.  
    st.text_input(  
        "Password", type="password", on_change=password_entered, key="password"  
    )  
    if "password_correct" in st.session_state:  
        st.error("😕 Password incorrect")  
    return False


def writetofile(text, filename):
    try:

        file = open(f"./data/{filename}", "w")

        # Write some text to the file
        file.write(text)

        # Close the file
        file.close()
    except Exception as e:
        print(f"Error encountered in writetofile() for file {filename} : {e}")
        return False

    return True
