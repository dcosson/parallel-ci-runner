# Parallel CI Runner

A framework for defining and running parallel CI tests.

In particular, it has helpers you use to write a ci.py file with arbitrarily complicated test runs on clusters of containers using docker-compose.

(It also works for running any other shell commands, but a lot of the useful helpers are docker related).

## Usage
It tries to be agnostic of your setup, and just provide building blocks for you to compose. An example, somewhat complex use migt be:

 - spinning up 5 independent copies of an environment defined in a docker-compose.yml file (each of which might have, say, a web app connected to a database and elasticsearch instance)
 - running integration tests in one cluster of containers and at the same time splitting up unit tests into 4 groups to run in parallel on the other 4
 - stopping & removing all 5 clusters when the tests finish

### Runner

The basic data model is that a CIRunner contains a list of steps, and each step is either a single command to run or a list of commands to run in parallel. You can set a timeout for a step, which is used to kill any command in the step that runs for longer than the timeout value.

A "command" (as passed to arguments that take a command or commands_list) is just a function that takes in an integer command number and returns a string of a shell command to run (the integer is used to specify which of N parallel proccesses it's running as)

If any of the shell commands in a step exits with a non-zero code or times out, the entire test run fails and exits with status 1.

You can define cleanup steps as well - these are run whether the test run succeeds or fails. The entire list of cleanup steps is run even if some of them fail, and a failing cleanup step won't cause the run to fail.

### Docker
The helpers for generating docker and docker-compose commands let you use a couple of approaches for isolating commands so that they can run in parallel.

 - It uses the -p project-name argument to docker-compose for spinning up isolated clusters of containers in parallel, which works for `docker-compose run`ing commands.
 - It exposes environment variables `CI_COMMAND_NUMBER` and `PROJECT_NAME` (which contains the command number) that you can assign to `container_name` in docker-compose.yml. This works for spinning up the containers with a dummy command like `docker-compose up -d sleep 3600` and then `docker exec`ing commands using the container_name in the running containers.

You'll probably need to be pretty comfortable with docker & docker-compose to make much sense of how this works. I tried to stick to a simple data model that lets you express arbitrarily complicated setups, multiple groups of containers at once, etc. (as opposed to trying to guess what everyone's setups might be and try to make it work out of the box).

## Examples

The examples directory has a super simple shell example, and a full-fledged example of spinning up separate docker-compose clusters and running some commands on them in parallel.

## Future improvements:

Number of parallel processes should be separate from the number of commands
to run, i.e. allow it to look like pool of workers pulling from a queue of
jobs. This would allow e.g. having 100 spec files and running them 1 at a
time as they finish on 10 parallel workers, where worker 1 might only run two files and worker 2 might run 20 in the same time.
  
Currently, it only supports e.g. splitting 100 files into 10 groups of 10 and
running each group on a worker, which is more prone to stragglers.

- Support running a parallel command step on multiple machines (this is
  should be super simple with the DOCKER_HOST variable, probably just need
  to be able to pass extra env vars to the `build()` methods for the docker,
  docker build and docker compose builders).
