from utils import trans_id
from abc import ABC, abstractmethod
import time
import numpy as np


class MDP(ABC):
    """Base environment for the dynamic programming chapter."""

    def __init__(self):
        self.init_p()

    def init_p(self):
        print("starting to compute transitions p...")
        start = time.time()
        self.p = {trans_id(s_p, r, s, a): self._p(s_p, r, s, a)
                  for s in self.states for a in self.moves
                  for s_p in self.states for r in self.r}

        def p_sum(s_p_list, r_list, s_list, a_list):
            return np.sum([self.p[trans_id(s_p, r, s, a)] for s_p in s_p_list
                           for r in r_list for s in s_list for a in a_list])
        for s in self.states:
            for a in self.moves:
                self.p[trans_id('', 'r', s, a)] = [p_sum(self.states, [r], [s],
                                                         [a]) for r in self.r]
                self.p[trans_id('s_p', '', s, a)] = [p_sum([s_p], self.r, [s],
                                                     [a])
                                                     for s_p in self.states]
        print(f"finished after {time.time()-start}s")

    @abstractmethod
    def _p(self, s_p, r, s, a):
        """Specific transition probabilities for environment."""
        raise NotImplementedError

    @property
    @abstractmethod
    def states(self):
        """List of possible states."""
        raise NotImplementedError

    @property
    @abstractmethod
    def r(self):
        """List of possible rewards."""
        raise NotImplementedError

    @property
    @abstractmethod
    def moves(self):
        """List of all available actions."""
        raise NotImplementedError
