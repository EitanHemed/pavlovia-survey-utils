"""This module contains the mock tests for the auth module."""

import json
import unittest
import unittest.mock as mock

from pavlovia_survey_utils.api import auth
from pavlovia_survey_utils.api.auth import TOKEN_KEY_NAME, REGISTRATION_DATE_KEY_NAME

mock_user_1 = 'mock_user_1'
mock_password_1 = 'mock_password_1'
mock_token_1 = 'mock_token_1'
registration_date_1 = auth._get_timestamp()

mock_user_1_updated = 'mock_user_1'
mock_password_1_updated = 'mock_password_1'
mock_token_1_updated = 'mock_token_1 UPDATED'
registration_date_1_updated = 'UPDATED TIMESTAMP'

mock_user_2 = 'mock_user_2'
mock_password_2 = 'mock_password_2'
mock_token_2 = 'mock_token_2'
registration_date_2 = registration_date_1

only_user_1 = {mock_user_1: {TOKEN_KEY_NAME: mock_token_1, REGISTRATION_DATE_KEY_NAME: registration_date_1}}
only_user_2 = {mock_user_2: {TOKEN_KEY_NAME: mock_token_2, REGISTRATION_DATE_KEY_NAME: registration_date_2}}

two_users = {**only_user_1, **only_user_2}

only_user_1_updated = {mock_user_1: {TOKEN_KEY_NAME: mock_token_1_updated,
                                     REGISTRATION_DATE_KEY_NAME: registration_date_1_updated}}


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

                # Change the return value of the post request
                mock_post.return_value.json.return_value = {'access_token': mock_token_2}

                auth.add_user_to_cache(mock_user_2, mock_password_2)
                _mock_open().write.assert_has_calls([mock.call(json.dumps(only_user_1)), mock.call(json.dumps(two_users))])




    def test_add_user_to_cache_force_update(self):

        with mock.patch('builtins.open', mock.mock_open()) as mock_open:
            mock_open.return_value.read.return_value = json.dumps({})

            with mock.patch('requests.post') as mock_post:

                mock_post.return_value.json.return_value = {'access_token': mock_token_1}
                # Add the user to the cache
                auth.add_user_to_cache(mock_user_1, mock_password_1)
                mock_open().read.return_value = json.dumps(only_user_1)

                mock_post.return_value.json.return_value = {'access_token': only_user_1_updated[mock_user_1][TOKEN_KEY_NAME]}
                mock_open().write.return_value = json.dumps(only_user_1_updated)
                auth.add_user_to_cache(mock_user_1, mock_password_1, force_update=True)
                mock_open().read.return_value = json.dumps(only_user_1_updated)

                assert auth.load_token_for_user(mock_user_1) == only_user_1_updated[mock_user_1][TOKEN_KEY_NAME]

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
