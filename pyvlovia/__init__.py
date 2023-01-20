from . import auth, surveys_io, cache_io

if not cache_io.test_if_user_cache_exists():
    cache_io.create_user_cache()
