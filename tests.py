#!/usr/bin/env python3
# Run as: ./tests.py

import logic
import unittest


class TestStringMethods(unittest.TestCase):
    def check_sequence(self, sequence):
        game = logic.OngoingGame()
        for i, (query, expected_response) in enumerate(sequence):
            with self.subTest(step=i):
                actual_response = logic.handle(game, *query)
                self.assertEqual(expected_response, actual_response)

    def test_empty(self):
        self.check_sequence([])

    def test_start(self):
        self.check_sequence([
            (['start', '', 'fina', 'usna'], ['unknown_command', 'fina']),
        ])

    def test_join(self):
        self.check_sequence([
            (['join', '', 'fina', 'usna'], ['welcome', 'fina']),
        ])

if __name__ == '__main__':
    unittest.main()
