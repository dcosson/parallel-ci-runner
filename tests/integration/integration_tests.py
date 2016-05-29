from unittest import TestCase

from app import (
    DockerBuildCommandBuilder, DockerComposeCommandBuilder, ParallelRunner, SerialRunner)


class IntegrationTests(TestCase):

    def test_docker_build_and_run_command(self):
        build_cmd = DockerBuildCommandBuilder('elasticsearch', '1.5.2')
        sr = SerialRunner()
        sr.add_command(build_cmd)
