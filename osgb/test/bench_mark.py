import timeit
import platform

n = 10

t = timeit.timeit("osgb.ll_to_grid(52 + 2 * random.random(), 0 - 3 * random.random())",
                  setup="import random; import osgb", number=n * 1000)

s = timeit.timeit("osgb.grid_to_ll(random.randrange(400000,500000), random.randrange(200000,500000))",
                  setup="import random; import osgb", number=n * 1000)

print("Grid banger bench mark running under {} {} on {}".format(
      platform.python_implementation(), platform.python_version(), platform.platform()))
print("ll_to_grid: {:5d}/s {:.3g} ms per call".format(int(1000 * n / t), t / n))
print("grid_to_ll: {:5d}/s {:.3g} ms per call".format(int(1000 * n / s), s / n))
