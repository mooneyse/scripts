from multiprocessing import Pool

def add(args):
    (x, y, z) = args
    return x + y + z

pool = Pool(4)
pool.map(add, [(1, 2, 3), (4, 5, 6), (7, 8, 9)])
