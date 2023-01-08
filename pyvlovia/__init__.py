from . import auth, surveys, cache_io
from .ui import *

if not cache_io.test_if_user_cache_exists():
    cache_io.create_user_cache()
