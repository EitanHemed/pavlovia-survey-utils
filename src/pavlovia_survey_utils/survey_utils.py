import json
import os
import pathlib
import typing
import warnings

import pandas as pd
import requests

from . import file_utils

COLUMN_NAME_SURVEY_NAME = 'surveyName'

COLUMN_NAME_SURVEY_RESPONSE = 'surveyResponse'

SURVEYS_URL = 'https://pavlovia.org/api/v2/surveys'

__all__ = ['load_available_surveys', 'download_surveys', 'get_surveys_dataframe', 'get_surveys_raw',
           'download_surveys_as_json']


def download_surveys(token: str, survey_ids: str | typing.Sequence[str] | None = None,
                     root: typing.Union[str, pathlib.Path] = '.'):
    abs_root = os.path.abspath(root)

    if survey_ids is None:
        survey_ids = list(load_available_surveys(token).keys())

    surveys_dfs = get_surveys_dataframe(survey_ids, token)

    for _id in surveys_dfs.keys():
        if not surveys_dfs[_id].empty:
            _save_survey_as_directory(
                surveys_dfs[_id], surveys_dfs[_id]['surveyName'].iloc[0],
                root=abs_root
            )
        else:
            warnings.warn(f"No data found for survey {_id}.")


def download_surveys_as_json(survey_id: str, token: str, survey_name: str, root='.') -> None:
    data = _download_survey(survey_id, token)

    _root = os.path.abspath(root)

    os.makedirs(os.path.join(_root, 'pyvlovia_output', survey_name), exist_ok=True)

    with open(os.path.join(_root, 'pyvlovia_output', survey_name, f'raw.json'),
              'w', encoding='utf-8') as f:
        json.dump(data, f)


def load_available_surveys(token: str, access_rights: str = 'both') -> dict:
    """
    Return available surveys for a given token, as a dictionary where keys are the survey ids and values are the survey
    names.

    :param token (str): The Pavlovia token.
    :param access_rights (str): The access rights to the surveys. Can be 'owned', 'shared', or 'both'.
    :return: dict: A dictionary where keys are the survey ids and values are the survey names. Returns empty if no surveys
    are available.

    """
    if access_rights == 'both':
        _access_rights = 'owned, shared'
    else:
        if access_rights not in ['owned', 'shared']:
            raise ValueError(f"Invalid access rights: {access_rights}.")

    # TODO - see how we can query for surveys which are not owned, but shared.
    resp = requests.get(f'https://pavlovia.org/api/v2/surveys?accessRights={_access_rights}',
                        headers={'oauthToken': token,
                                 'Referer': 'https://pavlovia.org/dashboard?tab=0'})

    if resp.status_code == 200:
        return {i['surveyId']: i['surveyName'] for i in resp.json()['surveys']}
    else:
        resp.raise_for_status()


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

    return {_id: extract_dataframes_from_raw_survey(raw_surveys[_id]) for _id in survey_ids}


def get_surveys_raw(survey_ids: str | typing.Sequence[str], token: str) -> dict:
    """
    Gets a dict of raw survey data for the given survey ids and token.

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
    """
    Saves the survey data as a directory containing a csv file and possibly images.

    :param df (pd.DataFrame): A DataFrame containing the survey data.
    :param survey_name (str): The name of the survey.
    :param root: (str, pathlib.Path): The root directory to save the survey data.
    :param save_images (bool): Whether to save images or not. Default is True.
    :return: None
    """
    image_columns = file_utils.find_image_columns(df)

    _save_csv(df.drop(image_columns, axis=1), survey_name, root)

    if save_images and len(image_columns):
        file_utils.save_image_columns(df, survey_name, root=root)


def _download_survey(survey_id: str, token: str) -> dict:
    """
    Downloads a survey from Pavlovia.
    :param survey_id: The survey id (e.g., "1fe6f860-7fad-4924-ac63-84d6be4a8fcb").
    :param token: The Pavlovia token.
    :return: dict: The survey data.
    """
    url = f'{SURVEYS_URL}/{survey_id}'
    req_resp = requests.get(url, headers={'oauthToken': token})

    if req_resp.status_code == 200:
        _json = req_resp.json()
        return {'survey_data': _json['survey'], 'survey_responses': _json['responses']}
    else:
        warnings.warn(f'The following HTTP error occurred: {req_resp.status_code}')
        return dict()


def extract_dataframes_from_raw_survey(raw_survey: dict) -> pd.DataFrame:
    """
    Extracts the survey dataframes from the raw survey data (json).

    :param raw_survey: The raw survey data as a dictionary.
    :return: pd.DataFrame: The extracted survey data as a DataFrame.
    """
    _meta_data = pd.DataFrame(raw_survey['survey_responses'])

    if COLUMN_NAME_SURVEY_RESPONSE not in _meta_data.columns:
        # Warn about no records
        warnings.warn(
            f"No survey responses found for survey {raw_survey['survey_data'][COLUMN_NAME_SURVEY_NAME]}.")

        _meta_data[COLUMN_NAME_SURVEY_RESPONSE] = [dict() for _ in range(len(_meta_data))]

    _responses = pd.DataFrame(_meta_data[COLUMN_NAME_SURVEY_RESPONSE].values.tolist())
    _meta_data = _meta_data.drop(COLUMN_NAME_SURVEY_RESPONSE, axis=1)
    df = pd.concat([_meta_data, _responses], axis=1)
    df[COLUMN_NAME_SURVEY_NAME] = raw_survey['survey_data'][COLUMN_NAME_SURVEY_NAME]
    return df.loc[:, ~df.columns.duplicated()]

def _save_csv(df: pd.DataFrame, survey_name: str,
              root: typing.Union[str, pathlib.Path] = './pavlovia-surveys-output') -> None:
    """"
    Save the survey data as a csv file.

    :param df (pd.Dataframe): The survey data as a DataFrame.
    :param survey_name (str): The name of the survey.
    :param root (str, pathlib.Path): The root directory to save the survey data.
    :return: None
    """
    pth = os.path.abspath(root)
    os.makedirs(pth, exist_ok=True)
    df.to_csv(os.path.join(pth, f'{survey_name}.csv'), encoding='utf-8-sig', index=False)
