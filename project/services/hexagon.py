import os
import json
from shapely.geometry import Polygon
import streamlit as st
import geopandas as gpd
from turpy.io.gdrive import download_file
from pathlib import Path

import geoplot as gplt
# import geoplot.crs as gcrs
import matplotlib.pyplot as plt

from h3 import h3
import folium
import streamlit.components.v1 as components

from config import DATA_URL_DICT


st.title('Hexagon grid')


@st.cache
def load_geopandas_dataset(
    DATA_URL: str, 
    dirpath: str = './data/',
    filename: str = "NMD2018_boolean_klass_62_10m.gpkg"):
    """

    Note: assumes datapath like:
    DATA_URL = r"https://drive.google.com/file/d/<google_file_id>/view?usp=sharing"
    """
    file_id = DATA_URL.split('/')[-2]

    save_dest = Path(dirpath)
    save_dest.mkdir(exist_ok=True)

    f_checkpoint = Path(os.path.join(dirpath, filename))

    if not f_checkpoint.exists():
        with st.spinner("Downloading data from google drive... this may take sometime! \n Please wait ..."):
            download_file(id=file_id, destination=f_checkpoint)

    gdf = gpd.read_file(f_checkpoint)  
    return gdf
    
""" when useing folium you need to reproject to 4326
import geopandas as gpd
df = gpd.read_file(data)

"""

def visualize_hexagons(hexagons, color="red", folium_map=None):
    """
    hexagons is a list of hexcluster. Each hexcluster is a list of hexagons. 
    eg. [[hex1, hex2], [hex3, hex4]]

    source: https://nbviewer.jupyter.org/github/uber/h3-py-notebooks/blob/master/notebooks/usage.ipynb
    """
    polylines = []
    lat = []
    lng = []
    for hex in hexagons:
        polygons = h3.h3_set_to_multi_polygon([hex], geo_json=False)
        # flatten polygons into loops.
        outlines = [loop for polygon in polygons for loop in polygon]
        polyline = [outline + [outline[0]] for outline in outlines][0]
        lat.extend(map(lambda v: v[0], polyline))
        lng.extend(map(lambda v: v[1], polyline))
        polylines.append(polyline)

    if folium_map is None:
        m = folium.Map(location=[sum(lat)/len(lat), sum(lng) /
                                 len(lng)], zoom_start=13, tiles='cartodbpositron')
    else:
        m = folium_map
    for polyline in polylines:
        my_PolyLine = folium.PolyLine(
            locations=polyline, weight=8, color=color)
        m.add_child(my_PolyLine)
    return m


def visualize_polygon(polyline, color):
    """
    source: https://nbviewer.jupyter.org/github/uber/h3-py-notebooks/blob/master/notebooks/usage.ipynb
    """
    polyline.append(polyline[0])
    lat = [p[0] for p in polyline]
    lng = [p[1] for p in polyline]
    m = folium.Map(location=[sum(lat)/len(lat), sum(lng) /
                             len(lng)], zoom_start=13, tiles='cartodbpositron', crs='EPSG3006')   # default 'EPSG3857'
    my_PolyLine = folium.PolyLine(locations=polyline, weight=8, color=color)
    m.add_child(my_PolyLine)
    return m




def folium_static(fig, width=700, height=500):
    """
    Renders `folium.Figure` or `folium.Map` in a Streamlit app. This method is 
    a static Streamlit Component, meaning, no information is passed back from
    Leaflet on browser interaction.

    Source: https://github.com/randyzwitch/streamlit-folium/blob/master/streamlit_folium/__init__.py
    # NOTE: reproduced in order to be able to use it without installing the component.
    Parameters
    ----------
    width : int
        Width of result
    
    Height : int
        Height of result
    Note
    ----
    If `height` is set on a `folium.Map` or `folium.Figure` object, 
    that value supersedes the values set with the keyword arguments of this function. 
    Example
    -------
    >>> m = folium.Map(location=[45.5236, -122.6750])
    >>> folium_static(m)
    """

    # if Map, wrap in Figure
    if isinstance(fig, folium.Map):
        fig = folium.Figure().add_child(fig)

    return components.html(
        fig.render(), height=(fig.height or height) + 10, width=width
    )


def gdf_to_h3_geojson(gdf: gpd.GeoDataFrame):

    assert gdf.crs is not None
    assert gdf.crs != ""

    st.write(f"gdf.crs: {gdf.crs}")
    df = gdf.to_crs(epsg='4326')
    js = df.to_json() #  this is a string
    geoJSON = json.loads(js)

    return geoJSON

