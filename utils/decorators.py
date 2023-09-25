from functools import wraps
import time
import logging

def time_it_async(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        tic = time.time()
        result = await func(*args, **kwargs)
        toc = time.time()
        logging.info(f"Time Elapsed: {round(toc-tic, 2)} seconds")
        return result
    return wrapper

def time_it_sync(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tic = time.time()
        result = func(*args, **kwargs)
        toc = time.time()
        logging.info(f"Time Elapsed: {round(toc-tic, 2)} seconds")
        return result
    return wrapper