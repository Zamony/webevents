import os
import io
import cgi
import json
import pathlib
import threading
import contextlib
import socketserver
import multiprocessing
from http.server import SimpleHTTPRequestHandler

import pkg_resources


class WebGUIRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def do_GET(self):
        if self.path == "/snakes_receive.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            try:
                message_dict = self.server.in_queue.get_nowait()
            except Exception:
                self.wfile.write('""'.encode("utf-8"))
                self.server.out_queue.put("keep_alive")
            else:    
                message_str = json.dumps(message_dict)
                self.wfile.write(message_str.encode("utf-8"))
            
        elif self.path == "/webevents.js":
            self.send_response(200)
            self.send_header(
                "Content-Type", "application/javascript; charset=utf-8"
            )
            self.end_headers()
            self.wfile.write(
                pkg_resources.resource_string(__name__, "webevents.js")
            )
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != "/snakes_send":
            self.send_response(404)
        else:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': self.headers['Content-Type'],
                }
            )

            self.server.out_queue.put({
                field: form.getvalue(field) for field in form.keys()
            })

            out = io.TextIOWrapper(
                self.wfile,
                encoding='utf-8',
                line_buffering=False,
                write_through=True,
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            out.write('""')
            out.detach()

    def log_message(self, format, *args):
        pass


class SnakesEvents:
    def __init__(self, py_in_queue, py_out_queue, timeout):
        self._timeout = timeout
        self._termination_callbacks = []
        self._event_listeners = {}
        self._py_in_queue = py_in_queue
        self._py_out_queue = py_out_queue
        self._listener_thread = threading.Thread(target=self.run_listener)
        self._listener_thread.start()

    def fire_event(self, event_type, event_data):
        self._py_out_queue.put({
            "event_type": event_type, "data": event_data
        })

    def add_event_listener(self, event_type, func):
        try:
            self._event_listeners[event_type].append(func)
        except KeyError:
            self._event_listeners[event_type] = [func]

    def remove_event_listener(self, event_type, func):
        self._event_listeners[event_type].remove(func)

    def add_termination_callback(self, func):
        self._termination_callbacks.append(func)

    def run_listener(self):
        timeout = None
        while True:
            try:
                data = self._py_in_queue.get(timeout=timeout)
            except Exception:
                break
            if data is None:
                break
            if data == "keep_alive":
                continue
            try:
                event_type = data["event_type"]
                event_data = data.get("data")
                for callback in self._event_listeners[event_type]:
                    if event_data:
                        callback(json.loads(event_data))
                    else:
                        callback()
            except KeyError:
                pass

            timeout = self._timeout

        for callback in self._termination_callbacks:
            callback()

    def terminate(self):
        self._py_in_queue.put(None)


@contextlib.contextmanager
def _working_directory(path):
    prev_cwd = pathlib.Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def _run_server(address, in_queue, out_queue):
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(
        address, WebGUIRequestHandler
    ) as httpd:
        httpd.in_queue = in_queue
        httpd.out_queue = out_queue
        httpd.allow_reuse_address = True
        httpd.serve_forever()


def run(address, folder, timeout=5):
    with _working_directory(folder):
        py_in_queue = multiprocessing.Queue()
        py_out_queue = multiprocessing.Queue()
        guiproc = multiprocessing.Process(
            target=_run_server,
            args=(address, py_out_queue, py_in_queue)
        )
        guiproc.start()
    snakes_events = SnakesEvents(py_in_queue, py_out_queue, timeout)
    snakes_events.add_termination_callback(lambda: guiproc.terminate())
    snakes_events.add_termination_callback(lambda: guiproc.join())
    return snakes_events
