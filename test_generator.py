#!/usr/bin/env python3
# Run as: ./tests.py

from generation import GenerationTracker
import unittest


class TestSequences(unittest.TestCase):
    def check_sequence(self, sequence):
        generator = GenerationTracker()
        for i, (action, option, expected_distrib) in enumerate(sequence):
            with self.subTest(step=i):
                if action == 'join':
                    generator.notify_join(option)
                elif action == 'leave':
                    generator.notify_leave(option)
                elif action == 'chosen':
                    generator.notify_chosen(option)
                else:
                    raise AssertionError(action)
                actual_distrib = generator.get_weights()
                self.assertEqual(expected_distrib, actual_distrib)
                d = generator.to_dict()
                generator2 = GenerationTracker.from_dict(d)
                d2 = generator2.to_dict()
                self.assertEqual(d, d2)
                GenerationTracker.combine_weights(1, actual_distrib, 2, actual_distrib)

    def test_empty(self):
        self.check_sequence([])

    def test_join(self):
        self.check_sequence([
            ('join', 'a', dict(a=9)),
        ])

    def test_multijoin(self):
        self.check_sequence([
            ('join', 'a', dict(a=9)),
            ('join', 'b', dict(a=9, b=9)),
            ('join', 'c', dict(a=9, b=9, c=9)),
        ])

    def test_single(self):
        self.check_sequence([
            ('join', 'a', dict(a=9)),
            ('chosen', 'a', dict(a=0)),
            ('chosen', 'a', dict(a=0)),
            ('chosen', 'a', dict(a=0)),
        ])

    def test_leave(self):
        self.check_sequence([
            ('join', 'a', dict(a=9)),
            ('leave', 'a', dict()),
            ('join', 'a', dict(a=9)),
            ('leave', 'a', dict()),
        ])

    def test_two(self):
        self.check_sequence([
            ('join', 'a', dict(a=9)),
            ('join', 'b', dict(a=9, b=9)),
            ('chosen', 'a', dict(a=0, b=16)),
            ('chosen', 'a', dict(a=0, b=25)),
            ('chosen', 'a', dict(a=0, b=36)),
            ('chosen', 'b', dict(a=1, b=0)),
            ('chosen', 'b', dict(a=4, b=0)),
            ('chosen', 'b', dict(a=9, b=0)),
            ('chosen', 'a', dict(a=0, b=1)),
        ])

    def test_three(self):
        self.check_sequence([
            ('join', 'a', dict(a=9)),
            ('join', 'b', dict(a=9, b=9)),
            ('join', 'c', dict(a=9, b=9, c=9)),
            ('chosen', 'a', dict(a=0, b=16, c=16)),
            ('chosen', 'b', dict(a=1, b=0, c=25)),
            ('chosen', 'c', dict(a=4, b=1, c=0)),
            ('chosen', 'a', dict(a=0, b=4, c=1)),
            ('chosen', 'c', dict(a=1, b=9, c=0)),
            ('chosen', 'b', dict(a=4, b=0, c=1)),
        ])


if __name__ == '__main__':
    unittest.main()
