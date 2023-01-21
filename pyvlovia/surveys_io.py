import pathlib
import warnings
import requests
import typing
import json
import os

import pandas as pd

from . import file_utils

SURVEYS_URL = 'https://pavlovia.org/api/v2/surveys'

__all__ = ['load_available_surveys', 'download_surveys', 'get_surveys_dataframe', 'get_surveys_raw']


def download_surveys(token: str, survey_ids: str | typing.Sequence[str] | None = None,
                     root: typing.Union[str, pathlib.Path] = '.'):
    abs_root = os.path.abspath(root)

    if survey_ids is None:
        survey_ids = list(load_available_surveys(token).keys())

    surveys_dfs = get_surveys_dataframe(survey_ids, token)

    for _id in surveys_dfs.keys():
        _save_survey_as_directory(
            surveys_dfs[_id], surveys_dfs[_id]['_survey_name'].iloc[0],
            root=abs_root
        )


def load_available_surveys(token: str) -> dict:
    """
    Retrieves a dictionary of the available surveys for a given token.

    :param token: The Pavlovia token.
    :return: A dictionary where keys are the survey ids and values are the survey names. Returns empty if no surveys
    are available.

    """

    # TODO - see how we can query for surveys which are not owned, but shared.
    resp = requests.get('https://pavlovia.org/api/v2/surveys?accessRights=owned',
                        headers={'oauthToken': token,
                                 'Referer': 'https://pavlovia.org/dashboard?tab=0'})

    if resp.status_code == 200:
        return {i['surveyId']: i['surveyName'] for i in resp.json()['surveys']}
    else:
        resp.raise_for_status()
        # warnings.warn(f'The following HTTP error occurred: {resp.status_code}.')
        # return dict()


def get_surveys_dataframe(survey_ids: str | typing.Sequence[str], token: str) -> dict:
    """
    Gets a dict of survey dataframes for the given survey ids and token.

    :param survey_ids: A list of survey ids.
    :param token: The Pavlovia token.
    :return: A dict of survey dataframes.
    """
    if isinstance(survey_ids, str):
        survey_ids = [survey_ids]

    raw_surveys = get_surveys_raw(survey_ids, token)

    return {_id: extract_responses_from_raw_survey(raw_surveys[_id]) for _id in survey_ids}


def get_surveys_raw(survey_ids: str | typing.Sequence[str], token: str) -> dict:
    """

    :param survey_ids:
    :param token:
    :return:
    """
    if isinstance(survey_ids, str):
        survey_ids = [survey_ids]

    return {_id: _download_survey(_id, token) for _id in survey_ids}


def _save_survey_as_directory(df: pd.DataFrame, survey_name: str,
                              root: typing.Union[str, pathlib.Path] = '.',
                              save_images: bool = True, ) -> None:
    image_columns = file_utils.find_image_columns(df)

    _save_csv(df.drop(image_columns, axis=1), survey_name, root)

    if save_images and len(image_columns):
        file_utils.save_image_columns(df, survey_name, image_columns, root)


def _download_survey(survey_id: str, token: str) -> dict:
    url = f'{SURVEYS_URL}/{survey_id}'
    req_resp = requests.get(url, headers={'oauthToken': token})

    if req_resp.status_code == 200:
        _json = req_resp.json()
        return {'survey_data': _json['survey'], 'survey_responses': _json['responses']}
    else:
        warnings.warn(f'The following HTTP error occurred: {req_resp.status_code}')
        return dict()


def _save_survey_as_json(survey_id: str, token: str, survey_name: str) -> None:
    data = _download_survey(survey_id, token)

    with open(os.path.join('output', 'raw', 'json', f'{survey_name}.json'),
              'w', encoding='utf-8') as f:
        json.dump(data, f)


def extract_responses_from_raw_survey(raw_survey: dict) -> pd.DataFrame:
    meta_data = pd.DataFrame(raw_survey['survey_data'])
    data = pd.DataFrame(raw_survey['survey_responses']) # pd.DataFrame(meta_data['surveyResponse'].values.tolist())
    meta_data = meta_data.drop(['surveyResponse', 'participant'], axis=1)
    df = pd.concat([meta_data, data], axis=1)
    return df.loc[:, ~df.columns.duplicated()].copy()
    # metadata = raw_survey['survey_data']
    # responses = pd.DataFrame(raw_survey['survey_responses'])
    # responses['_survey_name'] = metadata['surveyName']
    # print(metadata.keys())
    # return responses


def _save_csv(df: pd.DataFrame, survey_name: str, root: typing.Union[str, pathlib.Path] = '.') -> None:
    pth = os.path.join(root, 'output', 'processed', survey_name)
    os.makedirs(pth, exist_ok=True)
    df.to_csv(os.path.join(pth, f'{survey_name}.csv'),
              encoding='utf-8-sig', index=False)
