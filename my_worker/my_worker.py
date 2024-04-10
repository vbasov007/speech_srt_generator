import ctypes
import threading
import uuid
from typing import Callable, MutableMapping, Any, Optional


class MyWorker:
    def __init__(self, storage: Optional[MutableMapping[str, Any]] = None):
        if storage is None:
            self._storage = {}
        else:
            self._storage = storage

        self._threads = {}

    def run(self, target: Callable, *args, **kwargs):
        worker_id = str(uuid.uuid4())  # Generate a unique ID

        # Initialize the job in our "database"
        self._storage[worker_id] = {
            'status': 'started',
            'progress': 0,
            'stage': "",
            'result': None,
        }

        def report_progress(value, stage=None):
            self._storage[worker_id]['progress'] = value
            self._storage[worker_id]['stage'] = "" if stage is None else stage

        # Function to execute and write the results to our "database"
        def task():
            result = target(*args, **kwargs, report_progress=report_progress)
            self._storage[worker_id]['status'] = 'completed'
            self._storage[worker_id]['result'] = result

        self._threads[worker_id] = threading.Thread(target=task)
        self._threads[worker_id].start()

        return worker_id

    def get_status(self, worker_id):
        return self._storage.get(worker_id, {}).get('status')

    def get_result(self, worker_id):
        return self._storage.get(worker_id, {}).get('result')

    def get_progress(self, worker_id):
        return self._storage.get(worker_id, {}).get('progress', 0)

    def get_stage(self, worker_id):
        return self._storage.get(worker_id, {}).get('stage', "")

    def clear(self, worker_id):
        if worker_id in self._threads:
            if self._threads[worker_id].is_alive():
                self.terminate(worker_id)

            del self._storage[worker_id]
            del self._threads[worker_id]

    def terminate(self, worker_id):
        if worker_id in self._threads:
            # Get the worker thread
            worker_thread = self._threads[worker_id]

            # Check if the worker thread is alive
            if worker_thread.is_alive():
                # Terminate the worker thread
                _async_raise(worker_thread.ident, SystemExit)

                # Update the status in storage
                self._storage[worker_id]['status'] = 'terminated'

                return True
        return False


def _async_raise(tid, ex_type):
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(ex_type))
    if res == 0:
        raise ValueError("Invalid thread ID")
    elif res != 1:
        # If it returns a number other than one, an error occurred
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")
