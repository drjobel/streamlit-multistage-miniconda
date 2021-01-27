import os
from pathlib import Path
import json
import geojson
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
import geopandas as gpd
from shapely.geometry import Polygon
import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
from h3 import h3
import folium

from turpy.io.gdrive import download_file
from config import DATA_URL_DICT
from h3_funtools import visualize_hexagons, visualize_polygon, polygonize_hexagons

import warnings
warnings.filterwarnings('ignore')

# don't use scientific notation
np.set_printoptions(suppress=True)
pd.set_option('display.float_format', lambda x: '%.5f' % x)


st.title('Hexagon grid')

# Stockholm
lat_centr_point = 59.6025
lon_centr_point = 18.1384


def latlong_to_geojson_string_h3_geometry(latitude_dd:float, longitude_dd:float, resolution: int = 8)->str:
    """Converts a lat long point in decimal degrees to a geojson string with H3 hexagon geometry.

    Args:
        latitude_dd (float): [latitude in decimal degrees]
        longitude_dd (float): [longitude in decimal degrees]
        resolution (int, optional): [H3 resolution/ APERTURE_SIZE]. Defaults to 8.

    Returns:
        [type]: geojson string
    """    
    
    

    list_hex_res = []
    list_hex_res_geom = []

    h = h3.geo_to_h3(
        lat=latitude_dd,
        lng=longitude_dd,
        resolution = resolution
        )

    list_hex_res.append(h)
    # get the geometry of the hexagon and convert to geojson
    h_geom = {"type": "Polygon",
              "coordinates": [h3.h3_to_geo_boundary(h=h, geo_json=True)]
              }
    list_hex_res_geom.append(h_geom)

    df_res_point = pd.DataFrame({"h3_resolution": resolution,
                                 "hex_id": list_hex_res,
                                 "geometry": list_hex_res_geom
                                 })

    list_features = []


    for _, row in df_res_point.iterrows():
        feature = geojson.feature.Feature(geometry=row["geometry"],
                        id=row["hex_id"],
            properties={"resolution": int(row["h3_resolution"])})
        list_features.append(feature)

    feat_collection = geojson.feature.FeatureCollection(list_features)
    geojson_result = json.dumps(feat_collection)

    return geojson_result


@st.cache(allow_output_mutation=True)
def geodataframe_from_local_filepath(local_filepath:Path)->gpd.GeoDataFrame:
    """Returns a Geopandas GeoDataFrame

    Args:
        local_filepath (Path): [description]
    """
    assert local_filepath.exists()

    gdf = gpd.read_file(local_filepath)
    return gdf


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

    destination_filepath = os.path.join(dirpath, filename)

    gdf = None

    if Path(destination_filepath).exists():
        with st.spinner('Loading local data ... please wait'):
            gdf = geodataframe_from_local_filepath(
                local_filepath=Path(destination_filepath))
    else:
        with st.spinner("Downloading data from google drive... this may take sometime! \n Please wait ..."):
            status, local_filepath = download_file(
                data_url = DATA_URL,
                destination_filepath=destination_filepath
            )
            if status:
                gdf = geodataframe_from_local_filepath(
                    local_filepath=local_filepath)
            else:
                st.error('ERROR: Downloading status : {status}: {local_filepath}')
                
    
    return gdf  # Note gdf is None by default 

        

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


def lat_lng_to_h3(row, h3_level:int):
    """
    """
    return h3.geo_to_h3(
        row.geometry.y, row.geometry.x, h3_level)

def main():
    """
    """
    
    # APERTURE_SIZE = 7

    filename = DATA_URL_DICT[3]['name']
    DATA_URL = DATA_URL_DICT[3]['URL']
    
    gdf = load_geopandas_dataset(
        DATA_URL=DATA_URL, 
        dirpath='./data/', 
        filename=filename)

    if gdf is not None:
        #
        assert gdf.crs is not None
        assert gdf.crs != ""

        st.write(f"gdf.crs: {gdf.crs}")
        gdf = gdf.to_crs(epsg='4326').copy()
        #
        h3_level = 8.5
        gdf[f'H3_{h3_level}'] = gdf.apply(
            lambda row: h3.geo_to_h3(
                row.geometry.y, row.geometry.x, h3_level), axis=1)

        # st.write(gdf.plot())
        # lat, lng, hex resolution
        h3_address = h3.geo_to_h3(58.426172, 17.3623063, h3_level)
        hex_center_coordinates = h3.h3_to_geo(h3_address)
        hex_boundary = h3.h3_to_geo_boundary(h3_address)
        m = visualize_hexagons([h3_address])
        tooltip = "Hexagon center"
        folium.Marker(
            hex_center_coordinates, popup="Hexagon center", tooltip=tooltip
        ).add_to(m)

        # hexagons = polygonize_hexagons(gdf=gdf, APERTURE_SIZE=8, crs='EPSG:3006')

        #st.write(hexagons)
        
        # st.write(gdf[f'H3_{h3_level}'].head(20))

        # find all points that fall in the grid polygon
        counts = gdf.groupby([f'H3_{h3_level}'])[f'H3_{h3_level}'].agg(
            'count').to_frame('count').reset_index()

        # https://spatialthoughts.com/2020/07/01/point-in-polygon-h3-geopandas/
        # To visualize the results or export it to a GIS, we need to convert the H3 cell ids to a geometry.
        # The h3_to_geo_boundary function takes a H3 key and returns a list of coordinates that form the hexagonal cell.
        # Since GeoPandas uses shapely library for constructing geometries, we convert the list of coordinates 
        # to a shapely Polygon object. Note the optional second argument to the h3_to_geo_boundary function which 
        # we have set to True which returns the coordinates in the(x, y) order compared to default(lat, lon)

        def add_geometry(row):
            points = h3.h3_to_geo_boundary(
                row[f'H3_{h3_level}'], True)
            return Polygon(points)

        st.write(counts.head(20))
        counts['geometry'] = counts.apply(add_geometry, axis=1)

        counts_gdf = gpd.GeoDataFrame(counts, crs='EPSG:4326')

        # We turn the dataframe to a GeoDataframe with the CRS EPSG:4326
        # (WGS84 Latitude/Longitude) and write it to a geopackage.
        output_filename = f'./data/gridcounts_H3_{h3_level}.gpkg'
        counts_gdf.to_file(driver='GPKG', filename=output_filename)

        #hexs = h3.polyfill(
        #    gdf.geometry[0].__geo_interface__, APERTURE_SIZE, geo_json_conformant=True)

    """
  
    fig, ax = plt.subplots(figsize=(2, 4))

    geojson_result = latlong_to_geojson_string_h3_geometry(
        latitude_dd=lat_centr_point, longitude_dd=lon_centr_point, resolution=APERTURE_SIZE)

    ax = show_map(
        geojson_result=geojson_result, 
        center_location=[lat_centr_point, lon_centr_point],
        zoom_start=5.5,
        tiles="cartodbpositron")

    #ax = hexagons.plot(alpha=0.5, color="xkcd:pale yellow", figsize=(9, 9))

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

    """
    

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
