#!/usr/bin/env python3
# Heavily inspired by chatmemberbot.py in the examples folder.

import logging
import secret  # See secret_template.py
import secrets
from telegram import Chat, ChatMember, ChatMemberUpdated, ParseMode, Update
from telegram.ext import CallbackContext, ChatMemberHandler, CommandHandler, Updater
import logic

logger = logging.getLogger(__name__)

MESSAGES = {
    'welcome': [
        'Alles klar, {}!',
        'Na dann viel Spaß, {}!',
    ],
    'already_in': [
        'Du bist doch schon drin, {}! :D',
        'Geht nicht, du bist schon drin, {}.',
        'Alzheimer, {}? Du bist schon drin ;)',
    ],
    'leave': [
        'Och, schade. Na bis dann, {}!',
    ],
    'already_left': [
        'Pöh! Du warst sowieso nicht in der Runde, {}!',
    ],
    'nonplayer': [
        'Du bist der Runde noch nicht beigetreten, {}. Probier doch mal /join!',
    ],
    'random_singleplayer': [
        'Du spielst gerade alleine, {0}. Hmm, wen wähle ich da bloß? Oh, ich hab\'s! Ich wähle *dich*, {0}!',
    ],
    'random_chosen': [
        'I choose you, @{}!',
    ],
    'random_already_chosen': [
        'Du hast doch schon jemanden gewählt, {0}? Und zwar @{1}!',
    ],
    'wop_nobodychosen': [
        'Ich bin verwirrt {0}, aber eigentlich ist zur Zeit niemand dran. Ich sag jetzt mal {1}, hilft das?'
    ],
    'wop_nonchosen': [
        'Sorry {0}, aber gerade ist @{1} dran.'
    ],
    'wop_again': [
        'Du hast doch schon gefragt, {0}? Ich bleibe bei {1}.',
    ],
    'wop_result_w': [
        'WAHRHEIT! @{1} darf eine Frage stellen, und du musst die Wahrheit sagen, {0}.'
    ],
    'wop_result_p': [
        'PLICHT! @{1} darf dir eine Aufgabe stellen, und du musst sie ausführen, {0}.'
    ],
    'who_nobody': [
        'Sorry {0}, ich bin verwirrt. Im Moment ist niemand dran. Probiere doch mal /join und /random.'
    ],
    'who_kicked_or_removed': [
        'Im Moment ist @{0} dran, einen neuen Spieler zu wählen.'
    ],
    'who_no_wop': [
        'Im Moment ist entweder @{1} dran, Wahrheit oder Pflicht zu wählen; oder @{0} muss sich eine Frage/Aufgabe ausdenken; oder @{1} muss darauf reagieren.'
    ],
    'who_wop_w': [
        'Im Moment ist @{1} dran, denn {0} hat Wahrheit gewählt. Wenn du fertig bist, wähle mit /random den nächsten Spieler!'
    ],
    'who_wop_p': [
        'Im Moment ist @{1} dran, denn {0} hat Pflicht gewählt. Wenn du fertig bist, wähle mit /random den nächsten Spieler!'
    ],
    'unknown_command': [
        'Häh? Kann mal jemand {} dessen Pillen bringen, danke.',
    ],
}

WOP_TO_WOP = {
    'w': 'Wahrheit',
    'p': 'Pflicht',
}


def message(msg_id):
    return secrets.choice(MESSAGES[msg_id])


# bot_data is a dict of:
# * 'chat_rounds', which is a dict of:
#   * keys: chat ID
#   * values: dict of:
#     * 'joined_users', value is a dict of:
#       * username to telegram.User's (yes, can be changed, therefore it's insecure, meh)
#     * 'last_chooser', value is either None or the telegram.User of the last choosing person
#     * 'last_chosen', value is either None or the telegram.User of the last chosen person
#     * 'last_wop', value is either None or 'w' or 'p'

def get_chat_round(bot_data, chatID):
    chats = bot_data.setdefault('chat_rounds', dict())
    return chats.setdefault(chatID, {'joined_users': dict(), 'last_chosen': None, 'last_chooser': None, 'last_wop': None})


def cmd_show_chats(update: Update, context: CallbackContext) -> None:
    keys = ', '.join(str(e) for e in context.bot_data.keys())
    chat_ids = ', '.join(str(e) for e in context.bot_data.setdefault('chat_rounds', dict()).keys())
    text = (
        f"@{context.bot.username} ist in den Chats {chat_ids}."
        f"\nWeiterhin kenne ich Kontext zu den keys {keys}."
    )
    update.effective_message.reply_text(text)


