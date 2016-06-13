# from app.docker_utils import DockerComposeCommandBuilder
from app.runner import BaseRunner


def foo_cmd(i):
    return r"sleep 2 && echo -e 'ran command with {0}\nanother line\nanother line'".format(i)

# web_compose_builder = DockerComposeCommandBuilder()
# cmd = web_compose_builder.build('run web echo hello')

runner = BaseRunner()
runner.add_serial_command_step(foo_cmd)
runner.add_parallel_command_step([foo_cmd, foo_cmd, foo_cmd])
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

