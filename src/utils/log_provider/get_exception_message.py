import sys
import traceback


def get_exception_message(exception: Exception, limit: int = -5):
    """
    If an exception raised, show the last few call stacks.
    """
    error_class = exception.__class__.__name__
    detail = None if not exception.args else exception.args[0]

    _, _, tb = sys.exc_info()
    lastCallStack = traceback.extract_tb(tb, limit=limit)
    message = "Traceback (most recent call last):"
    for call in lastCallStack:
        filename, lineno, name, line = call[:]  # type: ignore
        message += f"\n  File \"{filename}\", line {lineno}, in {name}\n    {line}"
    message += f"\n[{error_class}] {detail}"

    return message
