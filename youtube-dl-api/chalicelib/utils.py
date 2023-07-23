#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gzip
import simplejson as json
import base64
from typing import Any, Union


def json_to_base64_gzip_compressed(data: Any) -> str:
    """
    Converts the input Python object to JSON, compresses it using gzip, and encodes it using base64.

    Parameters:
    data (Any): The input Python object to be compressed.

    Returns:
    str: The base64 encoded string of the compressed JSON representation of the input object.
    """
    json_data = json.dumps(data, iterable_as_array=True).encode('utf-8')
    return base64.b64encode(gzip.compress(json_data)).decode('utf-8')


def base64_gzip_compressed_to_json(data: str) -> Union[dict, list]:
    """
    Decodes the base64 input, decompresses it using gzip, and converts it back to a Python object (dict or list).

    Parameters:
    data (str): The base64 encoded string of the compressed JSON representation of the input object.

    Returns:
    Union[dict, list]: The decompressed Python object (dict or list) from the compressed JSON representation.
    """
    decompressed_data = gzip.decompress(base64.b64decode(data.encode('utf-8')))
    return json.loads(decompressed_data.decode('utf-8'))