def cmd_show_state(update: Update, context: CallbackContext) -> None:
    chat_round = get_chat_round(context.bot_data, update.effective_chat.id)
    last_chooser = chat_round['last_chooser']
    last_chosen = chat_round['last_chosen']
    last_wop = chat_round['last_wop']
    text = (
        f"Im Moment sind die Spieler {['@' + u for u in chat_round['joined_users'].keys()]} in der Runde."
        f"\nZuletzt hat {'@' + last_chooser.username if last_chooser else 'keiner'} gewählt."
        f"\nZuletzt wurde {'@' + last_chosen.username if last_chosen else 'keiner'} gewählt."
        f"\nDie Wahl ist {WOP_TO_WOP[last_wop] if last_wop else 'noch ausstehend'}."
    )
    update.effective_message.reply_text(text)


def cmd_start(update: Update, context: CallbackContext) -> None:
    update.effective_message.reply_text(
        f'Hi {update.effective_user.first_name}!'
        f'\n/join → an der Runde teilnehmen'
        f'\n/leave → Runde verlassen (keine Angst, du bleibst im Chat)'
        f'\n/random → neue (andere) Person aus der Runde wählen'
        f'\n/wop → neue (andere) Person aus der Runde wählen'
        f'\n/who → wiederholt, wer zur Zeit dran ist'
        f'\n/kick → die zuletzt gewählte Person aus dem Spiel werfen (bleibt aber im Chat)'
        f'\n/players → schreibt in den Chat wer alles an der Runde teilnimmt'
        f'\nMehr macht der Bot nicht. Man muss selber Fragen stellen, Fragen beantworten, oder kapieren wann man dran ist :P'
        # For BotFather:
        # join - an der Runde teilnehmen
        # leave - Runde verlassen (keine Angst, du bleibst im Chat)
        # random - neue (andere) Person aus der Runde wählen
        # wop - neue (andere) Person aus der Runde wählen
        # who - wiederholt, wer zur Zeit dran ist
        # kick - die zuletzt gewählte Person aus dem Spiel werfen (bleibt aber im Chat)
        # players - schreibt in den Chat wer Alles an der Runde teilnimmt
    )


def cmd_join(update: Update, context: CallbackContext) -> None:
    chat_round = get_chat_round(context.bot_data, update.effective_chat.id)
    joined_users = chat_round['joined_users']
    if update.effective_user.username in joined_users.keys():
        update.effective_message.reply_text(
            message('already_in').format(update.effective_user.first_name)
        )
    else:
        joined_users[update.effective_user.username] = update.effective_user
        update.effective_message.reply_text(
            # TODO: More creative responses
            message('welcome').format(update.effective_user.first_name)
        )


def cmd_leave(update: Update, context: CallbackContext) -> None:
    chat_round = get_chat_round(context.bot_data, update.effective_chat.id)
    joined_users = chat_round['joined_users']
    last_chooser = chat_round['last_chooser']
    last_chosen = chat_round['last_chosen']

    if update.effective_user.username in joined_users:
        update.effective_message.reply_text(
            message('leave').format(update.effective_user.first_name)
        )
        del joined_users[update.effective_user.username]
        if last_chosen is not None and last_chosen.username == update.effective_user.username:
            last_chosen = None
    else:
        update.effective_message.reply_text(
            message('already_left').format(update.effective_user.first_name)
        )


def cmd_random(update: Update, context: CallbackContext) -> None:
    chat_round = get_chat_round(context.bot_data, update.effective_chat.id)
    last_chooser = chat_round['last_chooser']
    last_chosen = chat_round['last_chosen']

    # FIXME: Complain if not your turn!

    joined_users = chat_round['joined_users']
    if update.effective_user.username not in joined_users:
        update.effective_message.reply_text(
            message('nonplayer').format(update.effective_user.first_name)
        )
        return

    if last_chooser is not None and last_chosen is not None:
        if update.effective_user.username == last_chooser.username and last_chosen.username in joined_users:
            update.effective_message.reply_text(
                message('random_already_chosen').format(update.effective_user.first_name, last_chosen.username)
            )
            return
        if update.effective_user.username != last_chooser.username and update.effective_user.username != last_chosen.username:
            update.effective_message.reply_text(
                message('random_already_chosen').format(update.effective_user.first_name, last_chosen.username)
            )
            return

    available_players = joined_users.copy()
    del available_players[update.effective_user.username]

    if len(available_players) == 0:
        update.effective_message.reply_text(
            message('random_singleplayer').format(update.effective_user.first_name)
        )
        return

    chosen_username = secrets.choice(list(available_players.keys()))
    chosen_player = available_players[chosen_username]
    chat_round['last_chooser'] = update.effective_user
    chat_round['last_chosen'] = chosen_player
    chat_round['last_wop'] = None
    update.effective_message.reply_text(
        message('random_chosen').format(update.effective_user.username)
    )


