# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

from ajsonrpc.core import JSONRPC20DispatchException

from platformio.compat import aio_get_running_loop


class IDERPC:
    def __init__(self):
        self._queue = {}

    def send_command(self, sid, command, params):
        if not self._queue.get(sid):
            raise JSONRPC20DispatchException(
                code=4005, message="PIO Home IDE agent is not started"
            )
        while self._queue[sid]:
            self._queue[sid].pop().set_result(
                {"id": time.time(), "method": command, "params": params}
            )

    async def listen_commands(self, sid=0):
        if sid not in self._queue:
            self._queue[sid] = []
        self._queue[sid].append(aio_get_running_loop().create_future())
        return await self._queue[sid][-1]

    def open_project(self, sid, project_dir):
        return self.send_command(sid, "open_project", project_dir)

    def open_text_document(self, sid, path, line=None, column=None):
        return self.send_command(
            sid, "open_text_document", dict(path=path, line=line, column=column)
        )
