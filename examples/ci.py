from datetime import timedelta
# from app.docker_utils import DockerComposeCommandBuilder
from app.runner import BaseRunner


def foo_cmd(i):
    return r"sleep 2 && echo ran command with {0}".format(i)


def foo_timeout_cmd(i):
    return r"sleep 10 && echo ran command with {0}".format(i)


# web_compose_builder = DockerComposeCommandBuilder()
# cmd = web_compose_builder.build('run web echo hello')

runner = BaseRunner()
runner.add_serial_command_step(foo_cmd)
runner.add_parallel_command_step([foo_cmd, foo_cmd, foo_timeout_cmd], timeout=timedelta(seconds=3))
runner.run()

# pr = ParallelRunner()
# pr.add_command(foo_cmd)
# pr.add_command(foo_cmd)
# pr.add_command(foo_cmd)
# 
# print("running in parallel")
# pr.run()
# 
# 

