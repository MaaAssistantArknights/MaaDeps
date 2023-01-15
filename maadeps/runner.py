from __future__ import annotations
from typing import overload, TYPE_CHECKING, Generic, TypeVar, Callable
P = TypeVar("P")
RetT = TypeVar("RetT")
if TYPE_CHECKING:
    from typing import ParamSpec
    P = ParamSpec("P")


class Task(Generic[P, RetT]):
    def __init__(self, func: Callable[P, RetT], cached=False, ignore_failure=False):
        self.__func__ = func
        self.completed = False
        self.result = None
        self.cached = cached
        self.ignore_failure = ignore_failure
    
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> RetT:
        if self.cached and self.completed:
            return self.result
        try:
            self.result = self.__func__(*args, **kwargs)
            self.completed = True
            return self.result
        except:
            if not self.ignore_failure:
                raise
            import traceback
            traceback.print_exc()

@overload
def task(func: Callable[P, RetT]) -> Task[P, RetT]:
    ...

@overload
def task(*, ignore_failure=False) -> Callable[[Callable[P, RetT]], Task[P, RetT]]:
    ...

def task(func=..., *, ignore_failure=False):
    if func is ...:
        def wrapper(func):
            return Task(func, ignore_failure=ignore_failure)
        return wrapper
    else:
        return Task(func, ignore_failure=ignore_failure)
