# Set up and run this Streamlit App
import streamlit as st
from helper_functions import utility as ut

#---to overcome issue of streamlit cloud runtime error---#
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


def main():
    pages = [st.Page("aboutus.py", title="About Us"),
            st.Page("./pages/docupload.py", title="Document Upload"),
            st.Page("./pages/Evaluate Quality.py", title="Evaluate Tender Proposals"),
            st.Page("./pages/EvaluateShortListed.py", title="Evaluate Shortlisted Tender Proposals"),
            st.Page("./pages/Methodology.py", title="Methodology")
            ]

    pg = st.navigation(pages)
    pg.run()

if __name__ == "__main__": 
    # Do not continue if check_password is not True.  
    if not ut.check_password():  
        st.stop()
        
    main()