def build_hexs(gdf:gpd.GeoDataFrame, APERTURE_SIZE:int = 8):
    """
    source: https://geographicdata.science/book/data/h3_grid/build_sd_h3_grid.html
    """
    hexs = h3.polyfill(
        gdf.geometry[0].__geo_interface__, APERTURE_SIZE, geo_json_conformant=True)
    return hexs


def polygonise(hex_id):
    """
    source: https://geographicdata.science/book/data/h3_grid/build_sd_h3_grid.html
    """ 
    return Polygon(h3.h3_to_geo_boundary(
        hex_id, geo_json=True))


def polygonize_hexagons(gdf: gpd.GeoDataFrame, APERTURE_SIZE: int = 8, crs: str = "EPSG:4326"):
    """
    https://geographicdata.science/book/data/h3_grid/build_sd_h3_grid.html
    """

    GeoJSON_polygon = gdf_to_h3_geojson(gdf=gdf)



    hexs = h3.polyfill(GeoJSON_polygon, APERTURE_SIZE, geo_json_conformant=True)

    all_polys = gpd.GeoSeries(list(map(polygonise, hexs)),
                                    index=hexs,
                                    crs=crs
                                    )
    return all_polys



def main():

    APERTURE_SIZE = 7

    filename = DATA_URL_DICT[3]['name']
    DATA_URL = DATA_URL_DICT[3]['URL']
    
    gdf = load_geopandas_dataset(
        DATA_URL=DATA_URL, 
        dirpath='./data/', 
        filename=filename)

    hexagons = polygonize_hexagons(gdf=gdf, APERTURE_SIZE=8, crs='EPSG:3006')


    fig, ax = plt.subplots(figsize=(2, 4))
    ax = hexagons.plot(alpha=0.5, color="xkcd:pale yellow", figsize=(9, 9))

    st.pyplot(fig)

    #fig, ax = plt.subplots(figsize=(2, 4))
    #world = gpd.read_file(
    #    gpd.datasets.get_path('naturalearth_lowres'))
    #sweden = world.query('name == "Sweden"')    
    #sweden.plot(edgecolor='None', facecolor='lightgray', ax=ax)
    #gdf.plot(ax=ax)
    #ax.axis('off')
    #st.pyplot(fig)
    """
    # lat, lng, hex resolution
    h3_address = h3.geo_to_h3(58.426172, 17.3623063, APERTURE_SIZE)
    hex_center_coordinates = h3.h3_to_geo(h3_address)
    hex_boundary = h3.h3_to_geo_boundary(h3_address)

    m = visualize_hexagons([h3_address])

    m = visualize_hexagons(list(h3.k_ring_distances(
        h3_address, 4)[3]), color="purple")
    m = visualize_hexagons(list(h3.k_ring_distances(
        h3_address, 4)[2]), color="blue", folium_map=m)
    m = visualize_hexagons(list(h3.k_ring_distances(
        h3_address, 4)[1]), color="green", folium_map=m)
    m = visualize_hexagons(list(h3.k_ring_distances(
        h3_address, 4)[0]), color="red", folium_map=m)

    # add marker for center

    # add marker for Liberty Bell
    tooltip = "Hexagon center"
    folium.Marker(
        hex_center_coordinates, popup="Hexagon center", tooltip=tooltip
    ).add_to(m)
    """
    #geoJson = gdf_to_h3_geojson(gdf=gdf)
    #st.write(geoJson)
    #polyline = geoJson['coordinates'][0]
    """
    polyline.append(polyline[0])
    lat = [p[0] for p in polyline]
    lng = [p[1] for p in polyline]
    m = folium.Map(location=[sum(lat)/len(lat), sum(lng) /
                            len(lng)], zoom_start=13, tiles='cartodbpositron')
    my_PolyLine = folium.PolyLine(locations=polyline, weight=8, color="green")
    m.add_child(my_PolyLine)

    hexagons = list(h3.polyfill(geoJson, APERTURE_SIZE))
    polylines = []
    lat = []
    lng = []
    for hex in hexagons:
        polygons = h3.h3_set_to_multi_polygon([hex], geo_json=False)
        # flatten polygons into loops.
        outlines = [loop for polygon in polygons for loop in polygon]
        polyline = [outline + [outline[0]] for outline in outlines][0]
        lat.extend(map(lambda v: v[0], polyline))
        lng.extend(map(lambda v: v[1], polyline))
        polylines.append(polyline)
    for polyline in polylines:
        my_PolyLine = folium.PolyLine(locations=polyline, weight=8, color='red')
        m.add_child(my_PolyLine)


    # call to render Folium map in Streamlit
    folium_static(m)
    """

#
main()
