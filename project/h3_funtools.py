from shapely.geometry import Polygon
import geopandas as gpd
from h3 import h3
import folium

import streamlit as st

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
    for _hex in hexagons:
        polygons = h3.h3_set_to_multi_polygon([_hex], geo_json=False)
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


def build_hexs(gdf: gpd.GeoDataFrame, APERTURE_SIZE: int = 8):
    """
    source: https://geographicdata.science/book/data/h3_grid/build_sd_h3_grid.html
    """
    hexs = h3.polyfill(
        gdf.geometry[0].__geo_interface__, APERTURE_SIZE, geo_json_conformant=True)
    return hexs


def gdf_to_h3_geojson(gdf: gpd.GeoDataFrame):

    assert gdf.crs is not None
    assert gdf.crs != ""

    st.write(f"gdf.crs: {gdf.crs}")
    df = gdf.to_crs(epsg='4326')
    #  this is a string
    js = df.to_json()

    return js


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

    hexs = h3.polyfill(GeoJSON_polygon, APERTURE_SIZE,
                       geo_json_conformant=True)

    all_polys = gpd.GeoSeries(list(map(polygonise, hexs)),
                              index=hexs,
                              crs=crs
                              )
    return all_polys


def show_map(
    geojson_result,
    center_location: list,
    zoom_start: float = 5.5,
    tiles: str = "cartodbpositron",
    attr: str = '''© <a href="http://www.openstreetmap.org/copyright">
                          OpenStreetMap</a>contributors ©
                          <a href="http://cartodb.com/attributions#basemaps">
                          CartoDB</a>'''
):
    """[summary]

    Args:
        center_location (List): [description]
        zoom_start (float, optional): [description]. Defaults to 5.5.
        tiles (str, optional): [description]. Defaults to "cartodbpositron".
        attr (str, optional): [description]. Defaults to '''© <a href="http://www.openstreetmap.org/copyright"> OpenStreetMap</a>contributors © <a href="http://cartodb.com/attributions#basemaps"> CartoDB</a>'''.

    Returns:
        [type]: [description]
    """

    st.write(geojson_result)

    fmap = folium.Map(location=center_location,
                      zoom_start=zoom_start,
                      tiles=tiles,
                      attr=attr
                      )

    folium.GeoJson(
        geojson_result,
        style_function=lambda feature: {
            'fillColor': None,
            'color': ("green"),
            'weight': 1,
            'fillOpacity': 0.05
        },
        name="Marin Medvind"
    ).add_to(fmap)

    return fmap
