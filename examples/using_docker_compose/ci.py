from datetime import timedelta

from app.docker import DockerBuildCommand, DockerComposeCommand
from app.runner import CIRunner

runner = CIRunner()
docker_build = DockerBuildCommand('examples/ci-example-project', '1234')
runner.add_serial_command_step(docker_build.build(), timedelta(minutes=10))

docker_compose = DockerComposeCommand(
    project_name_base='ci-example', env_vars={
        'DOCKER_IMAGE': docker_build.full_path(),
        'CI_RUNNER_NUMBER': '1',
    })

runner.add_serial_command_step(docker_compose.build('web', 'up -d'), timedelta(minutes=1))


def rspec_cmd(process_number):
    return "docker exec parallel-ci-example-{0} rspec".format(process_number)

runner.add_serial_command_step(rspec_cmd, timedelta(minutes=1))

runner.add_serial_cleanup_step(docker_compose.cleanup(), timedelta(minutes=1))

runner.run()
