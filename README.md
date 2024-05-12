# pavlovia_survey_utils

`pavlovia_survey_utils` is a Python library for data retrieval from
[Pavlovia](https://pavlovia.org) surveys. It can be used to receive either the raw JSON format
data, or save a tidy version of the data, including downloading of images (e.g., signatures)
uploaded or created by your survey participants.

The main motivation is to automate the process of data retrieval from Pavlovia surveys. This is handy when you
either have a large number of surveys to download, or when you want to download the data regularly (e.g., after
running a cohort of participants on Prolific), and automatically calculate their bonus payments.


#### Disclaimer: This library is not affiliated with Pavlovia, and is not an official Pavlovia product. 

---
## See also In this README:

- [Setup](#Setup)
- [Usage](#Usage)
- [FAQ](#FAQ)
- [Contributing](#Contributing)

## Setup

`pip install git+https://github.com/EitanHemed/pavlovia_survey_utils.git`


For development purposes, clone the repository and install the package in editable mode:

```
pip install -e .[dev]
```

TODO - update the uasge section

## Usage

First:
`import pavlovia_survey_utils as psu`

Then, there are two main steps - (1) Accessing Pavlovia and (2) Data Retrieval

1. Accessing Pavlovia:

   You will need your access token to Pavlovia. From here you can choose to store it permanently in a local cache
   (more recommended), or generate it every time you use `pavlovia_survey_utils`. You can remove the cache of tokens at
   any time.

    * Permanent storage:
      Call `psu.add_user_to_cache(username, password)`. You can add as many users as you wish, at any stage.
        * Now the token is available using `psu.load_token_for_user('username')`, even in future sessions.
        * To view the stored users, call `psu.load_available_users()`.
        * To remove a specific user (or all users) from the local cache, call
          `psu.remove_user_from_cache('username')` (or `psu.purge_cache()`) respectively.

    * To use it in the current session only,
      call `psu.auth.get_pavlovia_access_token('my_username', 'my_password')`.

2. Data Retrieval

Now you can retrieve data from Pavlovia, either interactively, or in an automated script. There are several ways
to go about it.

* View the survey ids and names of all surveys available for a specific user:
   ```
   print(psu.load_available_surveys(token))
   # {'058b1326-70d2-9259-4f53-75477adf1871': 'MY SURVEY NAME'}
   ```

* Download and save survey(s) responses (including images and drawings):
   ```
   # To download a single survey
   target = '058b1326-70d2-9259-4f53-75477adf1871'
   # To download multiple surveys
   target = ['058b1326-70d2-9259-4f53-75477adf1871', '058b1326-70d2-9259-4f53-75477adf1872']
   # To downoload all surveys available for the given token
   target = None

   # If download_path is not specified, all data will be saved in new directories under the current directory
   psu.download_surveys(target, token, download_path) 
   ```

* Load survey(s) responses as a dictionary of dataframe:
   ```
   # A single survey
   psu.get_surveys_dataframe(survey_id, token)

   # Multuple surveys
   psu.get_surveys_dataframe(
       [survey_id1, survey_id2], token)
   ```

* Load survey(s) responses as a dictionary, where each entry is a dictionary containing the survey
  metadata and responses of a single survey:

   ```
   psu.get_surveys_raw(
       [survey_id1, survey_id2], token)
   ```

## FAQ

#### What permissions does `pavlovia_survey_utils` require?

_pavlovia_survey_utils generates an access token on gitlab with a `read-user` scope. See
[here](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#personal-access-token-scopes)
for details._

#### Where is my access token stored?

_Similarly to PsychoPy, your username and access token are stored in the AppData directory, on your computer (e.g.,
`C:\Users\User\AppData\Roaming\pavlovia_survey_utils` on Windows, `HOME/pavlovia_survey_utils` on MAC/Linux). If you did
not find it, try running
`import os; print(os.path.join(os.environ['APPDATA'], 'pavlovia_survey_utils'))`._

#### How to remove my access data?

_To remove a specific user (or all users) from the local cache, call `psu.remove_user_from_cache('username')` (
or `psu.purge_cache()`) respectively
Alternatively - manually edit or remove the JSON file under the directory used by `pavlovia_survey_utils`. Not sure
where that is?
See previous question._

## Contributing

If you find a bug :bug:, please open
a [bug report](https://github.com/EitanHemed/pavlovia_survey_utils/issues/new?assignees=&labels=bug&template=bug_report.md&title=).
If you have an idea for an improvement or new feature :rocket:, please open
a [feature request](https://github.com/EitanHemed/pavlovia_survey_utils/issues/new?assignees=&labels=Feature+request&template=feature_request.md&title=).

