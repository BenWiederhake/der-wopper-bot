#!/bin/false
# Not for execution

import datetime
import random
import secrets

WOP_TO_WOP = {
    'w': 'Wahrheit',
    'p': 'Pflicht',
}

DATETIME_FORMAT = '%Y-%m-%d %T'


class OngoingGame:
    def __init__(self, seed=None):
        self.joined_users = dict() # username to firstname
        self.last_chooser = None # or (username, firstname) tuple
        self.last_chosen = None # or (username, firstname) tuple
        self.last_wop = None # or 'w' or 'p'
        self.init_datetime = datetime.datetime.now()
        if seed is not None:
            self.rng = random.Random(seed)  # Necessary for testing
        else:
            self.rng = secrets.SystemRandom()

    def to_dict(self):
        return dict(
            joined_users=self.joined_users,
            last_chooser=self.last_chooser,
            last_chosen=self.last_chosen,
            last_wop=self.last_wop,
            init_datetime=self.init_datetime.timestamp(),
        )

    def from_dict(d):
        g = OngoingGame()
        g.joined_users = d['joined_users']
        g.last_chooser = d['last_chooser']
        g.last_chosen = d['last_chosen']
        g.last_wop = d['last_wop']
        g.init_datetime = datetime.datetime.fromtimestamp(d['init_datetime'])
        return g

    def __repr__(self):
        return str(self.to_dict())

    def check_can_choose_player(self, sender_firstname, sender_username):
        if sender_username not in self.joined_users.keys():
            return ('nonplayer', sender_firstname)

        # If both last_chooser and last_chosen are None, then we're in the first round, and we want to allow it anyway.

        # If only last_chooser is None, then *probably* last_chosen should be the one doing /random, but we'll allow it anyway.

        # If only last_chosen is None, then *probably* last_chooser should be the one doing /random, but we'll allow it anyway.

        # If both exist, only allow the last_chosen to do /random:
        if self.last_chooser is not None and self.last_chosen is not None:
            # There's a good chance the player just misunderstood.
            if self.last_chooser[0] == sender_username:
                return ('random_already_chosen', sender_firstname, self.last_chosen[0])
            if self.last_chosen[0] != sender_username:
                return ('random_not_involved', sender_firstname, self.last_chooser[1], self.last_chosen[0])

        return None


def compute_join(game, argument, sender_firstname, sender_username):
    if not sender_username:
        return ('welcome_no_username', sender_firstname)

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
    return compute_true_random(game, argument, sender_firstname, sender_username)  # FIXME


def compute_true_random(game, argument, sender_firstname, sender_username):
    why_not = game.check_can_choose_player(sender_firstname, sender_username)
    if why_not:
        return why_not

    available_players = game.joined_users.copy()
    del available_players[sender_username]

    if len(available_players) == 0:
        return ('random_singleplayer', sender_firstname)

    chosen_username, chosen_firstname = game.rng.choice(list(available_players.items()))

    if game.last_chooser is not None and chosen_username == game.last_chooser[0]:
        # So A chose B, and now B is about to choose A. Let's make this a lot less likely by drawing again:
        chosen_username, chosen_firstname = game.rng.choice(list(available_players.items()))
        # Note: It is still possible that we go back to the same person – in fact, this will always happen in a two-player setup.
        # However, in three-player setups we go back 25% of the time, and choose the other person 75% of the time.
        # In four-player setups we go back 11.1% of the time, and in general it's 1/(n-1)² instead of 1/(n-1).

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

    del game.joined_users[game.last_chosen[0]]

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


def compute_uptime(game, argument, sender_firstname, sender_username) -> None:
    return ('uptime', game.init_datetime.strftime(DATETIME_FORMAT), datetime.datetime.now().strftime(DATETIME_FORMAT))


def compute_choose(game, argument, sender_firstname, sender_username) -> None:
    why_not = game.check_can_choose_player(sender_firstname, sender_username)
    if why_not:
        return why_not

    if len(game.joined_users) <= 1:
        return ('random_singleplayer', sender_firstname)

    if not argument:
        return ('chosen_empty', sender_firstname, sender_username)

    if argument.startswith('@'):
        argument = argument[1:]

    if argument in game.joined_users.keys():
        chosen_username, chosen_firstname = argument, game.joined_users[argument]
    else:
        for usna, fina in game.joined_users.items():
            if argument == fina:
                chosen_username, chosen_firstname = usna, fina
                break
        else:
            return ('unknown_user', sender_firstname, sender_username)

    if chosen_username == sender_username:
        return ('chosen_self', sender_firstname)

    game.last_chooser = (sender_username, sender_firstname)
    game.last_chosen = (chosen_username, chosen_firstname)
    game.last_wop = None
    return ('chosen_chosen', chosen_username, sender_firstname)


def check_can_do_x(game, sender_firstname, sender_username):
    if sender_username not in game.joined_users.keys():
        return ('nonplayer', sender_firstname)

    if game.last_chooser is None or game.last_chosen is None:
        return ('dox_choose_first', sender_firstname)

    if game.last_chooser[0] == sender_username:
        return ('dox_wrong_side', sender_firstname, game.last_chosen[0])
    if game.last_chosen[0] != sender_username:
        return ('dox_not_involved', sender_firstname, game.last_chosen[0], game.last_chooser[1])

    if game.last_wop is not None:
        return ('dox_already_' + game.last_wop, sender_firstname, game.last_chooser[0])

    return None


def compute_do_w(game, argument, sender_firstname, sender_username) -> None:
    why_not = check_can_do_x(game, sender_firstname, sender_username)
    if why_not:
        return why_not

    game.last_wop = 'w'
    return ('dox_w', sender_firstname, game.last_chooser[0])


def compute_do_p(game, argument, sender_firstname, sender_username) -> None:
    why_not = check_can_do_x(game, sender_firstname, sender_username)
    if why_not:
        return why_not

    game.last_wop = 'p'
    return ('dox_p', sender_firstname, game.last_chooser[0])


def handle(game, command, argument, sender_firstname, sender_username):
    if command == 'join':
        return compute_join(game, argument, sender_firstname, sender_username)
    elif command == 'leave':
        return compute_leave(game, argument, sender_firstname, sender_username)
    elif command == 'random':
        return compute_random(game, argument, sender_firstname, sender_username)
    elif command == 'true_random':
        return compute_true_random(game, argument, sender_firstname, sender_username)
    elif command == 'wop':
        return compute_wop(game, argument, sender_firstname, sender_username)
    elif command == 'who':
        return compute_who(game, argument, sender_firstname, sender_username)
    elif command == 'kick':
        return compute_kick(game, argument, sender_firstname, sender_username)
    elif command == 'players':
        return compute_players(game, argument, sender_firstname, sender_username)
    elif command == 'uptime':
        return compute_uptime(game, argument, sender_firstname, sender_username)
    elif command == 'do_w':
        return compute_do_w(game, argument, sender_firstname, sender_username)
    elif command == 'do_p':
        return compute_do_p(game, argument, sender_firstname, sender_username)
    elif command == 'choose':
        return compute_choose(game, argument, sender_firstname, sender_username)
    else:
        return ('unknown_command', sender_firstname)
