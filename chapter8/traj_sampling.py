import numpy as np
import time

class TrajectorySampling:
  def __init__(self, env, gamma=1, eps=0.1):
    self.env = env
    self.g = gamma
    self.eps = eps
    self.reset()

  def gre(self, s):
    q_arr = np.array([self.Q[(s, a)] for a in self.env.moves_d[s]])
    return self.env.moves_d[s][np.random.choice(np.flatnonzero(q_arr == q_arr.max()))]

  def gre_value_iteration(self, s_0, theta=1e-4):
    V = {s: 0 for s in self.env.states}
    while True:
      delta = 0
      for s in self.env.states:
        v = V[s]
        r, next_states = self.env.trans[(s, self.gre(s))]
        V[s] = r + ((1 - self.env.eps)  / self.env.b) * sum(V[s_p] for s_p in next_states)
        delta = max(delta, abs(v-V[s]))
      if delta < theta:
        break
    return V[s_0]

  def eps_gre(self, s):
    if np.random.random() < self.eps:
      return sample(self.env.moves_d[s])
    return self.gre(s)

  def exp_update(self, s, a):
    exp_rew, next_states = self.env.trans[(s, a)]
    self.Q[(s, a)] = exp_rew + self.g * (1 - self.eps) * sum(max(self.Q[(s_p, a_p)] for a_p in self.env.moves_d[s_p]) for s_p in next_states)

  def uniform(self, start_state, n_updates, log_freq=100):
    values = []
    start = time.time()
    for upd in range(n_updates):
      for s in self.env.states:
        for a in self.env.moves_d[s]:
          self.exp_update(s, a) 
      if upd % log_freq == (log_freq - 1):
        print(f"{upd + 1} updates (total of {time.time()-start:.2f}s)")
        values.append(self.gre_value_iteration(start_state, theta=1))
    return np.array(values)

  def on_policy(self, start_state, n_updates, log_freq=100):
    values = []
    start = time.time()
    for upd in range(n_updates):
      for s in self.env.states:
        for a in self.env.moves_d[s]:
          self.exp_update(s, a) 
      if upd % log_freq == (log_freq - 1):
        print(f"{upd + 1} updates (total of {time.time()-start:.2f}s)")
        values.append(self.gre_estimation(start_state))
    return values

  def reset(self):
    self.Q = {(s, a): 0 for s in self.env.states for a in self.env.moves_d[s]} 
