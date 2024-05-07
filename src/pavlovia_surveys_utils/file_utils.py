import base64
import typing
import os

# TODO - support non-image files

def process_image(s, pth):
    image_format, image_data = read_base64_img(s)
    save_base64_image(pth, image_format, image_data)


def find_image_columns(df) -> typing.List:
    str_cols = df.columns[(df.applymap(type) == str).all(axis='index')]

    return str_cols[
        df[str_cols].apply(lambda s: s.str.startswith('data:image')).any(axis='index').values]


def read_base64_img(image_string):
    image_format = image_string.split(';')[0].split('/')[1]
    image_data = base64.decodebytes(
        bytes(image_string.split('base64,')[1], "utf-8"))
    return image_format, image_data


def save_base64_image(fname, iamge_format, image_data):
    with open(f"{fname}.{iamge_format}", "wb") as fh:
        fh.write(image_data)

def save_image_columns(df, survey_name, root='.', grouper='sessionToken'):
    image_columns = find_image_columns(df)

    if len(image_columns):
        grouped = df.groupby(grouper)

        for n, g in grouped:
            for i in image_columns:
                pth = os.path.join(root, 'pyvlovia_output', survey_name, 'images', i)
                os.makedirs(pth, exist_ok=True)
                process_image(g[i].values[0],
                              os.path.join(pth, n))