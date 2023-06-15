import unittest


def swap(i: int, j: int, sol: list) -> list:
    sol[i], sol[j] = sol[j], sol[i]
    return sol


def reverse(p1: int, p2: int, parent: list) -> list:
    reverse_part = parent[p1:p2]
    reverse_part.reverse()

    return parent[:p1] + reverse_part + parent[p2:]


def unique_pairs(n: int):
    for i in range(n + 1):
        for j in range(i + 1, n + 1):
            yield i, j


class UtilTestCase(unittest.TestCase):
    def test_swap(self):
        l = [i for i in range(10)]
        swap(0, 9, l)
        self.assertListEqual([9, 1, 2, 3, 4, 5, 6, 7, 8, 0], l)

    def test_reverse(self):
        l = [i for i in range(10)]
        reversed_list = reverse(1, 9, l)
        self.assertListEqual([0, 8, 7, 6, 5, 4, 3, 2, 1, 9], reversed_list)

    def test_reverse_2(self):
        l = [i for i in range(10)]
        reversed_list = reverse(8, 9, l)
        self.assertListEqual(l, reversed_list)

    def test_unique_pairs(self):
        pairs = list(unique_pairs(5))
        self.assertListEqual([(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 4), (3, 5), (4, 5)],
                             pairs)


if __name__ == '__main__':
    unittest.main()
