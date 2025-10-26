import random
import logging

_LOG = logging.getLogger("kxspy.utils")

def get_random_username():
    return "kxspy_" + ''.join(random.choice("0123456789abcdef") for _ in range(10))


