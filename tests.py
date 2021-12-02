#!/usr/bin/env python3
# Run as: ./tests.py

import bot  # check whether the file parses
import logic
import unittest


class TestStringMethods(unittest.TestCase):
    def check_sequence(self, sequence):
        game = logic.OngoingGame('Static seed for reproducible randomness, do not change')
        for i, (query, expected_response) in enumerate(sequence):
            with self.subTest(step=i):
                actual_response = logic.handle(game, *query)
                self.assertEqual(expected_response, actual_response)

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

    def test_random_twoplayer(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('random', '', 'ofina', 'ousna'), ('random_chosen', 'usna')),
            (('random', '', 'fina', 'usna'), ('random_chosen', 'ousna')),
            (('random', '', 'ofina', 'ousna'), ('random_chosen', 'usna')),
        ])

    def test_random_chosen_left(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina2', 'usna2'), ('leave', 'fina2')),  # ← 'chosen' leaves!
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna3')),  # chooser tries again
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina2', 'usna2'), ('leave', 'fina2')),  # ← 'chosen' leaves!
            (('random', '', 'fina3', 'usna3'), ('random_chosen', 'usna1')),  # someone else tries again
        ])

    def test_random_chooser_left(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina1', 'usna1'), ('leave', 'fina1')),  # ← 'chooser' leaves!
            (('random', '', 'fina2', 'usna2'), ('random_chosen', 'usna3')),  # chosen continues game
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina1', 'usna1'), ('leave', 'fina1')),  # ← 'chooser' leaves!
            (('random', '', 'fina3', 'usna3'), ('random_chosen', 'usna2')),  # someone else tries again
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
            (('random', '', 'fina3', 'usna3'), ('random_chosen', 'usna2')),  # Relies on seeded RNG
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
            (('leave', '', 'fina2', 'usna2'), ('leave', 'fina2')),
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
            (('leave', '', 'fina1', 'usna1'), ('leave', 'fina1')),
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
            (('leave', '', 'fina1', 'usna1'), ('leave', 'fina1')),
            (('wop', '', 'fina2', 'usna2'), ('wop_result_p', 'fina2', '???')),  # Relies on seeded RNG
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
            (('leave', '', 'fina1', 'usna1'), ('leave', 'fina1')),
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
            (('leave', '', 'fina1', 'usna1'), ('leave', 'fina1')),
            (('who', '', 'qfina', 'qusna'), ('who_no_chooser', 'qfina', 'usna2')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('leave', '', 'fina2', 'usna2'), ('leave', 'fina2')),
            (('who', '', 'qfina', 'qusna'), ('who_no_chosen', 'usna1')),
        ])

    def test_who_regular(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('who', '', 'qfina', 'qusna'), ('who_no_wop', 'usna1', 'usna2')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('wop', '', 'fina2', 'usna2'), ('wop_result_p', 'fina2', 'usna1')),  # Relies on seeded RNG
            (('who', '', 'qfina', 'qusna'), ('who_wop_p', 'fina1', 'usna2')),
        ])

    def test_players_zero(self):
        self.check_sequence([
            (('players', '', 'fina1', 'usna1'), ('players_nobody', 'fina1')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('leave', '', 'fina1', 'usna1'), ('leave', 'fina1')),
            (('players', '', 'qfina', 'qusna'), ('players_nobody', 'qfina')),
        ])

    def test_players_one(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('players', '', 'fina1', 'usna1'), ('players_one_self', 'fina1', 'fina1')),
            (('players', '', 'fina2', 'usna2'), ('players_one_other', 'fina2', 'fina1')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('leave', '', 'fina2', 'usna2'), ('leave', 'fina2')),
            (('players', '', 'fina1', 'usna1'), ('players_one_self', 'fina1', 'fina1')),
            (('players', '', 'fina2', 'usna2'), ('players_one_other', 'fina2', 'fina1')),
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
            (('players', '', 'a', 'ua'), ('players_many_self', 'a', 'a, b, c, d und e')),
            (('players', '', 'xx', 'uxx'), ('players_many_other', 'xx', 'a, b, c, d und e')),
            (('join', '', 'f', 'uf'), ('welcome', 'f')),
            (('players', '', 'a', 'ua'), ('players_many_self', 'a', 'a, b, c, d, e und f')),
            (('players', '', 'xx', 'uxx'), ('players_many_other', 'xx', 'a, b, c, d, e und f')),
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
            (('leave', '', 'fina2', 'usna2'), ('leave', 'fina2')),
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
            (('kick', '', 'fina2', 'usna2'), ('kick', 'fina2', 'usna2')),  # Self-kick is okay I guess?
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('kick', '', 'fina3', 'usna3'), ('kick', 'fina3', 'usna2')),  # join-kick is okay I guess?
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
            (('choose', 'usna', 'ofina', 'ousna'), ('chosen_chosen', 'usna', 'ofina')),
            (('choose', 'ousna', 'fina', 'usna'), ('chosen_chosen', 'ousna', 'fina')),
            (('choose', 'usna', 'ofina', 'ousna'), ('chosen_chosen', 'usna', 'ofina')),
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
            (('leave', '', 'fina2', 'usna2'), ('leave', 'fina2')),  # ← 'chosen' leaves!
            (('choose', 'usna3', 'fina1', 'usna1'), ('chosen_chosen', 'usna3', 'fina1')),  # chooser tries again
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina2', 'usna2'), ('leave', 'fina2')),  # ← 'chosen' leaves!
            (('choose', 'usna1', 'fina3', 'usna3'), ('chosen_chosen', 'usna1', 'fina3')),  # someone else tries again
        ])

    def test_choose_chooser_left(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina1', 'usna1'), ('leave', 'fina1')),  # ← 'chooser' leaves!
            (('choose', 'usna3', 'fina2', 'usna2'), ('chosen_chosen', 'usna3', 'fina2')),  # chosen continues game
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('leave', '', 'fina1', 'usna1'), ('leave', 'fina1')),  # ← 'chooser' leaves!
            (('choose', 'usna2', 'fina3', 'usna3'), ('chosen_chosen', 'usna2', 'fina3')),  # someone else tries again
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
            (('choose', 'usna3', 'fina1', 'usna1'), ('chosen_chosen', 'usna3', 'fina1')),  # Relies on seeded RNG
            (('choose', 'usna2', 'fina3', 'usna3'), ('chosen_chosen', 'usna2', 'fina3')),  # Relies on seeded RNG
        ])

    def test_dox_nonplayer(self):
        self.check_sequence([
            (('do_w', '', 'fina', 'usna'), ('nonplayer', 'fina')),
            (('do_p', '', 'fina', 'usna'), ('nonplayer', 'fina')),
        ])

    def test_dox_nonplayer_nonempty(self):
        self.check_sequence([
            (('join', '', 'a', 'a'), ('welcome', 'a')),
            (('join', '', 'b', 'b'), ('welcome', 'b')),
            (('do_w', '', 'fina', 'usna'), ('nonplayer', 'fina')),
            (('do_p', '', 'fina', 'usna'), ('nonplayer', 'fina')),
        ])

    def test_dox_nobody(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('do_w', '', 'fina', 'usna'), ('dox_choose_first', 'fina')),
            (('do_p', '', 'fina', 'usna'), ('dox_choose_first', 'fina')),
        ])

    def test_dox_nochosen(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('leave', '', 'fina2', 'usna2'), ('leave', 'fina2')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_choose_first', 'fina1')),
            (('do_p', '', 'fina1', 'usna1'), ('dox_choose_first', 'fina1')),
        ])

    def test_dox_nochooser(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('random', '', 'fina1', 'usna1'), ('random_chosen', 'usna2')),
            (('leave', '', 'fina1', 'usna1'), ('leave', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_choose_first', 'fina2')),
            (('do_p', '', 'fina2', 'usna2'), ('dox_choose_first', 'fina2')),
        ])

    def test_dox_twoplayer(self):
        self.check_sequence([
            (('join', '', 'fina', 'usna'), ('welcome', 'fina')),
            (('join', '', 'ofina', 'ousna'), ('welcome', 'ofina')),
            (('choose', 'ousna', 'fina', 'usna'), ('chosen_chosen', 'ousna', 'fina')),
            (('do_w', '', 'ofina', 'ousna'), ('dox_w', 'ofina', 'usna')),
            (('choose', 'usna', 'ofina', 'ousna'), ('chosen_chosen', 'usna', 'ofina')),
            (('do_p', '', 'fina', 'usna'), ('dox_p', 'fina', 'ousna')),
        ])

    def test_dox_not_involved(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('join', '', 'fina3', 'usna3'), ('welcome', 'fina3')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina3', 'usna3'), ('dox_not_involved', 'fina3', 'usna2', 'fina1')),
            (('do_p', '', 'fina3', 'usna3'), ('dox_not_involved', 'fina3', 'usna2', 'fina1')),
        ])

    def test_dox_wrong_side(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina1', 'usna1'), ('dox_wrong_side', 'fina1', 'usna2')),
            (('do_p', '', 'fina1', 'usna1'), ('dox_wrong_side', 'fina1', 'usna2')),
        ])

    def test_dox_again(self):
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_w', 'fina2', 'usna1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_already_w', 'fina2', 'usna1')),
            (('do_p', '', 'fina2', 'usna2'), ('dox_already_w', 'fina2', 'usna1')),
            (('wop', '', 'fina2', 'usna2'), ('wop_again', 'fina2', 'Wahrheit', 'usna1')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('do_p', '', 'fina2', 'usna2'), ('dox_p', 'fina2', 'usna1')),
            (('do_p', '', 'fina2', 'usna2'), ('dox_already_p', 'fina2', 'usna1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_already_p', 'fina2', 'usna1')),
            (('wop', '', 'fina2', 'usna2'), ('wop_again', 'fina2', 'Pflicht', 'usna1')),
        ])
        self.check_sequence([
            (('join', '', 'fina1', 'usna1'), ('welcome', 'fina1')),
            (('join', '', 'fina2', 'usna2'), ('welcome', 'fina2')),
            (('choose', 'usna2', 'fina1', 'usna1'), ('chosen_chosen', 'usna2', 'fina1')),
            (('wop', '', 'fina2', 'usna2'), ('wop_result_p', 'fina2', 'usna1')),  # Relies on seeded RNG
            (('do_p', '', 'fina2', 'usna2'), ('dox_already_p', 'fina2', 'usna1')),
            (('do_w', '', 'fina2', 'usna2'), ('dox_already_p', 'fina2', 'usna1')),
        ])


if __name__ == '__main__':
    unittest.main()
