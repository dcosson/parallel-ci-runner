from datetime import timedelta

from app.docker import DockerBuildCommand, DockerCommand, DockerComposeCommand
from app.runner import CIRunner

# Set up docker command generators
docker_build = DockerBuildCommand('examples/ci-example-project', '1234')
env_vars = {
    'DOCKER_IMAGE': docker_build.full_path()
}
docker_compose = DockerComposeCommand(env_vars=env_vars)
docker_run = DockerCommand('exec', 'parallel-ci-example-')

# Set commands and run
runner = CIRunner()
runner.add_serial_command_step(docker_build.build(), timedelta(minutes=10))
runner.add_serial_command_step(docker_compose.build('web', 'up -d'), timedelta(minutes=1))
runner.add_serial_command_step(docker_run.build('rspec'), timedelta(minutes=1))
runner.add_serial_cleanup_step(docker_compose.cleanup(), timedelta(minutes=1))
runner.run()
