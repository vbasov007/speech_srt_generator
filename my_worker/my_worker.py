import threading
import uuid
from typing import Callable, MutableMapping, Any, Optional


class MyWorker:
    def __init__(self, storage: Optional[MutableMapping[uuid.UUID, Any]] = None):
        if storage is None:
            self._storage = {}
        else:
            self._storage = storage

    def run(self, target: Callable, *args, **kwargs):
        worker_id = uuid.uuid4()  # Generate a unique ID

        # Initialize the job in our "database"
        self._storage[worker_id] = {
            'status': 'started',
            'progress': 0,
            'result': None,
        }

        def report_progress(value):
            self._storage[worker_id]['progress'] = value

        # Function to execute and write the results to our "database"
        def task():
            result = target(*args, **kwargs, report_progress=report_progress)
            self._storage[worker_id]['status'] = 'completed'
            self._storage[worker_id]['result'] = result

        threading.Thread(target=task).start()

        return worker_id

    def get_status(self, worker_id):
        return self._storage[worker_id]['status']

    def get_result(self, worker_id):
        return self._storage[worker_id]['result']

    def get_progress(self, worker_id):
        return self._storage[worker_id]['progress']

    def clear(self, worker_id):
        del self._storage[worker_id]
