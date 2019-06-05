from django import template
from django.utils.safestring import mark_safe

from simple_webpack.utils import (
    get_bundle_path_by_chunkname,
    get_bundle_path_by_filename,
)

register = template.Library()


@register.simple_tag
def simple_webpack_bundle(chunk_name='main'):
    """Load a bundle's URL path by chunk/entry name.

    Load a bundle by chunk name. The default name for a single chunk
    is "main".

    Args:
        chunk_name (str): The chunk name of your bundle.
            Defaults to "main".

    Returns:
        str: The URL path of the bundle "chunk_name".

    """
    if not isinstance(chunk_name, str):
        raise ValueError('chunk_name must be a str.')
    bundle_path = get_bundle_path_by_chunkname(chunk_name)
    return bundle_path


@register.simple_tag
def simple_webpack_static(bundle_filename):
    """Load a bundle's URL path by filename.

    Args:
        bundle_filename (str): The filename, with its extension, of
            a bundle.

    Returns:
        str: The URL path of the bundle "bundle_filename".

    """
    if not isinstance(bundle_filename, str):
        raise ValueError('bundle_filename must be a str.')
    bundle_path = get_bundle_path_by_filename(bundle_filename)
    return bundle_path


@register.simple_tag
def simple_webpack_tags(*exclude):
    """Load all bundles as tags.

    Args:
        *exclude (str): The chunk name of the bundle to be excluded.

    Returns:
        str: Script and link tags for all bundles.

    """
    if len(exclude) > 0 and not all([isinstance(i, str) for i in exclude]):
        raise ValueError('*exclude must be a str.')


    bundle_path = get_bundle_path(entry_name)
    return bundle_path