def cmd_wop(update: Update, context: CallbackContext) -> None:
    chat_round = get_chat_round(context.bot_data, update.effective_chat.id)
    last_chooser = chat_round['last_chooser']
    last_chosen = chat_round['last_chosen']
    last_wop = chat_round['last_wop']

    joined_users = chat_round['joined_users']
    if update.effective_user.username not in joined_users:
        update.effective_message.reply_text(
            message('nonplayer').format(update.effective_user.first_name)
        )
        return

    if last_chosen is None:
        update.effective_message.reply_text(
            message('wop_nobodychosen').format(update.effective_user.first_name, secrets.choice(WOP_TO_WOP.values()))
        )
        return
    if last_chosen.username != update.effective_user.username:
        update.effective_message.reply_text(
            message('wop_nonchosen').format(update.effective_user.first_name, last_chosen.username)
        )
        return

    if last_wop is not None:
        update.effective_message.reply_text(
            message('wop_again').format(update.effective_user.first_name, WOP_TO_WOP[last_wop])
        )
        return

    if last_chooser is None:
        last_chooser_username = '???'
    else:
        last_chooser_username = last_chooser.username

    chat_round['last_wop'] = secrets.choice('wp')
    update.effective_message.reply_text(
        message('wop_result_' + chat_round['last_wop']).format(update.effective_user.first_name, last_chooser_username)
    )


def cmd_who(update: Update, context: CallbackContext) -> None:
    chat_round = get_chat_round(context.bot_data, update.effective_chat.id)
    last_chooser = chat_round['last_chooser']
    last_chosen = chat_round['last_chosen']
    last_wop = chat_round['last_wop']

    if last_chooser is None:
        update.effective_message.reply_text(
            message('who_nobody').format(update.effective_user.first_name)
        )
        return

    if last_chosen is None:
        update.effective_message.reply_text(
            message('who_kicked_or_removed').format(last_chooser.username)
        )
        return

    if last_wop is None:
        update.effective_message.reply_text(
            message('who_no_wop').format(last_chooser.username, last_chosen.username)
        )
    else:
        update.effective_message.reply_text(
            message('who_wop_' + last_wop).format(last_chooser.first_name, last_chosen.username)
        )


def cmd_missing(update: Update, context: CallbackContext) -> None:
    update.effective_message.reply_text(
        message('unknown_command').format(update.effective_user.first_name)
    )


def run():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Alive")

    # Create the Updater and pass it your bot's token.
    updater = Updater(secret.TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # FIXME: In chats schreiben, wenn neu gestartet

    dispatcher.add_handler(CommandHandler("show_chats", cmd_show_chats))
    dispatcher.add_handler(CommandHandler("show_state", cmd_show_state))
    dispatcher.add_handler(CommandHandler("start", cmd_start))
    dispatcher.add_handler(CommandHandler("join", cmd_join))
    dispatcher.add_handler(CommandHandler("leave", cmd_leave))
    dispatcher.add_handler(CommandHandler("random", cmd_random))
    dispatcher.add_handler(CommandHandler("wop", cmd_wop))
    dispatcher.add_handler(CommandHandler("who", cmd_who))
    dispatcher.add_handler(CommandHandler("kick", cmd_missing))
    dispatcher.add_handler(CommandHandler("players", cmd_missing))

    # Start the Bot
    # We pass 'allowed_updates' handle *all* updates including `chat_member` updates
    # To reset this, simply pass `allowed_updates=[]`
    updater.start_polling(allowed_updates=Update.ALL_TYPES)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    logger.info("Begin idle loop")
    updater.idle()


if __name__ == '__main__':
    run()
