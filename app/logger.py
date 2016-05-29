import logging
import sys


logger = logging.Logger('parallel-test-runner')
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.level = logging.INFO
