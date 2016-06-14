import logging
import sys


logger = logging.Logger('parallel-test-runner', level=logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
handler.formatter = logging.Formatter(
        '%(asctime)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
logger.addHandler(handler)
