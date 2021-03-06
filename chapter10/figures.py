import argparse
import matplotlib.pyplot as plt
import numpy as np
from tiles_sutton import IHT, tiles
from mountain_car import MountainCar, X_MIN, X_MAX, V_MIN, V_MAX
from semi_grad_sarsa import EpisodicSemiGradientTD0
from nstep_semi_grad_sarsa import nStepSemiGradSarsa
from access_control import AccessControlQueuingTask, ACCEPT, REJECT
from diff_semi_grad_sarsa import DiffSemiGradientSarsa
import seaborn as sns

BIG_FONT = 20
MED_FONT = 15

N_TIL = 4096
N_TLGS = 8

FIG_10_1_G = 1
FIG_10_1_STEPS = 428
FIG_10_1_EP_L = [12, 104, 1000, 9000]
FIG_10_1_ALP = 0.5 / 8

FIG_10_2_ALP_L = [alpha / 8 for alpha in [0.1, 0.2, 0.5]]
FIG_10_2_N_EP = 500
FIG_10_2_G = FIG_10_1_G
FIG_10_2_N_RUNS = 100

FIG_10_3_ALP_L = [alpha / 8 for alpha in [0.5, 0.3]]
FIG_10_3_N_L = [1, 8]
FIG_10_3_N_EP = 500
FIG_10_3_G = FIG_10_1_G
FIG_10_3_N_RUNS = 100

FIG_10_4_N_EP = 50
FIG_10_4_G = FIG_10_2_G
FIG_10_4_N_RUNS = 100
FIG_10_4_ALP_PTS = 10
FIG_10_4_ALP_BND = {
  1: [0.4, 1.7],
  2: [0.3, 1.7],
  4: [0.2, 1.5],
  8: [0.1, 1.0],
  16: [0.1, 0.8],
}

FIG_10_5_ALP = 0.01
FIG_10_5_BET = 0.01
FIG_10_5_EPS = 0.1
FIG_10_5_QUE_SIZE = 4
FIG_10_5_N_SERV = 10
FIG_10_5_N_STEPS = int(2e6)


def save_plot(filename, dpi=None):
  plt.savefig('plots/' + filename + '.png', dpi=dpi)


def plot_figure(ax, title, xticks, xnames, xlabel, yticks, ynames, ylabel,
                labelpad=15, font=MED_FONT, loc='upper left'):
  ax.set_title(title, fontsize=font)
  ax.set_xticks(xticks)
  ax.set_xticklabels(xnames)
  ax.set_yticks(yticks)
  ax.set_yticklabels(ynames)
  ax.set_xlim([min(xticks), max(xticks)])
  ax.set_ylim([min(yticks), max(yticks)])
  ax.set_xlabel(xlabel, fontsize=font)
  ax.set_ylabel(ylabel, rotation=0, fontsize=font, labelpad=labelpad)
  plt.legend(loc=loc)


def get_idxs(iht, x, xdot, a):
  return tiles(iht, N_TLGS, [N_TLGS * x / (X_MAX - X_MIN),
               N_TLGS * xdot / (V_MAX - V_MIN)], [a])


def print_qhat_mc(alg, fig, fig_id, title, n_pts=50, act=None):
  ax = fig.add_subplot(fig_id, projection='3d')
  ax.set_title(title, fontsize=BIG_FONT)
  qhat, w = alg.qhat, alg.w
  X = np.linspace(X_MIN, X_MAX, n_pts)
  V = np.linspace(V_MIN, V_MAX, n_pts)
  if act is None:
    def cost(x, v): return -max([qhat([x, v], a, w) for a in alg.env.moves])
  else:
    def cost(x, v): return -qhat([x, v], act, w)
  qvals = np.array([[cost(x, v) for x in X] for v in V])
  (X, Y), Z = np.meshgrid(X, V), qvals
  ax.set_xlabel('Position', fontsize=15)
  ax.set_ylabel('Velocity', fontsize=15)
  ax.set_zlabel('Cost', fontsize=15)
  ax.set_xticks([X.min(), X.max()])
  ax.set_yticks([V.min(), V.max()])
  ax.set_zticks([qvals.min(), qvals.max()])
  COLOR_DICT = {-1: 'r', 0: 'g', 1: 'b'}
  ax.plot_surface(X, Y, Z, color=COLOR_DICT[act] if act is not None else None)


