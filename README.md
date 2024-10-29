# Java Code Runner

Compile and run Java code with [Python Subprocess](https://docs.python.org/3/library/subprocess.html).
This project will act as a worker for another project, basically to create a service like 
[Leetcode](https://leetcode.com/) or [Hackerrank](https://www.hackerrank.com/)...a poor man's version at least. 

Meant to be run as a docker container to prevent any harsh actions to the host server.
More security measurements needed.

## Middlewares

- Postgresql: The Database...obviously
- RabbitMQ: Listens to incoming code run requests

All run on Docker with compose
 
## Dependencies

- SQLAlchemy: ORM Framework
- psycopg: Python Postgresql Driver
- Pika: AMQP 0-9-1 protocol implementation
  
## Interests

Recently participated projects was focused on what is right...or popular, to be precise. 
Which was a very stressful work environment.
So using python, I wanted to try out tools I wasn't familiar with, 
without much reference from blogs, tutorials, but only documentations.
Since most of my python experience was algorithms and Django, it was a joyful experience.

## Basic Concepts

Before, there were separate python scripts that control compiling and running.
Now, it is all wrapped up into an abstract class, [`CodeRunner`](runner.py), which handles the following tasks:

1. Save the source in a desired format. (`CodeRunner.save()`)
2. Prepare the source so it could be run. (`CodeRunner.prep()`)
3. Run the code and organize results. (`CodeRunner.run()`)
4. Cleanup any files no longer needed. (`CodeRunner.cleanup()`)

All methods are meant to be run in an independent manner, so when chances come
the tasks may be migrated to other compartments. `save()` method is the only `super` method, 
and each `CodeRunner` implementation is expected to work based on the method's return value.

The [`rabbit_listener.py`](rabbit_listener.py) listens to code run requests via RabbitMQ with pika.
So multiple instances of `rabbit_listener.py`s can run several solutions at once.


## Configuration

TODO

## TODO

- [X] Dockerfile
  - [ ] Documentation
- [X] Configuration management
  - [ ] Documentation
- [ ] GitHub Actions
- [X] Set run restrictions (timeout, memory)
- [ ] Run multiple test cases at once
- [ ] Find more security vulnerabilities
- [X] Clean up files
