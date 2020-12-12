import os
import streamlit as st
from services import get_available_activities
from config import SERVICES_YAML_URL
from context import metadata




def main():
    st.sidebar.title('AquaBiota')  

    selected_service, _ = get_available_activities(
    filepath=os.path.abspath(SERVICES_YAML_URL), label="services:", key='services')

    # metadata.update({'selected_service': selected_service})

if __name__ == "__main__":
    main()
