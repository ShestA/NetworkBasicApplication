from typing import Callable


def delete_multiple_element(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if idx < len(list_object):
            list_object.pop(idx)


def retry(fn: Callable[[], bool], retries: int) -> bool:
    for _ in range(retries):
        if fn() is True:
            return True
    return False
