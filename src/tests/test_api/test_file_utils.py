import unittest

import pandas as pd

from pavlovia_survey_utils.api import file_utils


class TestFileUtils(unittest.TestCase):

    def test_find_image_columns(self):
        df = pd.DataFrame({
            'image1': ['data:image/png;base64,abc', 'data:image/png;base64,def'],
            'image2': ['data:image/png;base64,ghi', 'data:image/png;base64,jkl'],
            'text': ['abc', 'def']
        })

        self.assertEqual(file_utils.find_image_columns(df), ['image1', 'image2'])

        self.assertEqual(file_utils.find_image_columns(
            df.drop(columns=['image1'])), ['image2'])

        self.assertEqual(file_utils.find_image_columns(
            df[['text']]), []) # No image columns

    def test_read_base64_img_str(self):
        pass

    def test_save_image_columns(self):
        pass


if __name__ == "__main__":
    unittest.main()