def get_qhats(n_til, n_tlgs):
  iht = IHT(N_TIL)
  def idxs(s, a): return get_idxs(iht, s[0], s[1], a)
  def qhat(s, a, w): return np.sum(w[idxs(s, a)])

  def nab_qhat(s, a, w):
    res = np.zeros(len(w))
    for idx in idxs(s, a):
      res[idx] = True
    return res
  return qhat, nab_qhat


def fig_10_1():
  def plot_and_save(filename, title, alg, n_ep, max_steps=np.inf):
    fig = plt.figure()
    alg.pol_eva(qhat, nab_qhat, n_ep, FIG_10_1_G, max_steps=max_steps)
    print_qhat_mc(alg, fig, '111', title)
    fig.set_size_inches(20, 14)
    save_plot(filename, dpi=100)
    plt.show()

  qhat, nab_qhat = get_qhats(N_TIL, N_TLGS)
  env = MountainCar()
  alg = EpisodicSemiGradientTD0(env, FIG_10_1_ALP, N_TIL * N_TLGS, eps=0)
  alg.seed(0)
  plot_and_save(f'fig10.1_{FIG_10_1_STEPS}_steps', f'Step {FIG_10_1_STEPS}',
                alg, 1, FIG_10_1_STEPS)

  tot_ep = 1
  for ep in FIG_10_1_EP_L:
    alg.pol_eva(qhat, nab_qhat, ep - tot_ep, FIG_10_2_G)
    plot_and_save(f'fig10.1_{ep}_episodes', f'Episode {ep}', alg, ep - tot_ep)
    tot_ep += (ep - tot_ep)


def fig_10_2():
  fig, ax = plt.subplots()
  qhat, nab_qhat = get_qhats(N_TIL, N_TLGS)

  for alp in FIG_10_2_ALP_L:
    print(f"[alpha={alp}]")
    tot_n_steps = np.zeros(FIG_10_2_N_EP)
    for seed in range(FIG_10_2_N_RUNS):
      print(f"[RUN #{seed}]")
      alg = EpisodicSemiGradientTD0(MountainCar(), alp, N_TIL * N_TLGS, eps=0)
      alg.seed(seed)
      tot_n_steps += np.array(alg.pol_eva(qhat, nab_qhat, FIG_10_2_N_EP,
                                          FIG_10_2_G))
    plt.plot(tot_n_steps / FIG_10_2_N_RUNS, label=f'alpha={alp}')
  plt.yscale('log')
  xticks, yticks = [0, 500], [100, 200, 400, 1000]
  plot_figure(ax, 'Figure 10.2', xticks, xticks, 'Episode', yticks, yticks,
              'Steps\nper episode\n(log scale)')
  fig.set_size_inches(20, 14)
  plt.legend()
  save_plot('fig10.2', dpi=100)
  plt.show()


def fig_10_3():
  fig, ax = plt.subplots()
  qhat, nab_qhat = get_qhats(N_TIL, N_TLGS)

  for (n, alp) in zip(FIG_10_3_N_L, FIG_10_3_ALP_L):
    print(f"[n={n}, alpha={alp}]")
    tot_n_steps = np.zeros(FIG_10_3_N_EP)
    for seed in range(FIG_10_3_N_RUNS):
      print(f"[RUN #{seed}]")
      alg = nStepSemiGradSarsa(MountainCar(), alp, N_TIL * N_TLGS, 0, n)
      alg.seed(seed)
      tot_n_steps += np.array(alg.pol_eva(None, qhat, nab_qhat, FIG_10_3_N_EP,
                                          FIG_10_3_G))
    plt.plot(tot_n_steps / FIG_10_3_N_RUNS, label=f'n={n}')
  plt.yscale('log')
  xticks, yticks = [0, 500], [100, 200, 400, 1000]
  plot_figure(ax, 'Figure 10.3', xticks, xticks, 'Episode', yticks, yticks,
              'Steps\nper episode\n(log scale)')
  fig.set_size_inches(20, 14)
  plt.legend()
  save_plot('fig10.3', dpi=100)
  plt.show()


