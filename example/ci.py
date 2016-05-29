from app.docker_utils import ParallelRunner, SerialRunner, DockerComposeCommandBuilder, DockerBuildCommandBuilder


def foo_cmd(i):
    return "sleep 2 && echo 'ran command with {0}'".format(i)

web_compose_builder = DockerComposeCommandBuilder()
cmd = web_compose_builder.build('run web echo hello')

sr = SerialRunner()
sr.add_command(cmd)

# print("running in serial")
sr.run()

# pr = ParallelRunner()
# pr.add_command(foo_cmd)
# pr.add_command(foo_cmd)
# pr.add_command(foo_cmd)
# 
# print("running in parallel")
# pr.run()
# 
# 

