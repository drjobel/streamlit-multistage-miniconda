import streamlit as st

# Extract-Transform-Load (ETL)

with st.beta_expander(label="Input files", expanded=True):
   
    uploaded_file =  st.file_uploader('', )

    st.write("""
    Only `tab` separated text files with `encoding='utf-8` are accepted.
    
    ***NOTE:*** *`max uploaded size = 200 MB`)*.""")
    
    if uploaded_file is not None:
        st.write(uploaded_file )
