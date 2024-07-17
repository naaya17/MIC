#!/usr/bin/env python3
"""The main module logger."""

import logging

_logger = logging.getLogger('main')

critical = _logger.critical
debug = _logger.debug
error = _logger.error
exception = _logger.exception
info = _logger.info
log = _logger.log
warning = _logger.warning