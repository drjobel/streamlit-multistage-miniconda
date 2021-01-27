import os
import streamlit as st
from collections import OrderedDict
from turpy.io.load_yaml import load_yaml
from turpy.utils import script_as_module

def get_available_activities(filepath: str, label: str = "services to perform", key: str = None):
    """Retrieves from a yaml file the services to show to the user as a sidebar menu"""

    available_activities_list = load_yaml(filepath=os.path.abspath(filepath))

    activities_dict = OrderedDict(
        {item['name']: item for item in available_activities_list})

    tasks_names = []
    selected_task = None

    if available_activities_list is not None:

        for _, task_dict in activities_dict.items():
            tasks_names.append(
                (task_dict['name'], task_dict['url']))

        selected_task, module_filepath = st.sidebar.selectbox(
            label,
            tasks_names, format_func=lambda x: str(x[0]), key=key)
        # Super geek powers!
        script_as_module(module_filepath)

    return selected_task, activities_dict
