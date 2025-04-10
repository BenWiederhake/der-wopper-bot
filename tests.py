#!/usr/bin/env python3
# Run as: ./tests.py

import bot  # check whether the file parses
import logic
import msg  # check keyset
import secret  # need MESSAGES_SHEET, ugh
import unittest


class TestMigration(unittest.TestCase):
    def check_dict(self, d1):
        g1 = logic.OngoingGame.from_dict(d1)
        d2 = g1.to_dict()
        g2 = logic.OngoingGame.from_dict(d2)
        d3 = g2.to_dict()
        self.assertEqual(d2, d3)

    def test_empty_v0(self):
        self.check_dict({
            'joined_users': {
                },
            'last_chooser': None,
            'last_chosen': None,
            'last_wop': 'w',  # This is actually possible!
            'init_datetime': 1234,
            })

    def test_nonempty_v0(self):
        self.check_dict({
            'joined_users': {
                'usna1': 'fina1',
                'usna2': 'fina2',
                'usna3': 'fina3',
                },
            'last_chooser': 'usna1',
            'last_chosen': 'usna2',
            'last_wop': 'p',
            'init_datetime': 1234,
            })

    def test_empty_v1(self):
        self.check_dict({
            'joined_users': {
                },
            'last_chooser': None,
            'last_chosen': None,
            'last_wop': None,
            'init_datetime': 1234,
            'track_overall': { 'g': 1, 'lc': {} },
            'track_individual': {
                }
            })

    def test_nonempty_v1(self):
        self.check_dict({
            'joined_users': {
                'usna1': 'fina1',
                'usna2': 'fina2',
                'usna3': 'fina3',
                },
            'last_chooser': 'usna1',
            'last_chosen': 'usna2',
            'last_wop': 'p',
            'init_datetime': 1234,
            'track_overall': { 'g': 1, 'lc': {'usna1': -2, 'usna2': -2, 'usna3': -2} },
            'track_individual': {
                'usna1': {'g': 1, 'lc': {'usna2': -2, 'usna3': -2}},
                'usna2': {'g': 1, 'lc': {'usna1': -2, 'usna3': -2}},
                'usna3': {'g': 1, 'lc': {'usna1': -2, 'usna2': -2}},
                }
            })

    def test_nonempty_v2(self):
        self.check_dict({
            'joined_users': {
                'usna1': 'fina1',
                'usna2': 'fina2',
                'usna3': 'fina3',
                },
            'last_chooser': 'usna1',
            'last_chosen': 'usna2',
            'last_wop': 'p',
            'last_reason': 'Some reason-string here',
            'init_datetime': 1234,
            'track_overall': { 'g': 1, 'lc': {'usna1': -2, 'usna2': -2, 'usna3': -2} },
            'track_individual': {
                'usna1': {'g': 1, 'lc': {'usna2': -2, 'usna3': -2}},
                'usna2': {'g': 1, 'lc': {'usna1': -2, 'usna3': -2}},
                'usna3': {'g': 1, 'lc': {'usna1': -2, 'usna2': -2}},
                }
            })


class RandomReplyTests(unittest.TestCase):
    def test(self):
        for command in msg.RANDOM_REPLY:
            with self.subTest(command=command):
                template_list = msg.MESSAGES[command]
                self.assertTrue(template_list)
                # Check that all templates all work:
                for template in template_list:
                    self.assertTrue(template.format('Firstname', 'Username', 'https://foob.ar'))


