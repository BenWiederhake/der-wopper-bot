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
        if seed is None:
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
    if game.last_chooser is not None and game.last_chooser[0] == update.effective_user.username:
        game.last_chooser = None
    if game.last_chosen is not None and game.last_chosen[0] == update.effective_user.username:
        game.last_chosen = None

    return ('leave', sender_firstname)


#def compute_random(update: Update, context: CallbackContext) -> None:
#    chat_round = get_chat_round(context.bot_data, update.effective_chat.id)
#    last_chooser = chat_round['last_chooser']
#    last_chosen = chat_round['last_chosen']
#
#    # FIXME: Complain if not your turn!
#
#    joined_users = chat_round['joined_users']
#    if update.effective_user.username not in joined_users:
#        update.effective_message.reply_text(
#            message('nonplayer').format(update.effective_user.first_name)
#        )
#        return
#
#    if last_chooser is not None and last_chosen is not None:
#        if update.effective_user.username == last_chooser.username and last_chosen.username in joined_users:
#            update.effective_message.reply_text(
#                message('random_already_chosen').format(update.effective_user.first_name, last_chosen.username)
#            )
#            return
#        if update.effective_user.username != last_chooser.username and update.effective_user.username != last_chosen.username:
#            update.effective_message.reply_text(
#                message('random_already_chosen').format(update.effective_user.first_name, last_chosen.username)
#            )
#            return
#
#    available_players = joined_users.copy()
#    del available_players[update.effective_user.username]
#
#    if len(available_players) == 0:
#        update.effective_message.reply_text(
#            message('random_singleplayer').format(update.effective_user.first_name)
#        )
#        return
#
#    chosen_username = secrets.choice(list(available_players.keys()))
#    chosen_player = available_players[chosen_username]
#    chat_round['last_chooser'] = update.effective_user
#    chat_round['last_chosen'] = chosen_player
#    chat_round['last_wop'] = None
#    update.effective_message.reply_text(
#        message('random_chosen').format(update.effective_user.username)
#    )
#
#
#def compute_wop(update: Update, context: CallbackContext) -> None:
#    chat_round = get_chat_round(context.bot_data, update.effective_chat.id)
#    last_chooser = chat_round['last_chooser']
#    last_chosen = chat_round['last_chosen']
#    last_wop = chat_round['last_wop']
#
#    joined_users = chat_round['joined_users']
#    if update.effective_user.username not in joined_users:
#        update.effective_message.reply_text(
#            message('nonplayer').format(update.effective_user.first_name)
#        )
#        return
#
#    if last_chosen is None:
#        update.effective_message.reply_text(
#            message('wop_nobodychosen').format(update.effective_user.first_name, secrets.choice(WOP_TO_WOP.values()))
#        )
#        return
#    if last_chosen.username != update.effective_user.username:
#        update.effective_message.reply_text(
#            message('wop_nonchosen').format(update.effective_user.first_name, last_chosen.username)
#        )
#        return
#
#    if last_wop is not None:
#        update.effective_message.reply_text(
#            message('wop_again').format(update.effective_user.first_name, WOP_TO_WOP[last_wop])
#        )
#        return
#
#    if last_chooser is None:
#        last_chooser_username = '???'
#    else:
#        last_chooser_username = last_chooser.username
#
#    chat_round['last_wop'] = secrets.choice('wp')
#    update.effective_message.reply_text(
#        message('wop_result_' + chat_round['last_wop']).format(update.effective_user.first_name, last_chooser_username)
#    )
#
#
#def compute_who(update: Update, context: CallbackContext) -> None:
#    chat_round = get_chat_round(context.bot_data, update.effective_chat.id)
#    last_chooser = chat_round['last_chooser']
#    last_chosen = chat_round['last_chosen']
#    last_wop = chat_round['last_wop']
#
#    if last_chooser is None:
#        update.effective_message.reply_text(
#            message('who_nobody').format(update.effective_user.first_name)
#        )
#        return
#
#    if last_chosen is None:
#        update.effective_message.reply_text(
#            message('who_kicked_or_removed').format(last_chooser.username)
#        )
#        return
#
#    if last_wop is None:
#        update.effective_message.reply_text(
#            message('who_no_wop').format(last_chooser.username, last_chosen.username)
#        )
#    else:
#        update.effective_message.reply_text(
#            message('who_wop_' + last_wop).format(last_chooser.first_name, last_chosen.username)
#        )


def handle(game, command, argument, sender_firstname, sender_username):
    if command == 'join':
        return compute_join(game, argument, sender_firstname, sender_username)
    elif command == 'leave':
        return compute_leave(game, argument, sender_firstname, sender_username)
    #elif command == 'random':
    #    return compute_random(game, argument, sender_firstname, sender_username)
    #elif command == 'wop':
    #    return compute_wop(game, argument, sender_firstname, sender_username)
    #elif command == 'who':
    #    return compute_who(game, argument, sender_firstname, sender_username)
    else:
        return ('unknown_command', sender_firstname)
