#!/bin/false
# Not for execution

import random
import secrets

WOP_TO_WOP = {
    'w': 'Wahrheit',
    'p': 'Pflicht',
}


class OngoingGame:
    def __init__(self, seed=None):
        self.joined_users = dict() # username to firstname
        self.last_chooser = None # or (username, firstname) tuple
        self.last_chosen = None # or (username, firstname) tuple
        self.last_wop = None # or 'w' or 'p'
        if seed is not None:
            self.rng = random.Random(seed)  # Necessary for testing
        else:
            self.rng = secrets.SystemRandom()


def compute_join(game, argument, sender_firstname, sender_username):
    if sender_username in game.joined_users.keys():
        return ('already_in', sender_firstname)
    else:
        game.joined_users[sender_username] = sender_firstname
        return ('welcome', sender_firstname)


def compute_leave(game, argument, sender_firstname, sender_username):
    if sender_username not in game.joined_users.keys():
        return ('already_left', sender_firstname)

    del game.joined_users[sender_username]
    if game.last_chooser is not None and game.last_chooser[0] == sender_username:
        game.last_chooser = None
    if game.last_chosen is not None and game.last_chosen[0] == sender_username:
        game.last_chosen = None

    return ('leave', sender_firstname)


def compute_random(game, argument, sender_firstname, sender_username):
    if sender_username not in game.joined_users.keys():
        return ('nonplayer', sender_firstname)

    # If both last_chooser and last_chosen are None, then we're in the first round, and we want to allow it anyway.

    # If only last_chooser is None, then *probably* last_chosen should be the one doing /random, but we'll allow it anyway.

    # If only last_chosen is None, then *probably* last_chooser should be the one doing /random, but we'll allow it anyway.

    # If both exist, only allow the last_chosen to do /random:
    if game.last_chooser is not None and game.last_chosen is not None:
        # There's a good chance the player just misunderstood.
        if game.last_chooser[0] == sender_username:
            return ('random_already_chosen', sender_firstname, game.last_chosen[0])
        if game.last_chosen[0] != sender_username:
            return ('random_not_involved', sender_firstname, game.last_chooser[1], game.last_chosen[0])

    available_players = game.joined_users.copy()
    del available_players[sender_username]

    if len(available_players) == 0:
        return ('random_singleplayer', sender_firstname)

    chosen_username, chosen_firstname = game.rng.choice(list(available_players.items()))
    game.last_chooser = (sender_username, sender_firstname)
    game.last_chosen = (chosen_username, chosen_firstname)
    game.last_wop = None
    return ('random_chosen', chosen_username)


def compute_wop(game, argument, sender_firstname, sender_username):
    if sender_username not in game.joined_users:
        return ('nonplayer', sender_firstname)

    if game.last_chosen is None:
        return ('wop_nobodychosen', sender_firstname, game.rng.choice(list(WOP_TO_WOP.values())))
    if game.last_chosen[0] != sender_username:
        return ('wop_nonchosen', sender_firstname, game.last_chosen[0])

    if game.last_chooser is None:
        last_chooser_username = '???'
    else:
        last_chooser_username = game.last_chooser[0]

    if game.last_wop is not None:
        return ('wop_again', sender_firstname, WOP_TO_WOP[game.last_wop], last_chooser_username)

    game.last_wop = game.rng.choice('wp')
    return ('wop_result_' + game.last_wop, sender_firstname, last_chooser_username)


def compute_who(game, argument, sender_firstname, sender_username) -> None:
    if game.last_chooser is None and game.last_chosen is None:
        return ('who_nobody', sender_firstname)

    if game.last_chooser is None:
        return ('who_no_chooser', sender_firstname, game.last_chosen[0])

    if game.last_chosen is None:
        return ('who_no_chosen', game.last_chooser[0])

    if game.last_wop is None:
        return ('who_no_wop', game.last_chooser[0], game.last_chosen[0])
    else:
        return ('who_wop_' + game.last_wop, game.last_chooser[1], game.last_chosen[0])


def compute_kick(game, argument, sender_firstname, sender_username) -> None:
    if sender_username not in game.joined_users:
        return ('kick_nonplayer', sender_firstname)

    if game.last_chosen is None:
        return ('kick_no_chosen', sender_firstname)

    old_last_chosen = game.last_chosen
    game.last_chosen = None
    game.last_wop = None
    return ('kick', sender_firstname, old_last_chosen[0])


def compute_players(game, argument, sender_firstname, sender_username) -> None:
    num_players = len(game.joined_users)
    if num_players == 0:
        return ('players_nobody', sender_firstname)

    firstnames = list(game.joined_users.values())
    firstnames.sort()
    sender_is_in = sender_username in game.joined_users.keys()
    msg_suffix = '_self' if sender_is_in else '_other'

    if num_players == 1:
        return ('players_one' + msg_suffix, sender_firstname, firstnames[0])

    firstnames_head = ', '.join(firstnames[:-1])
    firstnames_tail = firstnames[-1]
    # Extending the message-interface is too painful, so let's do this instead.
    firstnames_text = f'{firstnames_head} und {firstnames_tail}'

    if num_players < 5:
        return ('players_few' + msg_suffix, sender_firstname, firstnames_text)

    return ('players_many' + msg_suffix, sender_firstname, firstnames_text)


def handle(game, command, argument, sender_firstname, sender_username):
    if command == 'join':
        return compute_join(game, argument, sender_firstname, sender_username)
    elif command == 'leave':
        return compute_leave(game, argument, sender_firstname, sender_username)
    elif command == 'random':
        return compute_random(game, argument, sender_firstname, sender_username)
    elif command == 'wop':
        return compute_wop(game, argument, sender_firstname, sender_username)
    elif command == 'who':
        return compute_who(game, argument, sender_firstname, sender_username)
    elif command == 'kick':
        return compute_kick(game, argument, sender_firstname, sender_username)
    elif command == 'players':
        return compute_players(game, argument, sender_firstname, sender_username)
    else:
        return ('unknown_command', sender_firstname)
