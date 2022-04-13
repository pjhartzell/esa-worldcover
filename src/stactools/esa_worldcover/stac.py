import logging
import os
from datetime import datetime, timezone
from typing import Optional

import rasterio
import shapely
from pystac import Asset, Collection, Item, MediaType
from pystac.extensions.item_assets import ItemAssetsExtension
from pystac.extensions.projection import (AssetProjectionExtension,
                                          ItemProjectionExtension)
from pystac.extensions.raster import RasterExtension
from pystac.extensions.scientific import ScientificExtension
from pystac.utils import make_absolute_href, str_to_datetime
from stactools.core.io import ReadHrefModifier

from stactools.esa_worldcover import constants

logger = logging.getLogger(__name__)


def create_item(map_href: str,
                read_href_modifier: Optional[ReadHrefModifier] = None) -> Item:
    """Create a STAC Item for a 3x3 degree COG tile of the ESA 10m WorldCover
    classification product.

    Expects an input quality COG to exist alongside the classificaton map COG.

    Args:
        map_href (str): An href to a COG containing a tile of classication data.
        read_href_modifier (Callable[[str], str]): An optional function to
            modify the MTL and USGS STAC hrefs (e.g. to add a token to a url).
    Returns:
        Item: STAC Item object representing the worldcover tile
    """
    base_href = "_".join(map_href.split('_')[:-1])
    qua_href = f"{base_href}_InputQuality.tif"

    if read_href_modifier:
        modified_map_href = read_href_modifier(map_href)
    else:
        modified_map_href = map_href
    with rasterio.open(modified_map_href) as dataset:
        bbox = dataset.bounds
        map_transform = list(dataset.transform)[0:6]
        map_shape = dataset.shape
        map_tags = dataset.tags()

    # --Item--
    geometry = shapely.geometry.mapping(shapely.geometry.box(*bbox))

    item = Item(id=os.path.basename(base_href).lower(),
                geometry=geometry,
                bbox=bbox,
                datetime=constants.START_TIME,
                properties={})
    item.common_metadata.description = constants.ITEM_DESCRIPTION
    item.common_metadata.created = datetime.now(tz=timezone.utc)
    item.common_metadata.mission = constants.MISSION
    item.common_metadata.platform = constants.PLATFORM
    item.common_metadata.instruments = constants.INSTRUMENTS
    item.common_metadata.start_datetime = constants.START_TIME
    item.common_metadata.end_datetime = constants.END_TIME
    item.properties["esa_worldcover:product_tile"] = map_tags["product_tile"]

    item_proj = ItemProjectionExtension.ext(item, add_if_missing=True)
    item_proj.epsg = constants.EPSG

    # --Map asset--
    map_asset = Asset(href=make_absolute_href(map_href))
    map_asset.roles = constants.MAP_ROLES
    map_asset.title = constants.MAP_TITLE
    map_asset.description = constants.MAP_DESCRIPTION
    map_asset.media_type = MediaType.COG

    map_asset.extra_fields = {
        "raster:bands": constants.MAP_RASTER,
        "classification:classes": constants.MAP_CLASSES
    }
    RasterExtension.add_to(item)
    item.stac_extensions.append(constants.CLASSIFICATION_SCHEMA)

    map_proj = AssetProjectionExtension.ext(map_asset)
    map_proj.transform = map_transform
    map_proj.shape = map_shape

    map_asset.common_metadata.created = str_to_datetime(
        map_tags["creation_time"])

    item.add_asset('map', map_asset)

    # --Input quality asset--
    qua_asset = Asset(href=make_absolute_href(qua_href))
    qua_asset.roles = constants.QUALITY_ROLES
    qua_asset.title = constants.QUALITY_TITLE
    qua_asset.description = constants.QUALITY_DESCRIPTION
    qua_asset.media_type = MediaType.COG

    qua_asset.extra_fields = {"raster:bands": constants.QUALITY_RASTER}

    qua_proj = AssetProjectionExtension.ext(qua_asset)
    map_transform[0] = constants.QUAlITY_SCALE
    map_transform[4] = constants.QUAlITY_SCALE
    qua_proj.transform = map_transform
    qua_proj.shape = constants.QUALITY_SHAPE

    item.add_asset('input_quality', qua_asset)

    item.validate()

    return item


def create_collection(collection_id: str) -> Collection:
    """Creates a STAC Collection for the 2020 ESA 10m WorldCover classification
    product.

    Args:
        collection_id (str): Desired ID for the STAC Collection.
    Returns:
        Collection: The created STAC Collection.
    """
    collection = Collection(id=collection_id,
                            title=constants.COLLECTION_TITLE,
                            description=constants.COLLECTION_DESCRIPTION,
                            license=constants.LICENSE,
                            keywords=constants.KEYWORDS,
                            providers=constants.PROVIDERS,
                            extent=constants.EXTENT,
                            summaries=constants.SUMMARIES,
                            extra_fields={
                                "esa_worldcover:product_version":
                                constants.PRODUCT_VERSION
                            })

    scientific = ScientificExtension.ext(collection, add_if_missing=True)
    scientific.doi = constants.DATA_DOI
    scientific.citation = constants.DATA_CITATION

    item_assets = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_assets.item_assets = constants.ITEM_ASSETS

    RasterExtension.add_to(collection)
    collection.stac_extensions.append(constants.CLASSIFICATION_SCHEMA)

    collection.add_links([
        constants.LICENSE_LINK, constants.USER_LINK, constants.VALIDATION_LINK
    ])

    return collection
