import requests
import typing
import json
import os

import pandas as pd

from . import images

SURVEYS_URL = 'https://pavlovia.org/api/v2/surveys'


def get_available_surveys(token):
    resp = requests.get('https://pavlovia.org/api/v2/surveys?accessRights=owned',
                        headers={'oauthToken': token,
                                 'Referer': 'https://pavlovia.org/dashboard?tab=0'})

    if resp.status_code == 200:
        return [(i['surveyId'], i['surveyName']) for i in resp.json()['surveys']]


def get_surveys(token: str, save_json_output: bool = True):
    pass


def download_survey_data(survey_id: str, token: str) -> typing.Dict:
    url = f'{SURVEYS_URL}/{survey_id}'
    req_resp = requests.get(url, headers={'oauthToken': token})

    if req_resp.status_code == 400:
        raise RuntimeError("Bed request")

    survey_responses = req_resp.json()['responses']

    if len(survey_responses) == 0:
        raise ValueError

    return survey_responses


def get_json(survey_name, survey_id, token, save_json=True) -> None:
    data = download_survey_data(survey_id, token)

    if save_json:
        with open(f'output/raw/json/{survey_name}.json',
                  'w', encoding='utf-8') as f:
            json.dump(data, f)

    return data


def extract_survey_from_dict(src: typing.Dict):
    meta_data = pd.DataFrame(src)
    data = pd.DataFrame(meta_data['surveyResponse'].values.tolist())
    meta_data = meta_data.drop(['surveyResponse', 'participant'], axis=1)
    df = pd.concat([meta_data, data], axis=1)
    return df.loc[:, ~df.columns.duplicated()].copy()


def save_csv(df, survey_name):
    pth = f'output/processed/{survey_name}'
    os.makedirs(pth, exist_ok=True)
    df.to_csv(f'output/processed/{survey_name}/{survey_name}.csv',
              encoding='utf-8-sig', index=False)


def process_survey_df(df, survey_name):

    image_columns = images.find_image_columns(df)

    save_csv(df.drop(image_columns, axis=1), survey_name)

    if len(image_columns):
        images.save_image_columns(df, survey_name, image_columns)



