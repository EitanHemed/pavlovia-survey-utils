import warnings
from typing import List, Any

import requests
import typing
import json
import os

import pandas as pd

from . import images

SURVEYS_URL = 'https://pavlovia.org/api/v2/surveys'


def get_available_surveys_details(token: str) -> dict:
    """
    Retrieves a dictionary of the available surveys for a given token.

    :param token: The Pavlovia token.
    :return: A dictionary where keys are the survey ids and values are the survey names. Returns empty if no surveys
    are available.
    :rai
    """

    resp = requests.get('https://pavlovia.org/api/v2/surveys?accessRights=owned',
                        headers={'oauthToken': token,
                                 'Referer': 'https://pavlovia.org/dashboard?tab=0'})

    if resp.status_code == 200:
        return {i['surveyId']: i['surveyName'] for i in resp.json()['surveys']}
    else:
        resp.raise_for_status()
        # warnings.warn(f'The following HTTP error occurred: {resp.status_code}.')
        # return dict()

def get_surveys_raw(survey_ids, token: str) -> dict:
    """Return a dictionary of the available surveys for a given token"""
    if isinstance(survey_ids, str):
        survey_ids = [survey_ids]

    return {
        _id: _download_survey(_id, token) for _id in survey_ids
    }

def _download_survey(survey_id: str, token: str) -> dict:
    url = f'{SURVEYS_URL}/{survey_id}'
    req_resp = requests.get(url, headers={'oauthToken': token})

    if req_resp.status_code == 200:
        _json = req_resp.json()
        return {'survey_data': _json['survey'], 'survey_responses': _json['responses']}
    else:
        warnings.warn(f'The following HTTP error occurred: {req_resp.status_code}')
        return dict()

def get_surveys_dataframe(survey_ids, token: str) -> dict:
    """
    Gets a dict of survey dataframes for the given survey ids and token.

    :param survey_ids: A list of survey ids.
    :param token: The Pavlovia token.
    :return: A dict of survey dataframes.
    """
    if isinstance(survey_ids, str):
        survey_ids = [survey_ids]

    return {
        _id: extract_responses_from_raw_survey(get_surveys_raw(_id, token)) for _id in survey_ids
    }



def save_survey_as_directory(df, survey_name, save_images: bool=True) -> None:
    image_columns = images.find_image_columns(df)

    save_csv(df.drop(image_columns, axis=1), survey_name)

    if save_images and len(image_columns):
        images.save_image_columns(df, survey_name, image_columns)


def save_survey_as_json(survey_id: str, token: str, survey_name: str) -> None:
    data = _download_survey(survey_id, token)

    with open(f'output/raw/json/{survey_name}.json',
              'w', encoding='utf-8') as f:
        json.dump(data, f)


def extract_responses_from_raw_survey(raw_survey: typing.Dict):
    metadata = raw_survey['survey_data']
    responses = raw_survey['survey_responses']

    responses = pd.DataFrame(raw_survey['survey_responses'])
    responses['_survey_name'] = metadata['surveyName']
    responses['_survey_id'] = metadata['surveyId']
    return responses


def save_csv(df, survey_name):
    pth = f'output/processed/{survey_name}'
    os.makedirs(pth, exist_ok=True)
    df.to_csv(f'output/processed/{survey_name}/{survey_name}.csv',
              encoding='utf-8-sig', index=False)
