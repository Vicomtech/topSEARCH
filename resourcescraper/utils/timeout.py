import errno
import functools
import os
import signal
import threading


class TimeoutError(Exception):
    pass


def timeout(seconds:int=10, error_message:str=os.strerror(errno.ETIME)):
    """
    A decorator to apply a timeout to a function, raising a TimeoutError if the function execution exceeds the
    specified duration.

    Args:
        seconds (int, optional): The maximum number of seconds the function is allowed to run. If the function exceeds this duration, a TimeoutError is raised. Defaults to 10 seconds.
        error_message (str, optional): The error message to be used when raising the TimeoutError.

    Returns:
        A decorated function that raises a TimeoutError if the execution time exceeds the specified limit.
    """
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # signal.signal(signal.SIGALRM, _handle_timeout)
            # signal.alarm(seconds)
            # try:
            #     result = func(*args, **kwargs)
            # finally:
            #     signal.alarm(0)
            # return result
            result = [None]

            # Define a target function that runs the original function
            def target():
                result[0] = func(*args, **kwargs)

            # Create a thread to run the target function
            thread = threading.Thread(target=target)
            thread.start()
            thread.join(seconds)  # Wait for the thread to finish or timeout

            if thread.is_alive():
                raise TimeoutError(error_message)
            return result[0]

        return wrapper

    return decorator
