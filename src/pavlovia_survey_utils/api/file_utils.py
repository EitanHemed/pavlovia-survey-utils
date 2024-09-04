
import base64
import os
import pathlib
import typing

import pandas as pd


def process_image(image_str: str, pth: str | pathlib.Path) -> None:
    """
    Process an image string and save it to a file.

    :param image_str: The image string.
    :param pth: The path to save the image to.
    :return: None
    """
    image_format, image_data = read_base64_image_str(image_str)
    save_base64_image(pth, image_format, image_data)


def find_image_columns(df: pd.DataFrame) -> typing.List:
    """Find image columns in a dataframe.

    :param df: The dataframe to search for image columns.
    :return: List of image columns.
    """
    str_cols = df.columns[(df.map(type) == str).all(axis='index')]
    return str_cols[
        df[str_cols].apply(lambda s: s.str.startswith('data:image')).any(axis='index').values].tolist()


def read_base64_image_str(image_string: str) -> typing.Tuple[str, bytes]:
    """
    Read a base64 image string and return the image format and image data.
    :param image_string:
    :return: Tuple of image format and image data.
    """
    image_format = image_string.split(';')[0].split('/')[1]
    image_data = base64.decodebytes(
        bytes(image_string.split('base64,')[1], "utf-8"))
    return image_format, image_data


def save_base64_image(fname: str | pathlib.Path, image_format: str, image_data: bytes) -> None:
    """
    Save a base64 image to a file.
    :param fname: Name of the file to save the image to.
    :param image_format: Format of the image.
    :param image_data: Image data.
    :return: None
    """
    with open(f"{fname}.{image_format}", "wb") as fh:
        fh.write(image_data)


def save_image_columns(df: pd.DataFrame, survey_name: str, root: str | pathlib.Path = '.',
                       grouper: str = 'sessionToken') -> None:
    """
    Save image columns from a dataframe to a directory.
    :param df: The dataframe containing the image columns as base64 strings.
    :param survey_name: Name of the survey.
    :param root: Root directory to save the images to.
    :param grouper: The column to group the images by.
    :return:
    """
    image_columns = find_image_columns(df)

    if len(image_columns):
        grouped = df.groupby(grouper)

        for n, g in grouped:
            for i in image_columns:
                pth = os.path.join(os.path.abspath(root),
                                   'pavlovia-survey-utils', survey_name, 'images', i)
                os.makedirs(pth, exist_ok=True)
                process_image(g[i].values[0],
                              os.path.join(pth, n))
