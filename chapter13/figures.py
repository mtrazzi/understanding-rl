import argparse
import numpy as np
import matplotlib.pyplot as plt
from corridor import Corridor
from reinforce import Reinforce
from utils import feat_corr, pi_gen_corr, logpi_wrap_corr

#plt.switch_backend('Qt5Agg')

BIG_FONT = 20
MED_FONT = 15
SMA_FONT = 13

FIG_13_1_ALP_L = [2 ** (-k) for k in range(12, 15)]
FIG_13_1_N_EP = 1000
FIG_13_1_N_RUNS = 100
FIG_13_1_G = 1
FIG_13_1_THE_DIM = 2
FIG_13_1_OPT_REW = -11.6


def save_plot(filename, dpi=None):
  plt.savefig('plots/' + filename + '.png', dpi=dpi)


def plot_figure(ax, title, xticks, xnames, xlabel, yticks, ynames, ylabel,
                labelpad=15, font=SMA_FONT, loc='upper left'):
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


def run(ax, alg, alp_l, n_ep, n_runs):
  for alp in alp_l:
    alg.a = alp
    print(f"[ALPHA={alp}]")
    tot_rew = np.zeros(n_ep)
    for seed in range(n_runs):
      print(f"[RUN #{seed}]")
      alg.reset()
      alg.seed(seed)
      tot_rew += np.array(alg.train(n_ep))
    plt.plot(tot_rew / n_runs, label=f'alpha=2 ** {np.log(alp) / np.log(2)}')
  plt.plot(np.zeros(n_ep) + FIG_13_1_OPT_REW, '--', label='v*(s_0)')


def benchmark(alg, title, fn):
  fig, ax = plt.subplots()
  fig.suptitle(title, fontsize=BIG_FONT)
  fig.set_size_inches(20, 14)

  xticks, yticks = np.linspace(0, 1000, 6), np.linspace(-90, -10, 9)
  def short_str(x): return str(x)[:3]
  xnames, ynames = map(short_str, xticks), map(short_str, yticks)
  run(ax, alg, FIG_13_1_ALP_L, FIG_13_1_N_EP, FIG_13_1_N_RUNS)
  plot_figure(ax, '', xticks, xnames, 'Episode', list(yticks) + [0], ynames,
              (f'Total\nReward\non episode\n(Averaged over\n' +
               f'{FIG_13_1_N_RUNS} runs)'), font=MED_FONT, labelpad=40,
              loc='upper right')
  save_plot(fn, dpi=100)
  plt.show()


def fig_13_1():
  env = Corridor()

  alg = Reinforce(env, None, FIG_13_1_G, FIG_13_1_THE_DIM, pi_gen_corr,
                  logpi_wrap_corr(env, feat_corr), the_0=None)
  benchmark(alg, 'Figure 13.1', 'fig13.1')


PLOT_FUNCTION = {
  '13.1': fig_13_1,
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


if __name__ == "__main__":
  main()