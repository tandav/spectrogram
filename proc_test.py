import multiprocessing
import time
import random


def task(i):
    time.sleep(2 * random.random())
    return i


if __name__ == '__main__':
    n_processes = 16

    with multiprocessing.Pool(processes=n_processes) as pool:
        for i in pool.imap(task, range(100)):
            time.sleep(0.1)
            print(time.time(), i)
            if i % n_processes == 0:
                print('=' * 72)


