import time


def retry_log_error(retry_delay=5, logger=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            while 1:
                try:
                    s = f(*args, **kwargs)
                    return s
                except Exception as e:
                    msg = str(e) + '; retrying in %s s...' % retry_delay
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(retry_delay)

        return wrapper

    return decorator