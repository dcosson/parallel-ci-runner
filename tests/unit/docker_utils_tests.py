from unittest import TestCase

from app.docker_utils import (
    DockerBuildCommandBuilder, DockerComposeCommandBuilder)


class DockerUtilsTests(TestCase):

    def test_docker_build_command_builder(self):
        b = DockerBuildCommandBuilder('reponame', '123',
                                      dockerfile='./path/Dockerfile')
        self.assertEqual(
            b.build()(2),
            'docker build -f ./path/Dockerfile -t reponame:123')

    def test_docker_compose_command_builder_default_args(self):
        b = DockerComposeCommandBuilder()
        self.assertEqual(
            b.build('web', 'do foo')(1),
            'docker-compose -f docker-compose.yml run web do foo')

    def test_docker_compose_command_builder_with_env_vars(self):
        b = DockerComposeCommandBuilder(env_vars={'FOO': 'bar'})
        self.assertEqual(
            b.build('bar', 'do foo')(1),
            'FOO=bar docker-compose -f docker-compose.yml run bar do foo')

    def test_docker_compose_command_builder_with_process_num(self):
        b = DockerComposeCommandBuilder(project_name_base='project')
        self.assertEqual(
            b.build('web', 'cmd')(2),
            'docker-compose -f docker-compose.yml -p project2 run web cmd')

    def test_docker_compose_command_builder_with_process_num_but_no_base(self):
        b = DockerComposeCommandBuilder()
        # wont append the process_number if no base project name
        self.assertEqual(
            b.build('bar', 'cmd')(2),
            'docker-compose -f docker-compose.yml run bar cmd')

    def test_docker_compose_command_builder_other_commands(self):
        # A docker-compose command other than run, with an app args
        b = DockerComposeCommandBuilder()
        self.assertEqual(
            b.build('web', None, docker_compose_command='up -d')(2),
            'docker-compose -f docker-compose.yml up -d web')

    def test_docker_compose_command_builder_other_commands_no_args(self):
        # A docker-compose command other than run, all apps
        b = DockerComposeCommandBuilder()
        self.assertEqual(
            b.build(None, None, docker_compose_command='up -d')(2),
            'docker-compose -f docker-compose.yml up -d')
