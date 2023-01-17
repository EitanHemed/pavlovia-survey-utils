# pyvlovia

`pyvlovia` is a Python library that retrieves data from
[Pavlovia](https://pavlovia.org) surveys. It can be used to receive either the raw JSON format
data, or save a tidy version of the data, including downloading of images (e.g., signatures)
uploaded by your survey participants.

## Sections:

- [Setup](#setup)
- [Requirements](#requirements)
- [Usage](#usage)
- [FAQ](#faq)
- [Contributing](#contributing)

## Setup

`pip install pyvlovia`

## Requirements

- `pandas`
- `requests`

## Usage

You can use pyvlovia either interactively (`pyvlovia.ui`), or embed it in your scripts(`pyvlovia.cache_io`):

1. List existing users:

```
import pyvlovia
pyvlovia.list_users() #pyvlovia.
```

2. Add a new user:

`pyvlovia.add_user()`

3. List surveys for an existing user:
`pyvlovia.list_surveys(username)`

4.

## FAQ

#### What permissions does pyvlovia require?

pyvlovia generates an access token on gitlab with a `read-user` scope. See
[here](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#personal-access-token-scopes) for details.

#### Where is my access token stored?

Similarly to PsychoPy, your username and access token are stored in the AppData directory, on your computer (e.g.,
`C:\Users\User\AppData\Roaming\pyvlovia` on Windows, `HOME/pyvlovia` on MAC/Linux). If you did not find it, try running
`import os; print(os.path.join(os.environ['APPDATA'], 'pyvlovia'))`.

#### How to remove my login data?

1. Call either `pyvlovia.remove_user(username)` or
   `pyvlovia.remove_all_users()` to remove all existing logins.
2. Manually edit or remove the JSON file under the directory used by `pyvlovia`. Not sure where that is?
   See previous question.

## Contributing

If you find a bug :bug:, please open
a [bug report](https://github.com/EitanHemed/pyvlovia/issues/new?assignees=&labels=bug&template=bug_report.md&title=).
If you have an idea for an improvement or new feature :rocket:, please open
a [feature request](https://github.com/EitanHemed/pyvlovia/issues/new?assignees=&labels=Feature+request&template=feature_request.md&title=).
