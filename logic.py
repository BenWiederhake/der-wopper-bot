#!/bin/false
# Not for execution

import datetime
from generation import GenerationTracker
import random
import secret  # For MESSAGES_SHEET
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
        self.last_reason = 'dunno' # text that can be queried with /whytho
        self.init_datetime = datetime.datetime.now()
        self.track_overall = GenerationTracker() # Overall; ensuring that noone has to wait too long
        self.track_individual = dict() # username to GenerationTracker; ensuring that no pair happens too often / too seldomly
        if seed is not None:
            self.rng = random.Random(seed)  # Necessary for testing
        else:
            self.rng = secrets.SystemRandom()

    def notify_join(self, username, firstname):
        new_tracker = GenerationTracker()
        for other_username, other_tracker in self.track_individual.items():
            new_tracker.notify_join(other_username)
            other_tracker.notify_join(username)
        self.track_individual[username] = new_tracker
        self.track_overall.notify_join(username)

        self.joined_users[username] = firstname

    def notify_leave(self, username):
        del self.track_individual[username]
        for other_tracker in self.track_individual.values():
            other_tracker.notify_leave(username)
        self.track_overall.notify_leave(username)

        del self.joined_users[username]
        if self.last_chooser is not None and self.last_chooser[0] == username:
            self.last_chooser = None
            # self.last_wop = None  # Debatable, but let's try to keep it.
        if self.last_chosen is not None and self.last_chosen[0] == username:
            self.last_chosen = None
            self.last_wop = None

    def notify_chosen(self, chooser_username, chooser_firstname, chosen_username, chosen_firstname, reason):
        self.track_overall.notify_chosen(chosen_username)
        self.track_individual[chooser_username].notify_chosen(chosen_username)

        self.last_chooser = (chooser_username, chooser_firstname)
        self.last_chosen = (chosen_username, chosen_firstname)
        self.last_wop = None
        self.last_reason = reason

    def compute_weigths_for(self, sender_username):
        # All numbers are configurable. In particular the coefficient for w_individual could be 2, to prioritize that.
        w_overall = self.track_overall.get_weights(0)
        w_individual = self.track_individual[sender_username].get_weights(0)
        return GenerationTracker.combine_weights(1, w_overall, 1, w_individual)

    def to_dict(self):
        return dict(
            joined_users=self.joined_users,
            last_chooser=self.last_chooser,
            last_chosen=self.last_chosen,
            last_wop=self.last_wop,
            init_datetime=self.init_datetime.timestamp(),
            track_overall=self.track_overall.to_dict(),
            track_individual={u: t.to_dict() for u, t in self.track_individual.items()},
        )

    def from_dict(d):
        g = OngoingGame()
        assert ('track_overall' in d) == ('track_individual' in d)
        if 'track_overall' in d:
            g.track_overall = GenerationTracker.from_dict(d['track_overall'])
            g.track_individual = {u: GenerationTracker.from_dict(sub_dict) for u, sub_dict in d['track_individual'].items()}
            g.joined_users = d['joined_users']
        else:
            print(f'WARNING: Migrating users to generational RNG! Affected users: {list(d["joined_users"].keys())}\nRNG experience may feel discontinuous.')
            for username, firstname in d['joined_users'].items():
                g.notify_join(username, firstname)
            # No need to set g.joined_users

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
            if self.last_wop is None:
                return ('random_nowop', sender_username, self.last_chooser[1])

        return None


def compute_join(game, argument, sender_firstname, sender_username):
    if not sender_username:
        return ('welcome_no_username', sender_firstname)

    if sender_username in game.joined_users.keys():
        return ('already_in', sender_firstname)
    else:
        game.notify_join(sender_username, sender_firstname)
        return ('welcome', sender_firstname)


def compute_leave(game, argument, sender_firstname, sender_username):
    if sender_username not in game.joined_users.keys():
        return ('already_left', sender_firstname)

    response = ('leave', sender_firstname)

    if game.last_chooser is not None and game.last_chooser[0] == sender_username:
        if game.last_chosen is None:
            response = ('leave_chooser_dunno', sender_firstname)
        else:
            response = ('leave_chooser_handover', sender_firstname, game.last_chosen[0])
    if game.last_chosen is not None and game.last_chosen[0] == sender_username:
        if game.last_chooser is None:
            response = ('leave_chosen_dunno', sender_firstname)
        else:
            response = ('leave_chosen_flee', sender_firstname, game.last_chooser[0])

    game.notify_leave(sender_username)
    return response


