# prolog-env
A Python package providing an environment for AI agents to test their Prolog code.

## Getting started
[Install SWI-Prolog from PPA](https://www.swi-prolog.org/build/PPA.html)
```bash
sudo apt-add-repository ppa:swi-prolog/stable
sudo apt-get update
sudo apt-get install swi-prolog libpython3-dev
```

Install prolog-env
```bash
pip install prolog-env
```

Usage
```py
from prolog_env import SimpleEvaluator

env = SimpleEvaluator()

code = """
train('Amsterdam', 'Haarlem').
train('Amsterdam', 'Schiphol').
"""

observation, reward, terminated, truncated, info = env.step(code)

print("Observation:")
print(observation)
print("Reward:", reward)

tests = """
:- begin_tests(test).

test(a) :-
        A is 2^3,
        assertion(float(A)),
        assertion(A == 9).

:- end_tests(test).
"""

observation, reward, terminated, truncated, info = env.step(code, tests)

print("Observation:")
print(observation)
print("Reward:", reward)