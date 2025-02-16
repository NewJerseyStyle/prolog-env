import re
import io
import sys
import warnings
from contextlib import redirect_stdout, redirect_stderr, contextmanager
import traceback
import gymnasium as gym
from gymnasium.spaces import Text
import janus_swi as janus

@contextmanager
def capture_output():
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            yield new_out, new_err, w
    finally:
        sys.stdout, sys.stderr = old_out, old_err


DEFAULT_CONFIG = {
    "max_input_output_len": 32000,    # longest length of the code
    "exception_reward": -9
}
TEST_FAIL_PATTERN = r"ERROR:\s*(\d+)\s*test failed\s*\n%\s*(\d+)\s*tests passed"

class SimpleEvaluator(gym.Env):
    def __init__(self, config=DEFAULT_CONFIG):
        self.action_space = Text(config["max_input_output_len"])
        self.exception_reward = config["exception_reward"]
        assert self.exception_reward < 0, "Exception reward must be negative"
        self.observation_space = self.action_space
        self.reward = 0

    def reset(self, *, seed=None, options=None):
        """
        Resets the environment.

        Returns:
            tuple: A tuple containing the initial observation (empty string) and an info dictionary
                   with the key "env_state" set to "reset".
        """
        self.reward = 0
        return "", {"env_state": "reset"}

    def step(self, code, test:str=None):
        observation = "OK"
        reward = 0
        try:
            janus.consult("trains", action)
            if test:
                janus.consult("tests", test)
                with capture_output() as (out, err, warns):
                    janus.query("run_tests.")
                observation = f"## stdout:\n{out.getvalue()}\n\n"
                observation += f"## stderr:\n{err.getvalue()}\n\n"
                observation += f"## warnings:\n{[str(w.message)
                                                for w in warns]}\n\n"
                match = re.search(TEST_FAIL_PATTERN,
                                  observation,
                                  re.MULTILINE))
                if match:
                    failed_tests = int(match.group(1))
                    passed_tests = int(match.group(2))
                    total_tests = failed_tests + passed_tests
                    reward = failed_tests / total_tests
                    reward *= self.exception_reward
                else:
                    reward = -self.exception_reward
        except:
            observation = traceback.format_exc()
            reward = self.exception_reward
        terminated = False
        truncated = False
        infos = {}
        return (
            observation,
            reward,
            terminated,
            truncated,
            infos,
        )
