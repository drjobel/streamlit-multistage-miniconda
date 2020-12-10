import os
import streamlit as st
from services import get_available_activities
from config import SERVICES_YAML_URL


def main():
    st.sidebar.title('AquaBiota')  

    selected_service, _ = get_available_activities(
    filepath=os.path.abspath(SERVICES_YAML_URL), label="services:", key='services')

    


if __name__ == "__main__":
    main()