class TestSequences(unittest.TestCase):
    def check_sequence(self, sequence):
        game = logic.OngoingGame('Static seed for reproducible randomness, do not change')
        for i, (query, expected_response) in enumerate(sequence):
            with self.subTest(step=i):
                actual_response = logic.handle(game, *query)
                self.assertEqual(expected_response, actual_response, query)
                self.assertIn(expected_response[0], msg.MESSAGES.keys())
                if expected_response == actual_response and expected_response[0] in msg.MESSAGES.keys():
                    template_list = msg.MESSAGES[expected_response[0]]
                    self.assertTrue(template_list, expected_response[0])
                    # Check that all templates all work:
                    for template in template_list:
                        self.assertTrue(template.format(*expected_response[1:]), (template, expected_response))
        d = game.to_dict()
        g2 = logic.OngoingGame.from_dict(d)
        d2 = g2.to_dict()
        self.assertEqual(d, d2)

    def test_empty(self):
        self.check_sequence([])

    def test_start(self):
        self.check_sequence([
            (('start', '', 'fina', 'usna'), ('unknown_command', 'fina')),
        ])

    def test_join(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'fina', 'usna'), ('already_in', 'fina')),
        ])

    def test_join_no_username(self):
        self.check_sequence([
            (('join', '', 'fina', ''), ('welcome_no_username', 'fina')),
            (('join', '', 'fina', None), ('welcome_no_username', 'fina')),
        ])

    def test_leave(self):
        self.check_sequence([
            (('leave', '', 'fina', 'usna'), ('already_left', 'fina')),
        ])

    def test_join_leave(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('leave', '', 'fina', 'usna'), ('leave', 'fina')),
            (('leave', '', 'fina', 'usna'), ('already_left', 'fina')),
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('leave', '', 'fina', 'usna'), ('leave', 'fina')),
            (('leave', '', 'fina', 'usna'), ('already_left', 'fina')),
        ])

    def test_leave_chooser_first(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'finb', 'usnb'), ('welcome', 'finb')),
            (('random', '', 'fina', 'usna'), ('random_chosen', 'usnb')),
            (('leave', '', 'fina', 'usna'), ('leave_chooser_handover', 'fina', 'usnb')),
            (('leave', '', 'finb', 'usnb'), ('leave_chosen_dunno', 'finb')),
        ])

    def test_leave_chosen_first(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'finb', 'usnb'), ('welcome', 'finb')),
            (('random', '', 'fina', 'usna'), ('random_chosen', 'usnb')),
            (('leave', '', 'finb', 'usnb'), ('leave_chosen_flee', 'finb', 'usna')),
            (('leave', '', 'fina', 'usna'), ('leave_chooser_dunno', 'fina')),
        ])

    def test_leave_other(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'finb', 'usnb'), ('welcome', 'finb')),
            (('random', '', 'fina', 'usna'), ('random_chosen', 'usnb')),
            (('join', '', 'finc', 'usnc'), ('welcome', 'finc')),
            (('leave', '', 'finc', 'usnc'), ('leave', 'finc')),
        ])

    def test_random_nonplayer(self):
        self.check_sequence([
            (('random', '', 'fina', 'usna'), ('nonplayer', 'fina')),
        ])

    def test_random_nonplayer_nonempty(self):
        self.check_sequence([
            (('join', '', 'a', 'a'), ('welcome', 'a')),
            (('join', '', 'b', 'b'), ('welcome', 'b')),
            (('random', '', 'fina', 'usna'), ('nonplayer', 'fina')),
        ])

    def test_random_singleplayer(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('random', '', 'fina', 'usna'), ('random_singleplayer', 'fina')),
            (('random', '', 'fina', 'usna'), ('random_singleplayer', 'fina')),
        ])

    def test_random_twoplayer_nowop(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('random', '', 'ofina', 'ousna'), ('random_nowop', 'ousna', 'fina')),
        ])
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('do_w', '', 'ofina', 'ousna'), ('dox_w', 'ofina', 'usna')),
            (('random', '', 'ofina', 'ousna'), ('random_chosen', 'usna')),
            (('random', '', 'fina', 'usna'), ('random_nowop', 'usna', 'ofina')),
        ])

    def test_random_twoplayer_idc_nowop(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('random', '', 'ofina', 'ousna'), ('random_nowop', 'ousna', 'fina')),
        ])
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('do_idc', '', 'ofina', 'ousna'), ('do_idc_p', 'ofina', 'usna')),  # Relies on seeded RNG
            (('random', '', 'ofina', 'ousna'), ('random_chosen', 'usna')),
            (('random', '', 'fina', 'usna'), ('random_nowop', 'usna', 'ofina')),
        ])

    def test_choose_nowop(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('choose', 'ousna', 'fina', 'usna'), ('chosen_chosen', 'ousna', 'fina')),
            (('choose', 'usna', 'ofina', 'ousna'), ('random_nowop', 'ousna', 'fina')),
        ])
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('choose', 'ousna', 'fina', 'usna'), ('chosen_chosen', 'ousna', 'fina')),
            (('do_w', '', 'ofina', 'ousna'), ('dox_w', 'ofina', 'usna')),
            (('choose', 'usna', 'ofina', 'ousna'), ('chosen_chosen', 'usna', 'ofina')),
            (('choose', 'ousna', 'fina', 'usna'), ('random_nowop', 'usna', 'ofina')),
        ])

    def test_choose_idc_nowop(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('choose', 'ousna', 'fina', 'usna'), ('chosen_chosen', 'ousna', 'fina')),
            (('choose', 'usna', 'ofina', 'ousna'), ('random_nowop', 'ousna', 'fina')),
        ])
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('choose', 'ousna', 'fina', 'usna'), ('chosen_chosen', 'ousna', 'fina')),
            (('do_idc', '', 'ofina', 'ousna'), ('do_idc_p', 'ofina', 'usna')),  # Relies on seeded RNG
            (('choose', 'usna', 'ofina', 'ousna'), ('chosen_chosen', 'usna', 'ofina')),
            (('choose', 'ousna', 'fina', 'usna'), ('random_nowop', 'usna', 'ofina')),
        ])

    def test_true_random_twoplayer_nowop(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('true_random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('true_random', '', 'ofina', 'ousna'), ('random_nowop', 'ousna', 'fina')),
        ])
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('true_random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('do_w', '', 'ofina', 'ousna'), ('dox_w', 'ofina', 'usna')),
            (('true_random', '', 'ofina', 'ousna'), ('random_chosen', 'usna')),
            (('true_random', '', 'fina', 'usna'), ('random_nowop', 'usna', 'ofina')),
        ])

    def test_true_random_twoplayer_idc_nowop(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('true_random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('true_random', '', 'ofina', 'ousna'), ('random_nowop', 'ousna', 'fina')),
        ])
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('true_random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('do_idc', '', 'ofina', 'ousna'), ('do_idc_p', 'ofina', 'usna')),  # Relies on seeded RNG
            (('true_random', '', 'ofina', 'ousna'), ('random_chosen', 'usna')),
            (('true_random', '', 'fina', 'usna'), ('random_nowop', 'usna', 'ofina')),
        ])

    def test_random_twoplayer(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('do_w', '', 'ofina', 'ousna'), ('dox_w', 'ofina', 'usna')),
            (('random', '', 'ofina', 'ousna'), ('random_chosen', 'usna')),
            (('do_w', '', 'fina', 'usna'), ('dox_w', 'fina', 'ousna')),
            (('random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('do_w', '', 'ofina', 'ousna'), ('dox_w', 'ofina', 'usna')),
            (('random', '', 'ofina', 'ousna'), ('random_chosen', 'usna')),
        ])

    def test_idc_random_twoplayer(self):
        # Check that /do_idc can result in both options
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('do_idc', '', 'ofina', 'ousna'), ('do_idc_p', 'ofina', 'usna')),  # Relies on seeded RNG
            (('random', '', 'ofina', 'ousna'), ('random_chosen', 'usna')),
            (('do_idc', '', 'fina', 'usna'), ('do_idc_p', 'fina', 'ousna')),  # Relies on seeded RNG
            (('random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('do_idc', '', 'ofina', 'ousna'), ('do_idc_p', 'ofina', 'usna')),  # Relies on seeded RNG
            (('random', '', 'ofina', 'ousna'), ('random_chosen', 'usna')),
            (('do_idc', '', 'fina', 'usna'), ('do_idc_p', 'fina', 'ousna')),  # Relies on seeded RNG
            (('random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('do_idc', '', 'ofina', 'ousna'), ('do_idc_p', 'ofina', 'usna')),  # Relies on seeded RNG
            (('random', '', 'ofina', 'ousna'), ('random_chosen', 'usna')),
            (('do_idc', '', 'fina', 'usna'), ('do_idc_p', 'fina', 'ousna')),  # Relies on seeded RNG
            (('random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('do_idc', '', 'ofina', 'ousna'), ('do_idc_p', 'ofina', 'usna')),  # Relies on seeded RNG
            (('random', '', 'ofina', 'ousna'), ('random_chosen', 'usna')),
            # Finally!
            (('do_idc', '', 'fina', 'usna'), ('do_idc_w', 'fina', 'ousna')),  # Relies on seeded RNG
            (('random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('do_idc', '', 'ofina', 'ousna'), ('do_idc_w', 'ofina', 'usna')),  # Relies on seeded RNG
            (('random', '', 'ofina', 'ousna'), ('random_chosen', 'usna')),
        ])

    def test_true_random_twoplayer(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('true_random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('do_w', '', 'ofina', 'ousna'), ('dox_w', 'ofina', 'usna')),
            (('true_random', '', 'ofina', 'ousna'), ('random_chosen', 'usna')),
            (('do_w', '', 'fina', 'usna'), ('dox_w', 'fina', 'ousna')),
            (('true_random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('do_w', '', 'ofina', 'ousna'), ('dox_w', 'ofina', 'usna')),
            (('true_random', '', 'ofina', 'ousna'), ('random_chosen', 'usna')),
        ])

    def test_random_chosen_left(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina2', 'usna2'), ('leave_chosen_flee', 'fina2', 'usna1')),  # ← 'chosen' leaves!
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna3')),  # chooser tries again
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina2', 'usna2'), ('leave_chosen_flee', 'fina2', 'usna1')),  # ← 'chosen' leaves!
            (('random', '', 'fina3', 'usna3'), ('random_chosen', 'usna1')),  # someone else tries again
        ])

    def test_true_random_chosen_left(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('true_random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina2', 'usna2'), ('leave_chosen_flee', 'fina2', 'usna1')),  # ← 'chosen' leaves!
            (('true_random', '', 'fina1', 'usna1'), ('random_chosen', 'usna3')),  # chooser tries again
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('true_random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina2', 'usna2'), ('leave_chosen_flee', 'fina2', 'usna1')),  # ← 'chosen' leaves!
            (('true_random', '', 'fina3', 'usna3'), ('random_chosen', 'usna1')),  # someone else tries again
        ])

    def test_random_chooser_left(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina1', 'usna1'), ('leave_chooser_handover', 'fina1', 'usna2')),  # ← 'chooser' leaves!
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna3')),  # chosen continues game
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina1', 'usna1'), ('leave_chooser_handover', 'fina1', 'usna2')),  # ← 'chooser' leaves!
            (('random', '', 'fina3', 'usna3'), ('random_chosen', 'usna2')),  # someone else tries again
        ])

    def test_true_random_chooser_left(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('true_random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina1', 'usna1'), ('leave_chooser_handover', 'fina1', 'usna2')),  # ← 'chooser' leaves!
            (('true_random', '', 'fina2', 'usna2'), ('random_chosen', 'usna3')),  # chosen continues game
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('true_random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina1', 'usna1'), ('leave_chooser_handover', 'fina1', 'usna2')),  # ← 'chooser' leaves!
            (('true_random', '', 'fina3', 'usna3'), ('random_chosen', 'usna2')),  # someone else tries again
        ])

    def test_random_wrong(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('random', '', 'fina3', 'usna3'), ('random_not_involved', 'fina3', 'fina1', 'usna2')),  # Not your turn!
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('random', '', 'fina1', 'usna1'), ('random_already_chosen', 'fina1', 'usna2')),  # Already chosen!
        ])

    def test_random_several(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna3')),  # Relies on seeded RNG
            (('do_w', '', 'fina3', 'usna3'), ('dox_w', 'fina3', 'usna1')),
            (('random', '', 'fina3', 'usna3'), ('random_chosen', 'usna2')),  # Relies on seeded RNG
        ])

    def test_show_random_several(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 18), ('usna3', 18)]")),
            (('show_random', 'usna1', 'fina1', 'usna1'), ('debug1', "[('usna2', 18), ('usna3', 18)]")),
            (('show_random', 'usna2', 'fina1', 'usna1'), ('debug1', "[('usna1', 18), ('usna3', 18)]")),
            (('show_random', 'usna3', 'fina1', 'usna1'), ('debug1', "[('usna1', 18), ('usna2', 18)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 18), ('usna2', 18)]")),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna3')),  # Relies on seeded RNG
            (('do_w', '', 'fina3', 'usna3'), ('dox_w', 'fina3', 'usna1')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "random:\n- usna2: 18 Lose (also 50%)\n- usna3: 18 Lose (also 50%)")),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 32), ('usna3', 0)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 25), ('usna3', 9)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 25), ('usna2', 25)]")),  # <- The important one
            (('random', '', 'fina3', 'usna3'), ('random_chosen', 'usna2')),  # Relies on seeded RNG
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna3')),
            (('whytho', '', 'fina2', 'usna2'), ('debug1', "random:\n- usna1: 25 Lose (also 50%)\n- usna2: 25 Lose (also 50%)")),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 16), ('usna3', 1)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 34), ('usna3', 10)]")),  # <- The important one
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 41), ('usna2', 0)]")),
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna1')),  # Relies on seeded RNG
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('whytho', '', 'fina2', 'usna2'), ('debug1', "random:\n- usna3: 10 Lose (also 23%)\n- usna1: 34 Lose (also 77%)")),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 17), ('usna3', 4)]")),  # <- The important one
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 0), ('usna3', 20)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 16), ('usna2', 1)]")),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),  # Relies on seeded RNG
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 0), ('usna3', 10)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 1), ('usna3', 25)]")),  # <- The important one
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 17), ('usna2', 0)]")),
        ])

    @unittest.skip('Not an actual test, just generates test data, must be sanity-checked by human')
    def test_make_reference(self):
        game = logic.OngoingGame('Static seed for reproducible randomness, do not change')
        current_player = 'usna1'
        def observe(*tuple_in):
            tuple_out = logic.handle(game, *tuple_in)
            print(f'            {(tuple_in, tuple_out)},', end='')
            if tuple_in[0] == 'show_random' and tuple_in[3] == current_player:
                print('  # <- The important one', end='')
            print()
            return tuple_out
        num_players = 5
        num_turns = 40
        for i in range(1, num_players + 1):
            observe('join', '', f'fina{i}', f'usna{i}')
        player_sequence = [current_player.replace('usna', '')]
        for step in range(num_turns):
            for i in range(1, num_players + 1):
                observe('show_random', '', f'fina{i}', f'usna{i}')
            tuple_out = observe('random', '', current_player.replace('usna', 'fina'), current_player)
            assert tuple_out[0] == 'random_chosen'
            observe('do_w', '', current_player.replace('usna', 'fina'), tuple_out[1])
            current_player = tuple_out[1]
            player_sequence.append(current_player.replace('usna', ''))
        print(f'            # Sequence: {" ".join(player_sequence)}')

    def test_show_random_many(self):
        # Use test_make_reference to generate, then sanity-check by hand!
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('join', '', 'fina4', 'usna4'), ('welcome', 'fina4')),
            (('join', '', 'fina5', 'usna5'), ('welcome', 'fina5')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 18), ('usna3', 18), ('usna4', 18), ('usna5', 18)]")),  # <- The important one
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 18), ('usna3', 18), ('usna4', 18), ('usna5', 18)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 18), ('usna2', 18), ('usna4', 18), ('usna5', 18)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 18), ('usna2', 18), ('usna3', 18), ('usna5', 18)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 18), ('usna2', 18), ('usna3', 18), ('usna4', 18)]")),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna3')),
            (('do_w', '', 'fina1', 'usna3'), ('dox_w', 'fina1', 'usna1')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 32), ('usna3', 0), ('usna4', 32), ('usna5', 32)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 25), ('usna3', 9), ('usna4', 25), ('usna5', 25)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 25), ('usna2', 25), ('usna4', 25), ('usna5', 25)]")),  # <- The important one
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 25), ('usna2', 25), ('usna3', 9), ('usna5', 25)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 25), ('usna2', 25), ('usna3', 9), ('usna4', 25)]")),
            (('random', '', 'fina3', 'usna3'), ('random_chosen', 'usna5')),
            (('do_w', '', 'fina3', 'usna5'), ('dox_w', 'fina3', 'usna3')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 41), ('usna3', 1), ('usna4', 41), ('usna5', 16)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 34), ('usna3', 10), ('usna4', 34), ('usna5', 9)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 41), ('usna2', 41), ('usna4', 41), ('usna5', 0)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 34), ('usna2', 34), ('usna3', 10), ('usna5', 9)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 34), ('usna2', 34), ('usna3', 10), ('usna4', 34)]")),  # <- The important one
            (('random', '', 'fina5', 'usna5'), ('random_chosen', 'usna2')),
            (('do_w', '', 'fina5', 'usna2'), ('dox_w', 'fina5', 'usna5')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 16), ('usna3', 4), ('usna4', 52), ('usna5', 17)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 45), ('usna3', 13), ('usna4', 45), ('usna5', 10)]")),  # <- The important one
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 52), ('usna2', 16), ('usna4', 52), ('usna5', 1)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 45), ('usna2', 9), ('usna3', 13), ('usna5', 10)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 52), ('usna2', 0), ('usna3', 20), ('usna4', 52)]")),
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna4')),
            (('do_w', '', 'fina2', 'usna4'), ('dox_w', 'fina2', 'usna2')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 17), ('usna3', 9), ('usna4', 16), ('usna5', 20)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 65), ('usna3', 25), ('usna4', 0), ('usna5', 20)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 65), ('usna2', 17), ('usna4', 16), ('usna5', 4)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 58), ('usna2', 10), ('usna3', 18), ('usna5', 13)]")),  # <- The important one
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 65), ('usna2', 1), ('usna3', 25), ('usna4', 16)]")),
            (('random', '', 'fina4', 'usna4'), ('random_chosen', 'usna3')),
            (('do_w', '', 'fina4', 'usna3'), ('dox_w', 'fina4', 'usna4')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 20), ('usna3', 0), ('usna4', 17), ('usna5', 25)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 80), ('usna3', 16), ('usna4', 1), ('usna5', 25)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 80), ('usna2', 20), ('usna4', 17), ('usna5', 9)]")),  # <- The important one
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 80), ('usna2', 20), ('usna3', 0), ('usna5', 25)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 80), ('usna2', 4), ('usna3', 16), ('usna4', 17)]")),
            (('random', '', 'fina3', 'usna3'), ('random_chosen', 'usna1')),
            (('do_w', '', 'fina3', 'usna1'), ('dox_w', 'fina3', 'usna3')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 25), ('usna3', 1), ('usna4', 20), ('usna5', 32)]")),  # <- The important one
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 16), ('usna3', 17), ('usna4', 4), ('usna5', 32)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 0), ('usna2', 34), ('usna4', 29), ('usna5', 17)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 16), ('usna2', 25), ('usna3', 1), ('usna5', 32)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 16), ('usna2', 9), ('usna3', 17), ('usna4', 20)]")),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('do_w', '', 'fina1', 'usna2'), ('dox_w', 'fina1', 'usna1')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 0), ('usna3', 5), ('usna4', 34), ('usna5', 50)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 17), ('usna3', 20), ('usna4', 9), ('usna5', 41)]")),  # <- The important one
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 1), ('usna2', 25), ('usna4', 34), ('usna5', 26)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 17), ('usna2', 16), ('usna3', 4), ('usna5', 41)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 17), ('usna2', 0), ('usna3', 20), ('usna4', 25)]")),
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna1')),
            (('do_w', '', 'fina2', 'usna1'), ('dox_w', 'fina2', 'usna2')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 1), ('usna3', 10), ('usna4', 41), ('usna5', 61)]")),  # <- The important one
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 0), ('usna3', 34), ('usna4', 17), ('usna5', 61)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 0), ('usna2', 26), ('usna4', 41), ('usna5', 37)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 16), ('usna2', 17), ('usna3', 9), ('usna5', 52)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 16), ('usna2', 1), ('usna3', 25), ('usna4', 32)]")),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna5')),
            (('do_w', '', 'fina1', 'usna5'), ('dox_w', 'fina1', 'usna1')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 5), ('usna3', 20), ('usna4', 61), ('usna5', 0)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 1), ('usna3', 41), ('usna4', 26), ('usna5', 25)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 1), ('usna2', 29), ('usna4', 50), ('usna5', 1)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 17), ('usna2', 20), ('usna3', 16), ('usna5', 16)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 17), ('usna2', 4), ('usna3', 32), ('usna4', 41)]")),  # <- The important one
            (('random', '', 'fina5', 'usna5'), ('random_chosen', 'usna4')),
            (('do_w', '', 'fina5', 'usna4'), ('dox_w', 'fina5', 'usna5')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 10), ('usna3', 29), ('usna4', 36), ('usna5', 1)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 4), ('usna3', 50), ('usna4', 1), ('usna5', 26)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 4), ('usna2', 34), ('usna4', 25), ('usna5', 2)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 20), ('usna2', 25), ('usna3', 25), ('usna5', 17)]")),  # <- The important one
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 29), ('usna2', 10), ('usna3', 50), ('usna4', 0)]")),
            (('random', '', 'fina4', 'usna4'), ('random_chosen', 'usna5')),
            (('do_w', '', 'fina4', 'usna5'), ('dox_w', 'fina4', 'usna4')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 17), ('usna3', 40), ('usna4', 37), ('usna5', 0)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 9), ('usna3', 61), ('usna4', 2), ('usna5', 25)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 9), ('usna2', 41), ('usna4', 26), ('usna5', 1)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 34), ('usna2', 41), ('usna3', 37), ('usna5', 0)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 34), ('usna2', 17), ('usna3', 61), ('usna4', 1)]")),  # <- The important one
            (('random', '', 'fina5', 'usna5'), ('random_chosen', 'usna3')),
            (('do_w', '', 'fina5', 'usna3'), ('dox_w', 'fina5', 'usna5')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 26), ('usna3', 4), ('usna4', 40), ('usna5', 1)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 16), ('usna3', 25), ('usna4', 5), ('usna5', 26)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 16), ('usna2', 50), ('usna4', 29), ('usna5', 2)]")),  # <- The important one
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 41), ('usna2', 50), ('usna3', 1), ('usna5', 1)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 52), ('usna2', 29), ('usna3', 0), ('usna4', 5)]")),
            (('random', '', 'fina3', 'usna3'), ('random_chosen', 'usna2')),
            (('do_w', '', 'fina3', 'usna2'), ('dox_w', 'fina3', 'usna3')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 1), ('usna3', 5), ('usna4', 45), ('usna5', 4)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 25), ('usna3', 26), ('usna4', 10), ('usna5', 29)]")),  # <- The important one
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 26), ('usna2', 0), ('usna4', 45), ('usna5', 8)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 50), ('usna2', 25), ('usna3', 2), ('usna5', 4)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 61), ('usna2', 4), ('usna3', 1), ('usna4', 10)]")),
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna3')),
            (('do_w', '', 'fina2', 'usna3'), ('dox_w', 'fina2', 'usna2')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 2), ('usna3', 4), ('usna4', 52), ('usna5', 9)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 37), ('usna3', 0), ('usna4', 20), ('usna5', 45)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 37), ('usna2', 1), ('usna4', 52), ('usna5', 13)]")),  # <- The important one
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 61), ('usna2', 26), ('usna3', 1), ('usna5', 9)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 72), ('usna2', 5), ('usna3', 0), ('usna4', 17)]")),
            (('random', '', 'fina3', 'usna3'), ('random_chosen', 'usna4')),
            (('do_w', '', 'fina3', 'usna4'), ('dox_w', 'fina3', 'usna3')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 5), ('usna3', 5), ('usna4', 36), ('usna5', 16)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 50), ('usna3', 1), ('usna4', 4), ('usna5', 52)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 53), ('usna2', 5), ('usna4', 0), ('usna5', 25)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 74), ('usna2', 29), ('usna3', 2), ('usna5', 16)]")),  # <- The important one
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 85), ('usna2', 8), ('usna3', 1), ('usna4', 1)]")),
            (('random', '', 'fina4', 'usna4'), ('random_chosen', 'usna1')),
            (('do_w', '', 'fina4', 'usna1'), ('dox_w', 'fina4', 'usna4')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 10), ('usna3', 8), ('usna4', 37), ('usna5', 25)]")),  # <- The important one
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 1), ('usna3', 4), ('usna4', 5), ('usna5', 61)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 4), ('usna2', 10), ('usna4', 1), ('usna5', 34)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 0), ('usna2', 45), ('usna3', 8), ('usna5', 26)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 36), ('usna2', 13), ('usna3', 4), ('usna4', 2)]")),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna4')),
            (('do_w', '', 'fina1', 'usna4'), ('dox_w', 'fina1', 'usna1')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 20), ('usna3', 18), ('usna4', 0), ('usna5', 37)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 2), ('usna3', 9), ('usna4', 4), ('usna5', 72)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 5), ('usna2', 17), ('usna4', 0), ('usna5', 45)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 1), ('usna2', 52), ('usna3', 13), ('usna5', 37)]")),  # <- The important one
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 37), ('usna2', 20), ('usna3', 9), ('usna4', 1)]")),
            (('random', '', 'fina4', 'usna4'), ('random_chosen', 'usna2')),
            (('do_w', '', 'fina4', 'usna2'), ('dox_w', 'fina4', 'usna4')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 4), ('usna3', 25), ('usna4', 1), ('usna5', 50)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 5), ('usna3', 16), ('usna4', 5), ('usna5', 85)]")),  # <- The important one
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 8), ('usna2', 1), ('usna4', 1), ('usna5', 58)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 5), ('usna2', 0), ('usna3', 25), ('usna5', 53)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 40), ('usna2', 4), ('usna3', 16), ('usna4', 2)]")),
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna5')),
            (('do_w', '', 'fina2', 'usna5'), ('dox_w', 'fina2', 'usna2')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 5), ('usna3', 34), ('usna4', 4), ('usna5', 1)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 13), ('usna3', 26), ('usna4', 13), ('usna5', 0)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 13), ('usna2', 2), ('usna4', 4), ('usna5', 9)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 10), ('usna2', 1), ('usna3', 34), ('usna5', 4)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 45), ('usna2', 5), ('usna3', 25), ('usna4', 5)]")),  # <- The important one
            (('random', '', 'fina5', 'usna5'), ('random_chosen', 'usna3')),
            (('do_w', '', 'fina5', 'usna3'), ('dox_w', 'fina5', 'usna5')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 8), ('usna3', 9), ('usna4', 9), ('usna5', 2)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 20), ('usna3', 1), ('usna4', 18), ('usna5', 1)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 20), ('usna2', 5), ('usna4', 9), ('usna5', 10)]")),  # <- The important one
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 17), ('usna2', 4), ('usna3', 9), ('usna5', 5)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 65), ('usna2', 13), ('usna3', 0), ('usna4', 13)]")),
            (('random', '', 'fina3', 'usna3'), ('random_chosen', 'usna5')),
            (('do_w', '', 'fina3', 'usna5'), ('dox_w', 'fina3', 'usna3')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 13), ('usna3', 10), ('usna4', 16), ('usna5', 1)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 29), ('usna3', 2), ('usna4', 25), ('usna5', 0)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 34), ('usna2', 13), ('usna4', 17), ('usna5', 0)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 26), ('usna2', 9), ('usna3', 10), ('usna5', 4)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 74), ('usna2', 18), ('usna3', 1), ('usna4', 20)]")),  # <- The important one
            (('random', '', 'fina5', 'usna5'), ('random_chosen', 'usna1')),
            (('do_w', '', 'fina5', 'usna1'), ('dox_w', 'fina5', 'usna5')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 20), ('usna3', 13), ('usna4', 25), ('usna5', 2)]")),  # <- The important one
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 4), ('usna3', 5), ('usna4', 34), ('usna5', 1)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 9), ('usna2', 20), ('usna4', 26), ('usna5', 1)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 1), ('usna2', 16), ('usna3', 13), ('usna5', 5)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 0), ('usna2', 32), ('usna3', 5), ('usna4', 34)]")),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna4')),
            (('do_w', '', 'fina1', 'usna4'), ('dox_w', 'fina1', 'usna1')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 34), ('usna3', 25), ('usna4', 0), ('usna5', 8)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 5), ('usna3', 10), ('usna4', 9), ('usna5', 4)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 10), ('usna2', 29), ('usna4', 1), ('usna5', 4)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 2), ('usna2', 25), ('usna3', 18), ('usna5', 8)]")),  # <- The important one
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 1), ('usna2', 41), ('usna3', 10), ('usna4', 9)]")),
            (('random', '', 'fina4', 'usna4'), ('random_chosen', 'usna3')),
            (('do_w', '', 'fina4', 'usna3'), ('dox_w', 'fina4', 'usna4')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 45), ('usna3', 16), ('usna4', 1), ('usna5', 13)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 8), ('usna3', 1), ('usna4', 10), ('usna5', 9)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 13), ('usna2', 40), ('usna4', 2), ('usna5', 9)]")),  # <- The important one
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 8), ('usna2', 37), ('usna3', 0), ('usna5', 18)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 4), ('usna2', 52), ('usna3', 1), ('usna4', 10)]")),
            (('random', '', 'fina3', 'usna3'), ('random_chosen', 'usna2')),
            (('do_w', '', 'fina3', 'usna2'), ('dox_w', 'fina3', 'usna3')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 9), ('usna3', 17), ('usna4', 4), ('usna5', 20)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 13), ('usna3', 2), ('usna4', 13), ('usna5', 16)]")),  # <- The important one
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 25), ('usna2', 0), ('usna4', 8), ('usna5', 17)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 13), ('usna2', 1), ('usna3', 1), ('usna5', 25)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 9), ('usna2', 16), ('usna3', 2), ('usna4', 13)]")),
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna1')),
            (('do_w', '', 'fina2', 'usna1'), ('dox_w', 'fina2', 'usna2')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 10), ('usna3', 20), ('usna4', 9), ('usna5', 29)]")),  # <- The important one
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 0), ('usna3', 8), ('usna4', 25), ('usna5', 26)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 16), ('usna2', 1), ('usna4', 13), ('usna5', 26)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 4), ('usna2', 2), ('usna3', 4), ('usna5', 34)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 0), ('usna2', 17), ('usna3', 5), ('usna4', 18)]")),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna5')),
            (('do_w', '', 'fina1', 'usna5'), ('dox_w', 'fina1', 'usna1')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 20), ('usna3', 34), ('usna4', 17), ('usna5', 0)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 1), ('usna3', 13), ('usna4', 32), ('usna5', 1)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 17), ('usna2', 4), ('usna4', 20), ('usna5', 1)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 5), ('usna2', 5), ('usna3', 9), ('usna5', 9)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 1), ('usna2', 20), ('usna3', 10), ('usna4', 25)]")),  # <- The important one
            (('random', '', 'fina5', 'usna5'), ('random_chosen', 'usna4')),
            (('do_w', '', 'fina5', 'usna4'), ('dox_w', 'fina5', 'usna5')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 25), ('usna3', 41), ('usna4', 1), ('usna5', 1)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 4), ('usna3', 20), ('usna4', 16), ('usna5', 2)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 20), ('usna2', 9), ('usna4', 4), ('usna5', 2)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 8), ('usna2', 10), ('usna3', 16), ('usna5', 10)]")),  # <- The important one
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 5), ('usna2', 34), ('usna3', 20), ('usna4', 0)]")),
            (('random', '', 'fina4', 'usna4'), ('random_chosen', 'usna3')),
            (('do_w', '', 'fina4', 'usna3'), ('dox_w', 'fina4', 'usna4')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 32), ('usna3', 25), ('usna4', 2), ('usna5', 4)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 9), ('usna3', 4), ('usna4', 17), ('usna5', 5)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 25), ('usna2', 16), ('usna4', 5), ('usna5', 5)]")),  # <- The important one
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 18), ('usna2', 20), ('usna3', 0), ('usna5', 20)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 10), ('usna2', 41), ('usna3', 4), ('usna4', 1)]")),
            (('random', '', 'fina3', 'usna3'), ('random_chosen', 'usna2')),
            (('do_w', '', 'fina3', 'usna2'), ('dox_w', 'fina3', 'usna3')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 16), ('usna3', 26), ('usna4', 5), ('usna5', 9)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 16), ('usna3', 5), ('usna4', 20), ('usna5', 10)]")),  # <- The important one
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 41), ('usna2', 0), ('usna4', 13), ('usna5', 13)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 25), ('usna2', 4), ('usna3', 1), ('usna5', 25)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 17), ('usna2', 25), ('usna3', 5), ('usna4', 4)]")),
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna1')),
            (('do_w', '', 'fina2', 'usna1'), ('dox_w', 'fina2', 'usna2')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 17), ('usna3', 29), ('usna4', 10), ('usna5', 16)]")),  # <- The important one
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 0), ('usna3', 13), ('usna4', 34), ('usna5', 20)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 25), ('usna2', 1), ('usna4', 18), ('usna5', 20)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 9), ('usna2', 5), ('usna3', 4), ('usna5', 32)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 1), ('usna2', 26), ('usna3', 8), ('usna4', 9)]")),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('do_w', '', 'fina1', 'usna2'), ('dox_w', 'fina1', 'usna1')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 0), ('usna3', 45), ('usna4', 20), ('usna5', 26)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 1), ('usna3', 18), ('usna4', 41), ('usna5', 29)]")),  # <- The important one
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 26), ('usna2', 0), ('usna4', 25), ('usna5', 29)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 10), ('usna2', 4), ('usna3', 9), ('usna5', 41)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 2), ('usna2', 25), ('usna3', 13), ('usna4', 16)]")),
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna4')),
            (('do_w', '', 'fina2', 'usna4'), ('dox_w', 'fina2', 'usna2')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 1), ('usna3', 52), ('usna4', 4), ('usna5', 37)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 5), ('usna3', 32), ('usna4', 0), ('usna5', 45)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 29), ('usna2', 1), ('usna4', 9), ('usna5', 40)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 13), ('usna2', 5), ('usna3', 16), ('usna5', 52)]")),  # <- The important one
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 5), ('usna2', 26), ('usna3', 20), ('usna4', 0)]")),
            (('random', '', 'fina4', 'usna4'), ('random_chosen', 'usna5')),
            (('do_w', '', 'fina4', 'usna5'), ('dox_w', 'fina4', 'usna4')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 4), ('usna3', 61), ('usna4', 5), ('usna5', 1)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 10), ('usna3', 41), ('usna4', 1), ('usna5', 9)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 34), ('usna2', 4), ('usna4', 10), ('usna5', 4)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 25), ('usna2', 13), ('usna3', 26), ('usna5', 0)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 10), ('usna2', 29), ('usna3', 29), ('usna4', 1)]")),  # <- The important one
            (('random', '', 'fina5', 'usna5'), ('random_chosen', 'usna3')),
            (('do_w', '', 'fina5', 'usna3'), ('dox_w', 'fina5', 'usna5')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 9), ('usna3', 36), ('usna4', 8), ('usna5', 2)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 17), ('usna3', 16), ('usna4', 4), ('usna5', 10)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 41), ('usna2', 9), ('usna4', 13), ('usna5', 5)]")),  # <- The important one
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 32), ('usna2', 18), ('usna3', 1), ('usna5', 1)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 20), ('usna2', 45), ('usna3', 0), ('usna4', 5)]")),
            (('random', '', 'fina3', 'usna3'), ('random_chosen', 'usna1')),
            (('do_w', '', 'fina3', 'usna1'), ('dox_w', 'fina3', 'usna3')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 16), ('usna3', 37), ('usna4', 13), ('usna5', 5)]")),  # <- The important one
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 1), ('usna3', 17), ('usna4', 9), ('usna5', 13)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 0), ('usna2', 17), ('usna4', 25), ('usna5', 13)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 16), ('usna2', 25), ('usna3', 2), ('usna5', 4)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 4), ('usna2', 52), ('usna3', 1), ('usna4', 10)]")),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna4')),
            (('do_w', '', 'fina1', 'usna4'), ('dox_w', 'fina1', 'usna1')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 26), ('usna3', 53), ('usna4', 0), ('usna5', 13)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 2), ('usna3', 20), ('usna4', 0), ('usna5', 18)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 1), ('usna2', 26), ('usna4', 16), ('usna5', 18)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 17), ('usna2', 34), ('usna3', 5), ('usna5', 9)]")),  # <- The important one
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 5), ('usna2', 61), ('usna3', 4), ('usna4', 1)]")),
            (('random', '', 'fina4', 'usna4'), ('random_chosen', 'usna2')),
            (('do_w', '', 'fina4', 'usna2'), ('dox_w', 'fina4', 'usna4')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 1), ('usna3', 58), ('usna4', 1), ('usna5', 20)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 5), ('usna3', 25), ('usna4', 1), ('usna5', 25)]")),  # <- The important one
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 4), ('usna2', 1), ('usna4', 17), ('usna5', 25)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 29), ('usna2', 0), ('usna3', 13), ('usna5', 17)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 8), ('usna2', 36), ('usna3', 9), ('usna4', 2)]")),
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna5')),
            (('do_w', '', 'fina2', 'usna5'), ('dox_w', 'fina2', 'usna2')),
            (('show_random', '', 'fina1', 'usna1'), ('debug1', "[('usna2', 2), ('usna3', 65), ('usna4', 4), ('usna5', 4)]")),
            (('show_random', '', 'fina2', 'usna2'), ('debug1', "[('usna1', 13), ('usna3', 41), ('usna4', 5), ('usna5', 0)]")),
            (('show_random', '', 'fina3', 'usna3'), ('debug1', "[('usna1', 9), ('usna2', 2), ('usna4', 20), ('usna5', 9)]")),
            (('show_random', '', 'fina4', 'usna4'), ('debug1', "[('usna1', 34), ('usna2', 1), ('usna3', 20), ('usna5', 1)]")),
            (('show_random', '', 'fina5', 'usna5'), ('debug1', "[('usna1', 13), ('usna2', 37), ('usna3', 16), ('usna4', 5)]")),  # <- The important one
            (('random', '', 'fina5', 'usna5'), ('random_chosen', 'usna3')),
            (('do_w', '', 'fina5', 'usna3'), ('dox_w', 'fina5', 'usna5')),
            # Sequence: 1 3 5 2 4 3 1 2 1 5 4 5 3 2 3 4 1 4 2 5 3 5 1 4 3 2 1 5 4 3 2 1 2 4 5 3 1 4 2 5 3
        ])

    def test_true_random_several(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('true_random', '', 'fina1', 'usna1'), ('random_chosen', 'usna3')),  # Relies on seeded RNG
            (('do_w', '', 'fina3', 'usna3'), ('dox_w', 'fina3', 'usna1')),
            (('true_random', '', 'fina3', 'usna3'), ('random_chosen', 'usna2')),  # Relies on seeded RNG
        ])

    def test_whytho(self):
        self.check_sequence([
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "dunno")),
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "dunno")),
            (('whytho', '', 'fina2', 'usna2'), ('debug1', "dunno")),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "random:\n- usna2: 18 Lose (also 100%)")),
            (('true_random', '', 'fina2', 'usna2'), ('random_chosen', 'usna1')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "true_random['fina1']")),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "choose")),
        ])

    def test_whytho_lowprob_1choose(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna3')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "random:\n- usna1: 25 Lose (also 50%)\n- usna3: 25 Lose (also 50%)")),  # 50%
        ])

    def test_whytho_lowprob_2choose(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna3')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "random:\n- usna2: 1 Los (also 2.4%)\n- usna3: 41 Lose (also 98%)")),  # 2.38%
        ])

    def test_whytho_lowprob_3choose(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna3')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "random:\n- usna1: 1 Los (also 1.9%)\n- usna3: 52 Lose (also 98%)")),  # 1.887%
        ])

    def test_whytho_lowprob_4choose(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna3')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "random:\n- usna2: 1 Los (also 1.3%)\n- usna3: 74 Lose (also 99%)")),  # 1.333%
        ])

    def test_whytho_lowprob_5choose(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna3')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "random:\n- usna1: 1 Los (also 1.1%)\n- usna3: 89 Lose (also 99%)")),  # 1.111%
        ])

    def test_whytho_lowprob_6choose(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna3')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "random:\n- usna2: 1 Los (also 0.85%)\n- usna3: 117 Lose (also 99%)")),  # 0.8475%
        ])

    def test_whytho_lowprob_7choose(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna3')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "random:\n- usna1: 1 Los (also 0.73%)\n- usna3: 136 Lose (also 99%)")),  # 0.72993%
        ])

    def test_whytho_lowprob_8choose(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna3')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "random:\n- usna2: 1 Los (also 0.58%)\n- usna3: 170 Lose (also 99%)")),  # 0.5848%
        ])

    def test_whytho_lowprob_9choose(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna3')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "random:\n- usna1: 1 Los (also 0.52%)\n- usna3: 193 Lose (also 99%)")),  # 0.51546%
        ])

    def test_whytho_lowprob_60choose(self):
        # In order to get close to 0.1%, have to repeat a surprisingly high number of iterations:
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            *(
                (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
                (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
                (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
                (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            ) * 30,
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna3')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "random:\n- usna2: 1 Los (also 0.02%)\n- usna3: 5058 Lose (also 100%)")),  # 0.019767%
        ])

    def test_whytho_lowprob_86choose(self):
        # In order to go below 0.01%, have to repeat a surprisingly high number of iterations:
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            *(
                (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
                (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
                (('choose', 'usna1', 'fina2', 'usna2'), ('chosen_chosen', 'usna1', 'fina2')),
                (('do_w', '', 'fina1', 'usna1'), ('dox_w', 'fina1', 'usna2')),
            ) * 43,
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna3')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "random:\n- usna2: 1 Los (also <0.01%, holy shit!)\n- usna3: 10037 Lose (also 100%)")),  # 0.0099621%
        ])

    def test_idc_whytho(self):
        self.check_sequence([
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "dunno")),
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "dunno")),
            (('whytho', '', 'fina2', 'usna2'), ('debug1', "dunno")),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('do_idc', '', 'fina2', 'usna2'), ('do_idc_p', 'fina2', 'usna1')),  # Relies on seeded RNG
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "random:\n- usna2: 18 Lose (also 100%)")),
            (('true_random', '', 'fina2', 'usna2'), ('random_chosen', 'usna1')),
            (('do_idc', '', 'fina1', 'usna1'), ('do_idc_p', 'fina1', 'usna2')),  # Relies on seeded RNG
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "true_random['fina1']")),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('whytho', '', 'fina1', 'usna1'), ('debug1', "choose")),
        ])

    def test_wop_nonplayer(self):
        self.check_sequence([
            (('wop', '', 'fina', 'usna'), ('nonplayer', 'fina')),
        ])

    def test_wop_nobodychosen(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('wop', '', 'fina', 'usna'), ('wop_nobodychosen', 'fina', 'Pflicht')),  # Relies on seeded RNG
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('leave', '', 'fina2', 'usna2'), ('leave_chosen_flee', 'fina2', 'usna1')),
            (('wop', '', 'fina1', 'usna1'), ('wop_nobodychosen', 'fina1', 'Pflicht')),  # Relies on seeded RNG
        ])

    def test_wop_nonchosen(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('wop', '', 'fina1', 'usna1'), ('wop_nonchosen', 'fina1', 'usna2')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('leave', '', 'fina1', 'usna1'), ('leave_chooser_handover', 'fina1', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('wop', '', 'fina3', 'usna3'), ('wop_nonchosen', 'fina3', 'usna2')),
        ])

    def test_wop_regular(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('wop', '', 'fina2', 'usna2'), ('wop_result_p', 'fina2', 'usna1')),  # Relies on seeded RNG
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('leave', '', 'fina1', 'usna1'), ('leave_chooser_handover', 'fina1', 'usna2')),
            (('wop', '', 'fina2', 'usna2'), ('dox_no_chooser', 'usna2')),
        ])

    def test_wop_again(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('wop', '', 'fina2', 'usna2'), ('wop_result_p', 'fina2', 'usna1')),  # Relies on seeded RNG
            (('wop', '', 'fina2', 'usna2'), ('wop_again', 'fina2', 'Pflicht', 'usna1')),  # Must be the same result
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('wop', '', 'fina2', 'usna2'), ('wop_result_p', 'fina2', 'usna1')),  # Relies on seeded RNG
            (('leave', '', 'fina1', 'usna1'), ('leave_chooser_handover', 'fina1', 'usna2')),
            (('wop', '', 'fina2', 'usna2'), ('wop_again', 'fina2', 'Pflicht', '???')),  # Must be the same result
        ])

    def test_who_error(self):
        self.check_sequence([
            (('who', '', 'qfina', 'qusna'), ('who_nobody', 'qfina')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('leave', '', 'fina1', 'usna1'), ('leave_chooser_handover', 'fina1', 'usna2')),
            (('who', '', 'qfina', 'qusna'), ('who_no_chooser', 'qfina', 'usna2')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('leave', '', 'fina2', 'usna2'), ('leave_chosen_flee', 'fina2', 'usna1')),
            (('who', '', 'qfina', 'qusna'), ('who_no_chosen', 'usna1')),
        ])

    def test_who_regular(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('who', '', 'qfina', 'qusna'), ('who_no_wop', 'usna2', 'fina1')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('do_p', '', 'fina2', 'usna2'), ('dox_p', 'fina2', 'usna1')),
            (('who', '', 'qfina', 'qusna'), ('who_wop_p', 'fina1', 'usna2')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('who', '', 'qfina', 'qusna'), ('who_wop_w', 'fina1', 'usna2')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('do_idc', '', 'fina2', 'usna2'), ('do_idc_p', 'fina2', 'usna1')),  # Relies on seeded RNG
            (('who', '', 'qfina', 'qusna'), ('who_wop_p', 'fina1', 'usna2')),
        ])

    def test_players_zero(self):
        self.check_sequence([
            (('players', '', 'fina1', 'usna1'), ('players_nobody', 'fina1', secret.MESSAGES_SHEET)),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('leave', '', 'fina1', 'usna1'), ('leave', 'fina1')),
            (('players', '', 'qfina', 'qusna'), ('players_nobody', 'qfina', secret.MESSAGES_SHEET)),
        ])

    def test_players_one(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('players', '', 'fina1', 'usna1'), ('players_one_self', 'fina1', 'fina1', secret.MESSAGES_SHEET)),
            (('players', '', 'fina2', 'usna2'), ('players_one_other', 'fina2', 'fina1', secret.MESSAGES_SHEET)),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('leave', '', 'fina2', 'usna2'), ('leave', 'fina2')),
            (('players', '', 'fina1', 'usna1'), ('players_one_self', 'fina1', 'fina1', secret.MESSAGES_SHEET)),
            (('players', '', 'fina2', 'usna2'), ('players_one_other', 'fina2', 'fina1', secret.MESSAGES_SHEET)),
        ])

    def test_players_few(self):
        self.check_sequence([
            (('join', '', 'a', 'ua'), ('welcome', 'a')),
            (('join', '', 'b', 'ub'), ('welcome', 'b')),
            (('players', '', 'a', 'ua'), ('players_few_self', 'a', 'a und b')),
            (('players', '', 'xx', 'uxx'), ('players_few_other', 'xx', 'a und b')),
            (('join', '', 'c', 'uc'), ('welcome', 'c')),
            (('players', '', 'a', 'ua'), ('players_few_self', 'a', 'a, b und c')),
            (('players', '', 'xx', 'uxx'), ('players_few_other', 'xx', 'a, b und c')),
            (('join', '', 'd', 'ud'), ('welcome', 'd')),
            (('players', '', 'a', 'ua'), ('players_few_self', 'a', 'a, b, c und d')),
            (('players', '', 'xx', 'uxx'), ('players_few_other', 'xx', 'a, b, c und d')),
        ])

    def test_players_many(self):
        self.check_sequence([
            (('join', '', 'e', 'ue'), ('welcome', 'e')),
            (('join', '', 'd', 'ud'), ('welcome', 'd')),
            (('join', '', 'c', 'uc'), ('welcome', 'c')),
            (('join', '', 'b', 'ub'), ('welcome', 'b')),
            (('join', '', 'a', 'ua'), ('welcome', 'a')),
            (('players', '', 'a', 'ua'), ('players_many_self', 'a', 'a, b, c, d und e', '5')),
            (('players', '', 'xx', 'uxx'), ('players_many_other', 'xx', 'a, b, c, d und e', '5')),
            (('join', '', 'f', 'uf'), ('welcome', 'f')),
            (('players', '', 'a', 'ua'), ('players_many_self', 'a', 'a, b, c, d, e und f', '6')),
            (('players', '', 'xx', 'uxx'), ('players_many_other', 'xx', 'a, b, c, d, e und f', '6')),
        ])

    def test_kick_nonplayer(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('kick', '', 'qfina', 'qusna'), ('kick_nonplayer', 'qfina')),
        ])
        self.check_sequence([
            (('kick', '', 'qfina', 'qusna'), ('kick_nonplayer', 'qfina')),
        ])

    def test_kick_no_chosen(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('kick', '', 'fina1', 'usna1'), ('kick_no_chosen', 'fina1')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('leave', '', 'fina2', 'usna2'), ('leave_chosen_flee', 'fina2', 'usna1')),
            (('kick', '', 'fina1', 'usna1'), ('kick_no_chosen', 'fina1')),
        ])

    def test_kick_regular(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('kick', '', 'fina1', 'usna1'), ('kick', 'fina1', 'usna2')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('kick', '', 'fina2', 'usna2'), ('kick_self', 'fina2')),  # Self-kick is probably unintentional.
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('kick', '', 'fina3', 'usna3'), ('kick', 'fina3', 'usna2')),  # join-kick is okay I guess?
        ])

    def test_kick_regular_function(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('kick', '', 'fina1', 'usna1'), ('kick', 'fina1', 'usna2')),
            (('leave', '', 'fina2', 'usna2'), ('already_left', 'fina2')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('kick', '', 'fina2', 'usna2'), ('kick_self', 'fina2')),  # Doesn't happen!
            (('leave', '', 'fina2', 'usna2'), ('leave_chosen_flee', 'fina2', 'usna1')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('kick', '', 'fina3', 'usna3'), ('kick', 'fina3', 'usna2')),  # join-kick is okay I guess?
            (('leave', '', 'fina2', 'usna2'), ('already_left', 'fina2')),
        ])

    def test_choose_nonplayer(self):
        self.check_sequence([
            (('choose', 'asdf', 'fina', 'usna'), ('nonplayer', 'fina')),
            (('choose', '', 'fina', 'usna'), ('nonplayer', 'fina')),
            (('choose', 'usna', 'fina', 'usna'), ('nonplayer', 'fina')),
        ])

    def test_choose_nonplayer_nonempty(self):
        self.check_sequence([
            (('join', '', 'a', 'a'), ('welcome', 'a')),
            (('join', '', 'b', 'b'), ('welcome', 'b')),
            (('choose', 'asdf', 'fina', 'usna'), ('nonplayer', 'fina')),
            (('choose', '', 'fina', 'usna'), ('nonplayer', 'fina')),
            (('choose', 'usna', 'fina', 'usna'), ('nonplayer', 'fina')),
        ])

    def test_choose_singleplayer(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('choose', 'asdf', 'fina', 'usna'), ('random_singleplayer', 'fina')),
            (('choose', 'asdf', 'fina', 'usna'), ('random_singleplayer', 'fina')),
            (('choose', '', 'fina', 'usna'), ('random_singleplayer', 'fina')),
            (('choose', 'usna', 'fina', 'usna'), ('random_singleplayer', 'fina')),
        ])

    def test_choose_twoplayer(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('choose', 'ousna', 'fina', 'usna'), ('chosen_chosen', 'ousna', 'fina')),
            (('do_w', '', 'ofina', 'ousna'), ('dox_w', 'ofina', 'usna')),
            (('choose', 'usna', 'ofina', 'ousna'), ('chosen_chosen', 'usna', 'ofina')),
            (('do_w', '', 'fina', 'usna'), ('dox_w', 'fina', 'ousna')),
            (('choose', 'ousna', 'fina', 'usna'), ('chosen_chosen', 'ousna', 'fina')),
            (('do_w', '', 'ofina', 'ousna'), ('dox_w', 'ofina', 'usna')),
            (('choose', 'usna', 'ofina', 'ousna'), ('chosen_chosen', 'usna', 'ofina')),
            (('do_w', '', 'fina', 'usna'), ('dox_w', 'fina', 'ousna')),
        ])

    def test_choose_form_at(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('choose', '@ousna', 'fina', 'usna'), ('chosen_chosen', 'ousna', 'fina')),
        ])

    def test_choose_form_fina(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('choose', 'ofina', 'fina', 'usna'), ('chosen_chosen', 'ousna', 'fina')),
        ])

    def test_choose_emptyarg(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('choose', '', 'fina', 'usna'), ('chosen_empty', 'fina', 'usna')),
        ])

    def test_choose_self(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('choose', 'usna', 'fina', 'usna'), ('chosen_self', 'fina')),
        ])

    def test_choose_chosen_left(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina2', 'usna2'), ('leave_chosen_flee', 'fina2', 'usna1')),  # ← 'chosen' leaves!
            (('choose', 'usna3', 'fina1', 'usna1'), ('chosen_chosen', 'usna3', 'fina1')),  # chooser tries again
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina2', 'usna2'), ('leave_chosen_flee', 'fina2', 'usna1')),  # ← 'chosen' leaves!
            (('choose', 'usna1', 'fina3', 'usna3'), ('chosen_chosen', 'usna1', 'fina3')),  # someone else tries again
        ])

    def test_choose_chooser_left(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina1', 'usna1'), ('leave_chooser_handover', 'fina1', 'usna2')),  # ← 'chooser' leaves!
            (('choose', 'usna3', 'fina2', 'usna2'), ('chosen_chosen', 'usna3', 'fina2')),  # chosen continues game, without /wop
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina1', 'usna1'), ('leave_chooser_handover', 'fina1', 'usna2')),  # ← 'chooser' leaves!
            (('choose', 'usna2', 'fina3', 'usna3'), ('chosen_chosen', 'usna2', 'fina3')),  # someone else tries again
        ])

    def test_wop_chooser_left(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina1', 'usna1'), ('leave_chooser_handover', 'fina1', 'usna2')),  # ← 'chooser' leaves!
            (('choose', 'usna3', 'fina2', 'usna2'), ('chosen_chosen', 'usna3', 'fina2')),  # chosen continues game normally
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('leave', '', 'fina1', 'usna1'), ('leave_chooser_handover', 'fina1', 'usna2')),  # ← 'chooser' leaves!
            (('do_w', '', 'fina2', 'usna2'), ('dox_no_chooser', 'usna2')),  # ← 'chooser' has already left, so doing a 'W' doesn't make sense.
            (('do_p', '', 'fina2', 'usna2'), ('dox_no_chooser', 'usna2')),  # same
            (('wop', '', 'fina2', 'usna2'), ('dox_no_chooser', 'usna2')),  # same
            (('do_idc', '', 'fina2', 'usna2'), ('dox_no_chooser', 'usna2')),  # same
        ])

    def test_choose_wrong(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('choose', 'usna1', 'fina3', 'usna3'), ('random_not_involved', 'fina3', 'fina1', 'usna2')),  # Not your turn!
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('choose', 'usna3', 'fina1', 'usna1'), ('random_already_chosen', 'fina1', 'usna2')),  # Already chosen!
        ])

    def test_choose_several(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('choose', 'usna3', 'fina1', 'usna1'), ('chosen_chosen', 'usna3', 'fina1')),
            (('do_w', '', 'fina3', 'usna3'), ('dox_w', 'fina3', 'usna1')),
            (('choose', 'usna2', 'fina3', 'usna3'), ('chosen_chosen', 'usna2', 'fina3')),
        ])

    def test_dox_nonplayer(self):
        self.check_sequence([
            (('do_w', '', 'fina', 'usna'), ('nonplayer', 'fina')),
            (('do_p', '', 'fina', 'usna'), ('nonplayer', 'fina')),
            (('do_idc', '', 'fina', 'usna'), ('nonplayer', 'fina')),
        ])

    def test_dox_nonplayer_nonempty(self):
        self.check_sequence([
            (('join', '', 'a', 'a'), ('welcome', 'a')),
            (('join', '', 'b', 'b'), ('welcome', 'b')),
            (('do_w', '', 'fina', 'usna'), ('nonplayer', 'fina')),
            (('do_p', '', 'fina', 'usna'), ('nonplayer', 'fina')),
            (('do_idc', '', 'fina', 'usna'), ('nonplayer', 'fina')),
        ])

    def test_dox_nobody(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('do_w', '', 'fina', 'usna'), ('dox_choose_first', 'fina')),
            (('do_p', '', 'fina', 'usna'), ('dox_choose_first', 'fina')),
            (('do_idc', '', 'fina', 'usna'), ('dox_choose_first', 'fina')),
        ])

    def test_dox_nochosen(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('leave', '', 'fina2', 'usna2'), ('leave_chosen_flee', 'fina2', 'usna1')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_choose_first', 'fina1')),
            (('do_p', '', 'fina1', 'usna1'), ('dox_choose_first', 'fina1')),
            (('do_idc', '', 'fina1', 'usna1'), ('dox_choose_first', 'fina1')),
        ])

    def test_dox_nochooser(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('leave', '', 'fina1', 'usna1'), ('leave_chooser_handover', 'fina1', 'usna2')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_no_chooser', 'usna2')),
            (('do_p', '', 'fina2', 'usna2'), ('dox_no_chooser', 'usna2')),
            (('do_idc', '', 'fina2', 'usna2'), ('dox_no_chooser', 'usna2')),
        ])

    def test_dox_twoplayer(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('choose', 'ousna', 'fina', 'usna'), ('chosen_chosen', 'ousna', 'fina')),
            (('do_w', '', 'ofina', 'ousna'), ('dox_w', 'ofina', 'usna')),
            (('choose', 'usna', 'ofina', 'ousna'), ('chosen_chosen', 'usna', 'ofina')),
            (('do_p', '', 'fina', 'usna'), ('dox_p', 'fina', 'ousna')),
            (('choose', 'ousna', 'fina', 'usna'), ('chosen_chosen', 'ousna', 'fina')),
            (('do_idc', '', 'ofina', 'ousna'), ('do_idc_p', 'ofina', 'usna')),  # Relies on seeded RNG
        ])

    def test_dox_not_involved(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina3', 'usna3'), ('dox_not_involved', 'fina3', 'usna2', 'fina1')),
            (('do_p', '', 'fina3', 'usna3'), ('dox_not_involved', 'fina3', 'usna2', 'fina1')),
            (('do_idc', '', 'fina3', 'usna3'), ('dox_not_involved', 'fina3', 'usna2', 'fina1')),
        ])

    def test_dox_wrong_side(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_wrong_side', 'fina1', 'usna2')),
            (('do_p', '', 'fina1', 'usna1'), ('dox_wrong_side', 'fina1', 'usna2')),
            (('do_idc', '', 'fina1', 'usna1'), ('dox_wrong_side', 'fina1', 'usna2')),
        ])

    def test_dox_again(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_already_w', 'fina2', 'usna1')),
            (('do_p', '', 'fina2', 'usna2'), ('dox_already_w', 'fina2', 'usna1')),
            (('do_idc', '', 'fina2', 'usna2'), ('dox_already_w', 'fina2', 'usna1')),
            (('wop', '', 'fina2', 'usna2'), ('wop_again', 'fina2', 'Wahrheit', 'usna1')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_p', '', 'fina2', 'usna2'), ('dox_p', 'fina2', 'usna1')),
            (('do_p', '', 'fina2', 'usna2'), ('dox_already_p', 'fina2', 'usna1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_already_p', 'fina2', 'usna1')),
            (('do_idc', '', 'fina2', 'usna2'), ('dox_already_p', 'fina2', 'usna1')),
            (('wop', '', 'fina2', 'usna2'), ('wop_again', 'fina2', 'Pflicht', 'usna1')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('wop', '', 'fina2', 'usna2'), ('wop_result_p', 'fina2', 'usna1')),  # Relies on seeded RNG
            (('do_p', '', 'fina2', 'usna2'), ('dox_already_p', 'fina2', 'usna1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_already_p', 'fina2', 'usna1')),
            (('do_idc', '', 'fina2', 'usna2'), ('dox_already_p', 'fina2', 'usna1')),
        ])

    def test_chicken_negative(self):
        self.check_sequence([
            (('chicken', '', 'fina1', 'usna1'), ('nonplayer', 'fina1')),
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('chicken', '', 'fina1', 'usna1'), ('chicken_not_involved', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('chicken', '', 'fina1', 'usna1'), ('chicken_wrong_side', 'fina1', 'usna2')),
            (('chicken', '', 'fina2', 'usna2'), ('chicken_too_early', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('chicken', '', 'fina3', 'usna3'), ('chicken_not_involved', 'fina3')),
        ])

    def test_chicken_normal(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('chicken', '', 'fina2', 'usna2'), ('chicken_w', secret.MESSAGES_SHEET, secret.OWNER)),
            (('chicken', '', 'fina2', 'usna2'), ('chicken_w', secret.MESSAGES_SHEET, secret.OWNER)),
            (('chicken', '', 'fina2', 'usna2'), ('chicken_w', secret.MESSAGES_SHEET, secret.OWNER)),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_p', '', 'fina2', 'usna2'), ('dox_p', 'fina2', 'usna1')),
            (('chicken', '', 'fina2', 'usna2'), ('chicken_p', secret.MESSAGES_SHEET, secret.OWNER)),
            (('chicken', '', 'fina2', 'usna2'), ('chicken_p', secret.MESSAGES_SHEET, secret.OWNER)),
            (('chicken', '', 'fina2', 'usna2'), ('chicken_p', secret.MESSAGES_SHEET, secret.OWNER)),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_idc', '', 'fina2', 'usna2'), ('do_idc_p', 'fina2', 'usna1')),  # Relies on seeded RNG
            (('chicken', '', 'fina2', 'usna2'), ('chicken_p', secret.MESSAGES_SHEET, secret.OWNER)),
            (('chicken', '', 'fina2', 'usna2'), ('chicken_p', secret.MESSAGES_SHEET, secret.OWNER)),
            (('chicken', '', 'fina2', 'usna2'), ('chicken_p', secret.MESSAGES_SHEET, secret.OWNER)),
        ])

    def test_chicken_wop(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('wop', '', 'fina2', 'usna2'), ('wop_result_p', 'fina2', 'usna1')),  # Relies on seeded RNG!
            (('chicken', '', 'fina2', 'usna2'), ('chicken_p', secret.MESSAGES_SHEET, secret.OWNER)),
            (('chicken', '', 'fina2', 'usna2'), ('chicken_p', secret.MESSAGES_SHEET, secret.OWNER)),
            (('chicken', '', 'fina2', 'usna2'), ('chicken_p', secret.MESSAGES_SHEET, secret.OWNER)),
        ])

    def test_chicken_edgecases(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('wop', '', 'fina2', 'usna2'), ('wop_result_p', 'fina2', 'usna1')),  # Relies on seeded RNG!
            (('leave', '', 'fina2', 'usna2'), ('leave_chosen_flee', 'fina2', 'usna1')),
            # Probably won't happen in real life, so the slightly weird response is okay, but it must not crash here:
            (('chicken', '', 'fina1', 'usna1'), ('chicken_wrong_side', 'fina1', '???')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('chicken', '', 'fina3', 'usna3'), ('chicken_not_involved', 'fina3')),
        ])


if __name__ == '__main__':
    unittest.main()