def fig_10_4():
  fig, ax = plt.subplots()
  qhat, nab_qhat = get_qhats(N_TIL, N_TLGS)

  alg = nStepSemiGradSarsa(MountainCar(), 0, N_TIL * N_TLGS, 0, 0)
  for n in FIG_10_4_ALP_BND:
    alg.n = n
    print(f"[n={n}]")
    steps_l = []
    alpha_l = np.linspace(*FIG_10_4_ALP_BND[n], FIG_10_4_ALP_PTS)
    for alpha in alpha_l:
      alg.a = alpha / N_TLGS
      print(f"[alpha={alg.a}]")
      tot_steps = 0
      for seed in range(FIG_10_4_N_RUNS):
        print(f"[RUN #{seed}]")
        alg.reset()
        alg.seed(seed)
        for ep in range(FIG_10_4_N_EP):
          tot_steps += alg.pol_eva(None, qhat, nab_qhat, 1, FIG_10_4_G,
                                   max_steps=1000)[0]
      steps_l.append(tot_steps / (FIG_10_4_N_RUNS * FIG_10_4_N_EP))
    plt.plot(alpha_l, steps_l, label=f'n={n}')
  xticks, yticks = np.linspace(0, 1.5, 4), np.linspace(220, 300, 5)
  left_title = (f'Mountain Car\nSteps per\nepisode\n(averaged \nover ' +
                f'first\n{FIG_10_4_N_EP} episodes\nand {FIG_10_4_N_RUNS} runs')
  plot_figure(ax, 'Figure 10.4', list(xticks) + [1.8], xticks,
              f'alpha * number of tilings ({N_TLGS})',
              yticks, yticks, left_title, labelpad=20)
  fig.set_size_inches(20, 14)
  plt.legend()
  save_plot('fig10.4', dpi=100)
  plt.show()


def print_pol_acc_contr(ax, alg):
  n_prio, n_serv = alg.env.queue.shape[0], alg.env.n_serv
  pol = np.zeros((n_prio, n_serv))
  for rank in range(n_prio):
    for free_serv in range(1, n_serv + 1):
      pol[rank, free_serv - 1] = alg.eps_gre(alg.env.encode_state(rank, n_serv,
                                                                  free_serv))
  yticks, xticks = np.arange(4), np.arange(10)
  ynames, xnames = [2 ** y for y in yticks], xticks + 1
  ax.set_title('Policy')
  sns.heatmap(pol, xticklabels=xnames, yticklabels=ynames,
              cbar_kws={'label': f'{REJECT} = REJECT, {ACCEPT} = ACCEPT'})


def print_val_acc_contr(ax, alg):
  n_prio, n_serv = alg.env.queue.shape[0], alg.env.n_serv
  for rank in range(n_prio):
    val = []
    for free_serv in range(n_serv + 1):
      s = alg.env.encode_state(rank, n_serv, free_serv)
      a_max = alg.eps_gre(s)
      val.append(alg.qhat(s, a_max, alg.w))
    plt.plot(val, label=f'priority {2 ** rank}')
  xticks, yticks = np.arange(n_serv + 1), np.linspace(-10, 10, 6)
  plot_figure(ax, 'Value Function', xticks, xticks,
              'Number of free servers', list(yticks) + [12], yticks,
              'Differential\nvalue of\n best action', labelpad=30)


def fig_10_5():
  fig = plt.figure()
  fig.set_size_inches(20, 28)
  fig.suptitle('Figure 10.5')
  env = AccessControlQueuingTask(FIG_10_5_N_SERV, FIG_10_5_QUE_SIZE)
  n_act = len(env.moves)
  w_dim = (env.n_serv + 1) * env.queue.shape[0] * n_act
  alg = DiffSemiGradientSarsa(env, FIG_10_5_ALP, FIG_10_5_BET, w_dim,
                              FIG_10_5_EPS)
  mat = np.eye(w_dim)
  nab_l = [mat[i] for i in range(w_dim)]
  def qhat(s, a, w): return w[s * n_act + a]
  def nab_qhat(s, a, w): return nab_l[s * n_act + a]
  alg.seed(0)
  alg.pol_eva(qhat, nab_qhat, FIG_10_5_N_STEPS)
  alg.eps = 0
  print_pol_acc_contr(fig.add_subplot('211'), alg)
  print_val_acc_contr(fig.add_subplot('212'), alg)
  plt.legend()
  save_plot('fig10.5', dpi=100)
  plt.show()


PLOT_FUNCTION = {
  '10.1': fig_10_1,
  '10.2': fig_10_2,
  '10.3': fig_10_3,
  '10.4': fig_10_4,
  '10.5': fig_10_5,
}


def main():
  parser = argparse.ArgumentParser()

  parser.add_argument('figure', type=str, default=None,
                      help='Figure to reproduce.',
                      choices=list(PLOT_FUNCTION.keys()) + ['all'])
  args = parser.parse_args()
  if args.figure == 'all':
    for key, f in PLOT_FUNCTION.items():
      print(f"[{key}]")
      f()
  else:
    print(f"[{args.figure}]")
    PLOT_FUNCTION[args.figure]()


if __name__ == '__main__':
  main()
