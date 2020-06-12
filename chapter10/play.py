import argparse
import os
from mountain_car import MountainCar

ENV_DICT = {
  'mountain_car': MountainCar(),
}


def play(env):
  def refresh():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(env)
  while True:
    env.reset()
    done = False
    while not done:
      key = ''
      while key not in env.keys:
        refresh()
        key = input("press key\n$>")
        if key == "exit()":
          exit()
      _, _, done, _ = env.step_via_key(key)
    again = input("episode done, continue? (Y / n)")
    if again == 'n':
      break


def main():
  parser = argparse.ArgumentParser()

  parser.add_argument('-e', '--env', type=str, default='mountain_car',
                      help='Env to play with.',
                      choices=ENV_DICT.keys())
  args = parser.parse_args()
  play(ENV_DICT[args.env])


if __name__ == "__main__":
  main()