def compute_show_random(game, argument, sender_firstname, sender_username):
    if argument:
        argument = argument.strip('@')
        if argument not in game.joined_users:
            return ('unknown_user', sender_firstname, sender_username)
        sender_username, sender_firstname = argument, game.joined_users[argument]

    if sender_username not in game.joined_users.keys():
        return ('nonplayer', sender_firstname)

    if len(game.joined_users) <= 1:
        return ('random_singleplayer', sender_firstname)

    weights = game.compute_weigths_for(sender_username)
    weight_tuples = list(weights.items())
    return ('debug1', str(weight_tuples))


def compute_whytho(game, argument, sender_firstname, sender_username):
    return ('debug1', game.last_reason)


def compute_random(game, argument, sender_firstname, sender_username):
    why_not = game.check_can_choose_player(sender_firstname, sender_username)
    if why_not:
        return why_not

    if len(game.joined_users) <= 1:
        return ('random_singleplayer', sender_firstname)

    weights = game.compute_weigths_for(sender_username)
    weight_tuples = list(weights.items())
    game.rng.shuffle(weight_tuples)  # Wtf? This shouldn't be necessary!
    chosen_username = game.rng.choices(*zip(*weight_tuples))[0]
    chosen_firstname = game.joined_users[chosen_username]  # This is unfortunate

    game.notify_chosen(sender_username, sender_firstname, chosen_username, chosen_firstname, f'random{weight_tuples}')
    return ('random_chosen', chosen_username)


def compute_true_random(game, argument, sender_firstname, sender_username):
    why_not = game.check_can_choose_player(sender_firstname, sender_username)
    if why_not:
        return why_not

    available_players = game.joined_users.copy()
    del available_players[sender_username]

    if len(available_players) == 0:
        return ('random_singleplayer', sender_firstname)

    # Purely uniform distribution, except only the player sending the request.
    chosen_username, chosen_firstname = game.rng.choice(list(available_players.items()))

    game.notify_chosen(sender_username, sender_firstname, chosen_username, chosen_firstname, f'true_random{list(available_players.values())}')
    return ('random_chosen', chosen_username)


def compute_who(game, argument, sender_firstname, sender_username) -> None:
    if game.last_chooser is None and game.last_chosen is None:
        return ('who_nobody', sender_firstname)

    if game.last_chooser is None:
        return ('who_no_chooser', sender_firstname, game.last_chosen[0])

    if game.last_chosen is None:
        return ('who_no_chosen', game.last_chooser[0])

    if game.last_wop is None:
        return ('who_no_wop', game.last_chosen[0], game.last_chooser[1])
    else:
        return ('who_wop_' + game.last_wop, game.last_chooser[1], game.last_chosen[0])


def compute_kick(game, argument, sender_firstname, sender_username) -> None:
    if sender_username not in game.joined_users:
        return ('kick_nonplayer', sender_firstname)

    if game.last_chosen is None:
        return ('kick_no_chosen', sender_firstname)

    old_last_chosen = game.last_chosen
    game.notify_leave(old_last_chosen[0])
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

    game.notify_chosen(sender_username, sender_firstname, chosen_username, chosen_firstname, f'choose')
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


def compute_chicken(game, argument, sender_firstname, sender_username):
    # Very similar to check_can_do_x and compute_wop
    if sender_username not in game.joined_users.keys():
        return ('nonplayer', sender_firstname)

    if game.last_chooser is not None and game.last_chooser[0] == sender_username:
        last_chosen_username = game.last_chosen[0] if game.last_chosen is not None else '???'
        return ('chicken_wrong_side', sender_firstname, last_chosen_username)

    if game.last_chosen is None or game.last_chosen[0] != sender_username:
        return ('chicken_not_involved', sender_firstname)

    if game.last_wop is None:
        return ('chicken_too_early', sender_firstname)

    return ('chicken_' + game.last_wop, secret.MESSAGES_SHEET, secret.OWNER)


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
    elif command == 'show_random':
        return compute_show_random(game, argument, sender_firstname, sender_username)
    elif command == 'whytho':
        return compute_whytho(game, argument, sender_firstname, sender_username)
    elif command == 'chicken':
        return compute_chicken(game, argument, sender_firstname, sender_username)
    else:
        return ('unknown_command', sender_firstname)
