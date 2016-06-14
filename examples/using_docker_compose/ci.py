#!/usr/bin/env python

from datetime import timedelta

from parallel_ci_runner import (
    CIRunner, DockerBuildCommand, DockerCommand, DockerComposeCommand, SpecCommandInGroups,
)

###
### Set up docker command generators
###
docker_build = DockerBuildCommand('examples/ci-example-project', '1234')
env_vars = {
    'DOCKER_IMAGE': docker_build.full_image_name()
}
docker_compose = DockerComposeCommand(env_vars=env_vars)
docker_run = DockerCommand('exec', docker_compose.project_name_base)
rspec_command = SpecCommandInGroups('rspec')

###
### Generate lists of parallel commands
###
NUM_PARALLEL = 4
up_cmds = [docker_compose.build('web', 'up -d') for _ in range(NUM_PARALLEL)]
rspec_cmds = [docker_run.build(rspec_command.build(NUM_PARALLEL)) for _ in range(NUM_PARALLEL)]
cleanup_commands = [docker_compose.cleanup() for _ in range(NUM_PARALLEL)]

###
### Set the commands and run
###
runner = CIRunner()
runner.add_serial_command_step(docker_build.build(), timedelta(minutes=10))
runner.add_parallel_command_step(up_cmds, timedelta(minutes=1))
runner.add_serial_command_step(docker_run.build("find . -name *_spec.rb"), timedelta(minutes=1),
                               stdout_callback=rspec_command.load_specs)
runner.add_parallel_command_step(rspec_cmds, timedelta(minutes=1))
runner.add_parallel_cleanup_step(cleanup_commands, timedelta(minutes=1))
runner.run()
