import os
import sys
import streamlit as st
from config import OPENCODE_PATH
if OPENCODE_PATH not in sys.path:
    sys.path.append(OPENCODE_PATH)

# `opencode` in github
import opencode as oc
from services import get_available_activities
from config import SERVICES_YAML_URL



def main():
    st.sidebar.title('Menu:')
    st.title(f'AquaBiota Water Research')

    selected_service, _ = get_available_activities(
    filepath=os.path.abspath(SERVICES_YAML_URL), label="services:", key='services')

    


if __name__ == "__main__":
    main()
