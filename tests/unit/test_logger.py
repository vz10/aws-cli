# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import contextlib
import logging
import mock
import io

from prompt_toolkit.buffer import Buffer
from awscli.logger import (
    set_stream_logger, remove_stream_logger, PromptToolkitHandler
)

from awscli.testutils import unittest


class TestLogger(unittest.TestCase):
    def test_can_set_stream_handler(self):
        set_stream_logger('test_logger', logging.DEBUG)
        log = logging.getLogger('test_logger')
        self.assertEqual(log.handlers[0].name, 'test_logger_stream_handler')

    def test_keeps_only_one_stream_handler(self):
        set_stream_logger('test_logger', logging.DEBUG)
        set_stream_logger('test_logger', logging.ERROR)
        log = logging.getLogger('test_logger')
        self.assertEqual(len(log.handlers), 1)
        self.assertEqual(log.handlers[0].name, 'test_logger_stream_handler')
        self.assertEqual(log.handlers[0].level, logging.ERROR)

    def test_can_remove_stream_handler(self):
        set_stream_logger('test_logger', logging.DEBUG)
        remove_stream_logger('test_logger')
        log = logging.getLogger('test_logger')
        self.assertEqual(len(log.handlers), 0)


class TestPromptToolkitHandler(unittest.TestCase):
    def setUp(self):
        self.handler = PromptToolkitHandler()

    @mock.patch('awscli.logger.get_app')
    def test_can_log_to_prompter(self, get_app):
        set_stream_logger('test_logger', logging.DEBUG)
        log = logging.getLogger('test_logger')
        buffer = Buffer()
        app = mock.Mock()
        app.debug = True
        app.is_running = True
        app.layout.get_buffer_by_name.return_value = buffer
        get_app.return_value = app
        log.debug('error message')
        self.assertIn('error message', buffer.document.text)

    def test_log_to_stderr_if_no_app(self):
        fake_stderr = io.StringIO()
        with contextlib.redirect_stderr(fake_stderr):
            set_stream_logger('test_logger', logging.DEBUG)
            log = logging.getLogger('test_logger')
            log.debug('error message')
        self.assertIn('error message', fake_stderr.getvalue())
