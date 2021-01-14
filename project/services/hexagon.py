import streamlit as st
import geopandas as gpd
from turpy.io.gdrive import download_file
from pathlib import Path

import geoplot as gplt
# import geoplot.crs as gcrs
import matplotlib.pyplot as plt



st.title('Hexagon grid')

DATA_URL = r"https://drive.google.com/file/d/11J7dG7JIkdnMvA2thgB97rRUV7A6226j/view?usp=sharing"


@st.cache
def load_geopandas_dataset(
    DATA_URL: str, 
    dirpath: str = './data/',
    check_filepath: str = "./data/NMD2018_boolean_klass_62_10m.gpkg"):
    """

    Note: assumes datapath like:
    DATA_URL = r"https://drive.google.com/file/d/<google_file_id>/view?usp=sharing"
    """
    file_id = DATA_URL.split('/')[-2]

    save_dest = Path(dirpath)
    save_dest.mkdir(exist_ok=True)

    f_checkpoint = Path(check_filepath)

    if not f_checkpoint.exists():
        with st.spinner("Downloading data from google drive... this may take sometime! \n Please wait ..."):
            download_file(id=file_id, destination=f_checkpoint)

    gdf = gpd.read_file(f_checkpoint)  
    return gdf
    


def main():

    fig, ax = plt.subplots(figsize=(2, 4))

    gdf = load_geopandas_dataset(
        DATA_URL=DATA_URL, 
        dirpath='./data/', 
        check_filepath = "./data/NMD2018_boolean_klass_62_10m.gpkg")

    #world = gpd.read_file(
    #    gpd.datasets.get_path('naturalearth_lowres'))
    #sweden = world.query('name == "Sweden"')    
    #sweden.plot(edgecolor='None', facecolor='lightgray', ax=ax)
    
    gdf.plot(ax=ax)
    ax.axis('off')


    # gplt.polyplot(gdf, ax=ax)

    st.pyplot(fig)
   
    
        


#
main()
