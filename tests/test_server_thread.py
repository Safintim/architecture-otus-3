from queue import Queue
from typing import Any

from architecture_otus_3.server_thread import (
    ServerThread,
    HardStopCommand,
    SoftStopCommand,
    RunnerCommand,
)


def test_hardstop_command(mocker: Any) -> None:
    queue: Queue = Queue()
    server_thread: ServerThread = ServerThread(queue)

    mock_command1: Any = mocker.Mock()
    mock_command2: Any = mocker.Mock()
    mock_command3: Any = mocker.Mock()

    queue.put(mock_command1)
    queue.put(HardStopCommand(server_thread))
    queue.put(mock_command2)
    queue.put(mock_command3)

    RunnerCommand(server_thread).execute()
    server_thread.thread.join()

    mock_command1.execute.assert_called_once()
    mock_command2.execute.assert_not_called()
    mock_command3.execute.assert_not_called()


def test_softstop_command(mocker: Any) -> None:
    queue: Queue = Queue()
    server_thread: ServerThread = ServerThread(queue)

    mock_command1: Any = mocker.Mock()
    mock_command2: Any = mocker.Mock()
    mock_command3: Any = mocker.Mock()

    queue.put(mock_command1)
    queue.put(SoftStopCommand(server_thread))
    queue.put(mock_command2)
    queue.put(mock_command3)

    RunnerCommand(server_thread).execute()
    server_thread.thread.join()

    mock_command1.execute.assert_called_once()
    mock_command2.execute.assert_called_once()
    mock_command3.execute.assert_called_once()


def test_command_with_exception(mocker: Any) -> None:
    queue: Queue = Queue()
    server_thread: ServerThread = ServerThread(queue)

    mock_command1: Any = mocker.Mock(**{"execute.side_effect": [Exception()]})
    mock_command2: Any = mocker.Mock()

    queue.put(mock_command1)
    queue.put(mock_command2)
    queue.put(SoftStopCommand(server_thread))

    RunnerCommand(server_thread).execute()
    server_thread.thread.join()

    mock_command1.execute.assert_called_once()
    mock_command2.execute.assert_called_once()
