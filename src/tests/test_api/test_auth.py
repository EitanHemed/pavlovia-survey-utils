"""This module contains the mock tests for the auth module."""

import json
import unittest
import unittest.mock as mock

import requests

from pavlovia_survey_utils.api import auth
from pavlovia_survey_utils.api.auth import USERS_CACHE_FNAME, TOKEN_KEY_NAME, REGISTRATION_DATE_KEY_NAME

mock_user_1 = 'mock_user_1'
mock_password_1 = 'mock_password_1'
mock_token_1 = 'mock_token_1'
registration_date_1 = auth._get_timestamp()

mock_user_2 = 'mock_user_2'
mock_password_2 = 'mock_password_2'
mock_token_2 = 'mock_token_2'
registration_date_2 = auth._get_timestamp()

two_users = {mock_user_1: {TOKEN_KEY_NAME: mock_token_1, REGISTRATION_DATE_KEY_NAME: registration_date_1},
             mock_user_2: {TOKEN_KEY_NAME: mock_token_2, REGISTRATION_DATE_KEY_NAME: registration_date_2}}
only_user_1 = {mock_user_1: {TOKEN_KEY_NAME: mock_token_1, REGISTRATION_DATE_KEY_NAME: registration_date_1}}
only_user_2 = {mock_user_2: {TOKEN_KEY_NAME: mock_token_2, REGISTRATION_DATE_KEY_NAME: registration_date_2}}



class TestAuth(unittest.TestCase):

    def test_get_pavlovia_access_token(self, mock_token=mock_token_1):
        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {'access_token': mock_token}
            token = auth.get_pavlovia_access_token(mock_user_1, mock_password_1)
            assert token == mock_token

    def test_add_user_to_cache(self):
        # Mock the http request and the response
        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {'access_token': mock_token_1}

            with mock.patch('builtins.open', mock.mock_open()) as _mock_open:
                _mock_open.return_value.read.return_value = json.dumps({})

                # Add the user to the cache
                auth.add_user_to_cache(mock_user_1, mock_password_1)

                _mock_open.return_value.read.return_value = json.dumps(only_user_1)

                # Check if the file was written to
                _mock_open().write.assert_called_once_with(json.dumps(only_user_1))

                _mock_open().write.rereset_mock()

                # Change the return value of the post request
                mock_post.return_value.json.return_value = {'access_token': mock_token_2}

                auth.add_user_to_cache(mock_user_2, mock_password_2)
                _mock_open().write.assert_called_once_with(json.dumps(only_user_2))



    def test_add_user_to_cache_force_update(self):
        with mock.patch('builtins.open', mock.mock_open()) as mock_open:

            with mock.patch('requests.post') as mock_post:
                mock_post.return_value.json.return_value = {'access_token': mock_token_1}

                auth.add_user_to_cache(mock_user_1, mock_password_1)
                mock_open().write.assert_called_once_with(json.dumps(only_user_1))

                mock_open().write.reset_mock()
                mock_post().reset_mock()

                auth.add_user_to_cache(mock_user_1, mock_password_1, force_update=True)
                mock_open().write.assert_called_once_with(json.dumps(only_user_1))

    def test_remove_user_from_cache(self):
        with mock.patch('builtins.open', mock.mock_open()) as mock_open:
            with mock.patch('os.path.exists', return_value=True):
                mock_open().read.return_value = json.dumps(only_user_1)
                # Should remove the user and return True - the user exists
                assert auth.remove_user_from_cache(mock_user_1)
                # Should not remove the user and return False - the user does not exist
                assert not auth.remove_user_from_cache(mock_user_2)

    def test_load_available_users(self):
        with mock.patch('builtins.open', mock.mock_open()) as mock_open:
            # Define the return value of the mock_open().read() method
            mock_open().read.return_value = json.dumps(
                {mock_user_1: {TOKEN_KEY_NAME: mock_token_1, REGISTRATION_DATE_KEY_NAME: registration_date_1}})

            # Load the available users
            users = auth.load_available_users()

            # Check if the users are as expected
            assert users == [mock_user_1]

            # Add the second user
            mock_open().read.return_value = json.dumps(two_users)

            # Load the available users
            users = auth.load_available_users()

            # Check if the users are as expected
            assert users == [mock_user_1, mock_user_2]

    def test_purge_cache(self):
        with mock.patch('os.remove') as mock_remove:
            auth.purge_cache()
            mock_remove.assert_called_once_with(auth._get_user_reg_path())


if __name__ == '__main__':
    unittest.main()
