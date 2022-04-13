from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pystac import (Extent, Link, MediaType, Provider, ProviderRole,
                    SpatialExtent, Summaries, TemporalExtent)
from pystac.extensions.item_assets import AssetDefinition

# --Item--
ITEM_DESCRIPTION = "ESA WorldCover product at 10m resolution for year 2020"
# Per the discussion in https://github.com/radiantearth/stac-spec/issues/216,
# the recommendation for multi-platform datasets is to include all platforms
# and use a string seperator. The same logic is applied to the mission.
MISSION = "Sentinel-1, Sentinel-2"
PLATFORM = "Sentinel-1A, Sentinel-1B, Sentinel-2A, Sentinel-2B"
INSTRUMENTS = ["C-SAR", "MSI"]
EPSG = 4326
START_TIME: Optional[datetime] = datetime(2020,
                                          1,
                                          1,
                                          0,
                                          0,
                                          0,
                                          tzinfo=timezone.utc)
END_TIME: Optional[datetime] = datetime(2020,
                                        12,
                                        31,
                                        23,
                                        59,
                                        59,
                                        tzinfo=timezone.utc)
CLASSIFICATION_SCHEMA = "https://stac-extensions.github.io/classification/v1.0.0/schema.json"

# --Map Asset--
MAP_TITLE = "Land Cover Classes"
MAP_DESCRIPTION = (
    "Discrete classification according to the Land Cover Classification System "
    "scheme developed by the United Nations Food and Agriculture Organization")
MAP_ROLES = ["data"]
MAP_RASTER: List[Dict[str, Any]] = [{
    "name": "Band1",
    "description": "Classification values",
    "nodata": 0,
    "sampling": "area",
    "data_type": "uint8",
    "spatial_resolution": 10
}]
MAP_CLASSES = [{
    "value": 10,
    "description": "Tree cover",
    "color-hint": "006400"
}, {
    "value": 20,
    "description": "Shrubland",
    "color-hint": "FFBB22"
}, {
    "value": 30,
    "description": "Grassland",
    "color-hint": "FFFF4C"
}, {
    "value": 40,
    "description": "Cropland",
    "color-hint": "F096FF"
}, {
    "value": 50,
    "description": "Built-up",
    "color-hint": "FA0000"
}, {
    "value": 60,
    "description": "Bare / sparse vegetation",
    "color-hint": "B4B4B4"
}, {
    "value": 70,
    "description": "Snow and ice",
    "color-hint": "F0F0F0"
}, {
    "value": 80,
    "description": "Permanent water bodies",
    "color-hint": "0064C8"
}, {
    "value": 90,
    "description": "Herbaceous wetland",
    "color-hint": "0096A0"
}, {
    "value": 95,
    "description": "Mangroves",
    "color-hint": "00CF75"
}, {
    "value": 100,
    "description": "Moss and lichen",
    "color-hint": "FAE6A0"
}]

# --Quality Input Asset--
QUALITY_TITLE = "Classification Input Data Quality"
QUALITY_DESCRIPTION = (
    "Per pixel quality indicator showing the quality of the electro-optical input data."
)
QUALITY_ROLES = ["metadata"]
QUALITY_RASTER: List[Dict[str, Any]] = [
    {
        "name": "Band1",
        "description":
        "Number of Sentinel-1 GAMMA0 observations used in the classification workflow",
        "nodata": -1,
        "sampling": "area",
        "data_type": "int16",
        "spatial_resolution": 60
    },
    {
        "name": "Band2",
        "description":
        "Number of Sentinel-2 L2A observations used in the classification workflow",
        "nodata": -1,
        "sampling": "area",
        "data_type": "int16",
        "spatial_resolution": 60
    },
    {
        "name": "Band3",
        "description":
        "Percentage (0-100) of invalid S2 observations discarded in the classification workflow (after cloud and cloud shadow filtering)",  # noqa
        "nodata": -1,
        "sampling": "area",
        "data_type": "int16",
        "spatial_resolution": 60
    }
]
QUALITY_SHAPE = [6000, 6000]
QUAlITY_SCALE = 0.0005

# --Collection--
COLLECTION_TITLE = "ESA WorldCover 2020"
COLLECTION_DESCRIPTION = (
    "Global land cover product at 10 meter resolution for 2020 based on "
    "Sentinel-1 and Sentinel-2 data")
PRODUCT_VERSION = "V1.0.0"
LICENSE = "CC-BY-4.0"
LICENSE_LINK = Link(
    rel="license",
    target="https://spdx.org/licenses/CC-BY-4.0.html",
    title="Creative Commons Attribution 4.0 International License")
DATA_DOI = "10.5281/zenodo.5571936"
DATA_CITATION = (
    "Zanaga, D., Van De Kerchove, R., De Keersmaecker, W., Souverijns, N., "
    "Brockmann, C., Quast, R., Wevers, J., Grosu, A., Paccini, A., Vergnaud, "
    "S., Cartus, O., Santoro, M., Fritz, S., Georgieva, I., Lesiv, M., Carter, "
    "S., Herold, M., Li, Linlin, Tsendbazar, N.E., Ramoino, F., Arino, O., "
    "2021. ESA WorldCover 10m 2020 v100. https://doi.org/10.5281/zenodo.5571936"
)
KEYWORDS = ["Global", "Land Cover", "Sentinel", "ESA"]
PROVIDERS = [
    Provider(
        name="ESA WorldCover Consortium",
        description=(
            "The WorldCover product is developed by a consortium led by "
            "VITO Remote Sensing together with partners Brockmann Consult, "
            "CS SI, Gamma Remote Sensing AG, IIASA and Wageningen "
            "University"),
        roles=[ProviderRole.PROCESSOR],
        url="https://worldcover2020.esa.int/"),
    Provider(name="ESA",
             roles=[
                 ProviderRole.LICENSOR, ProviderRole.PRODUCER,
                 ProviderRole.HOST
             ],
             url="https://esa-worldcover.org/en")
]
EXTENT = Extent(SpatialExtent([[-180.0, -60.0, 180.0, 82.75]]),
                TemporalExtent([[START_TIME, END_TIME]]))
SUMMARIES = Summaries({
    "platform": PLATFORM.split(", "),
    "instruments": INSTRUMENTS,
    "mission": MISSION.split(", ")
})
ITEM_ASSETS = {
    "map":
    AssetDefinition({
        "type": MediaType.COG,
        "title": MAP_TITLE,
        "description": MAP_DESCRIPTION,
        "classification:classes": MAP_CLASSES,
        "raster:bands": MAP_RASTER,
        "roles": MAP_ROLES
    }),
    "input_quality":
    AssetDefinition({
        "type": MediaType.COG,
        "title": QUALITY_TITLE,
        "description": QUALITY_DESCRIPTION,
        "raster:bands": QUALITY_RASTER,
        "roles": QUALITY_ROLES
    })
}
USER_LINK = Link(
    rel="manual",
    target=  # noqa
    "https://esa-worldcover.s3.amazonaws.com/v100/2020/docs/WorldCover_PUM_V1.0.pdf",
    title="Product User Manual")
VALIDATION_LINK = Link(
    rel="validation",
    target="https://worldcover2020.esa.int/data/docs/WorldCover_PVR_V1.1.pdf",
    title="Product Validation Report")
