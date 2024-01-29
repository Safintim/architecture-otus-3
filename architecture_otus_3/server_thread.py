from threading import Thread
from queue import Queue
from typing import Callable, Protocol
from loguru import logger


class ICommand(Protocol):
    def execute(self) -> None:
        ...


class ServerThread:
    def __init__(self, queue: Queue) -> None:
        self.queue: Queue = queue
        self.is_stop: bool = False
        self.behavior: Callable = self._default_behavior
        self.thread: Thread = Thread(target=self._run_behavior)

    def start(self) -> None:
        logger.debug(f"{self}: Start")
        self.thread.start()

    def stop(self) -> None:
        logger.debug(f"{self}: Stop")
        self.is_stop = True

    def update_behavior(self, new_behavior: Callable) -> None:
        self.behavior = new_behavior

    def _run_behavior(self) -> None:
        while not self.is_stop:
            self.behavior()

    def _default_behavior(self) -> None:
        logger.debug(f"{self}: default behavior run")
        command: ICommand = self.queue.get()
        try:
            logger.debug(f"{self}: execute {command.__class__.__name__}")
            command.execute()
        except Exception as exc:
            logger.error(f"{self}: {command.__class__.__name__} failed, {exc}")
            ...

    def __str__(self) -> str:
        return f"[{self.__class__.__name__}]"


class RunnerCommand:
    def __init__(self, server_thread: ServerThread) -> None:
        self.server_thread: ServerThread = server_thread

    def execute(self) -> None:
        self.server_thread.start()


class SoftStopCommand:
    def __init__(self, server_thread: ServerThread) -> None:
        self.server_thread: ServerThread = server_thread

    def execute(self) -> None:
        self.server_thread.update_behavior(self._soft_stop_behavior)

    def _soft_stop_behavior(self) -> None:
        logger.debug(f"{self}: soft_stop")
        if self.server_thread.queue.empty():
            logger.debug(f"{self}: queue is empty")
            return self.server_thread.stop()

        command: ICommand = self.server_thread.queue.get()
        try:
            logger.debug(f"{self}: execute {command.__class__.__name__}")
            command.execute()
        except Exception as exc:
            logger.error(f"{self}: {command.__class__.__name__} failed, {exc}")
            ...

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"


class HardStopCommand:
    def __init__(self, server_thread: ServerThread) -> None:
        self.server_thread: ServerThread = server_thread

    def execute(self) -> None:
        self.server_thread.stop()
