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
import logging

from prompt_toolkit.document import Document
from prompt_toolkit.application import get_app


LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def set_stream_logger(logger_name, log_level, stream=None,
                      format_string=None):
    """
    Convenience method to configure a stream logger.

    :type logger_name: str
    :param logger_name: The name of the logger to configure

    :type log_level: str
    :param log_level: The log level to set for the logger.  This
        is any param supported by the ``.setLevel()`` method of
        a ``Log`` object.

    :type stream: file
    :param stream: A file like object to log to.  If none is provided
        then sys.stderr will be used.

    :type format_string: str
    :param format_string: The format string to use for the log
        formatter.  If none is provided this will default to
        ``self.LOG_FORMAT``.

    """
    log = logging.getLogger(logger_name)
    log.setLevel(logging.DEBUG)

    remove_stream_logger(logger_name)

    handler_name = f'{logger_name}_stream_handler'
    ch = PromptToolkitHandler(stream, name=handler_name)
    ch.setLevel(log_level)

    # create formatter
    if format_string is None:
        format_string = LOG_FORMAT
    formatter = logging.Formatter(format_string)

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    log.addHandler(ch)


def remove_stream_logger(logger_name):
    """
    Convenience method to configure a stream logger.

    :type logger_name: str
    :param logger_name: The name of the logger to configure

    """
    log = logging.getLogger(logger_name)
    handler_name = f'{logger_name}_stream_handler'
    for handler in log.handlers:
        if handler.name == handler_name:
            log.removeHandler(handler)


class PromptToolkitHandler(logging.StreamHandler):

    def __init__(self, stream=None, name=None):
        super(PromptToolkitHandler, self).__init__(stream)
        if name is not None:
            self.set_name(name)

    def emit(self, record):
        try:
            app = get_app()
            if app.is_running and getattr(app, 'debug', False):
                msg = self.format(record)
                debug_buffer = app.layout.get_buffer_by_name('debug_buffer')
                current_document = debug_buffer.document.text
                if current_document:
                    msg = '\n'.join([current_document, msg])
                debug_buffer.set_document(
                    Document(text=msg), bypass_readonly=True
                )
            else:
                super().emit(record)
        except:
            self.handleError(record)
