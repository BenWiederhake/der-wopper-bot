#!/usr/bin/env python3
# Heavily inspired by chatmemberbot.py in the examples folder.

from atomicwrites import atomic_write
import json
import logging
import os
import secret  # See secret_template.py
import secrets
import sys
from telegram import Chat, ChatMember, ChatMemberUpdated, ParseMode, Update
from telegram.ext import CallbackContext, ChatMemberHandler, CommandHandler, Updater

import logic
import msg


logger = logging.getLogger(__name__)

PERMANENCE_FILENAME = 'wopper_data.json'

ONGOING_GAMES = dict()


def load_ongoing_games():
    global ONGOING_GAMES
    if os.path.exists(PERMANENCE_FILENAME):
        with open(PERMANENCE_FILENAME, 'r') as fp:
            ongoing_games = json.load(fp)
        for chat_id, game_dict in ongoing_games.items():
            ONGOING_GAMES[int(chat_id)] = logic.OngoingGame.from_dict(game_dict)
        logger.info(f'Loaded {len(ONGOING_GAMES)} games.')
    else:
        logger.info(f'Permanence file {PERMANENCE_FILENAME} does not exist; starting with all games denied.')


def save_ongoing_games():
    ongoing_games = {k: v.to_dict() for k, v in ONGOING_GAMES.items()}
    with atomic_write(PERMANENCE_FILENAME, overwrite=True) as fp:
        json.dump(ongoing_games, fp, indent=1)
    logger.info(f'Wrote {len(ONGOING_GAMES)} to {PERMANENCE_FILENAME}.')


def message(msg_id):
    return secrets.choice(msg.MESSAGES[msg_id])


def cmd_admin(update: Update, _context: CallbackContext) -> None:
    if update.effective_user.username != secret.OWNER:
        return

    update.effective_message.reply_text(
        'The admin can do:'
        '\n/admin → show admin commands'
        '\n/show_state → show *all* internal state'
        '\n/resetall → reset all games'
        '\n/resethere → reset game in the current room'
        '\n/permit → permit games in the current room, if not already'
        '\n/deny → stop and deny games in the current room'
        '\n/denyall → stop and deny all games in all rooms'
    )


def cmd_show_state(update: Update, _context: CallbackContext) -> None:
    if update.effective_user.username != secret.OWNER:
        return

    update.effective_message.reply_text(str(ONGOING_GAMES))


def cmd_resetall(update: Update, _context: CallbackContext) -> None:
    global ONGOING_GAMES

    if update.effective_user.username != secret.OWNER:
        return

    for key in ONGOING_GAMES.keys():
        ONGOING_GAMES[key] = logic.OngoingGame()
    save_ongoing_games()
    update.effective_message.reply_text(f'Alle Spiele zurückgesetzt. ({len(ONGOING_GAMES.keys())} erlaubte Räume blieben erhalten.)')


def cmd_resethere(update: Update, _context: CallbackContext) -> None:
    global ONGOING_GAMES

    if update.effective_user.username != secret.OWNER:
        return

    if update.effective_chat.id in ONGOING_GAMES.keys():
        ONGOING_GAMES[update.effective_chat.id] = logic.OngoingGame()
        save_ongoing_games()
        update.effective_message.reply_text('Spiel in diesem Raum zurückgesetzt. Spieler müssen erneut /join-en.')
    else:
        update.effective_message.reply_text('In diesem Raum sind noch keine Spiele erlaubt. Meintest du /permit?')


def cmd_permit(update: Update, _context: CallbackContext) -> None:
    global ONGOING_GAMES

    if update.effective_user.username != secret.OWNER:
        return

    if update.effective_chat.id in ONGOING_GAMES.keys():
        update.effective_message.reply_text('In diesem Raum kann man mit mir bereits Spiele spielen. Vielleicht meintest du /reset, /start, oder /join?')
    else:
        ONGOING_GAMES[update.effective_chat.id] = logic.OngoingGame()
        save_ongoing_games()
        update.effective_message.reply_text('In diesem Raum kann man nun Wahrheit oder Pflicht mit meiner Hilfe spielen. Probier doch mal /start oder /join! :)')


def cmd_deny(update: Update, _context: CallbackContext) -> None:
    global ONGOING_GAMES

    if update.effective_user.username != secret.OWNER:
        return

    if update.effective_chat.id in ONGOING_GAMES.keys():
        del ONGOING_GAMES[update.effective_chat.id]
        save_ongoing_games()
        update.effective_message.reply_text('Spiel gelöscht.')
    else:
        update.effective_message.reply_text('Spiel ist bereits gelöscht(?)')


def cmd_denyall(update: Update, _context: CallbackContext) -> None:
    global ONGOING_GAMES

    if update.effective_user.username != secret.OWNER:
        return

    count = len(ONGOING_GAMES)
    ONGOING_GAMES = dict()
    save_ongoing_games()
    update.effective_message.reply_text(f'Alle {count} Spiele gelöscht.')


def cmd_start(update: Update, _context: CallbackContext) -> None:
    update.effective_message.reply_text(
        f'Hi {update.effective_user.first_name}!'
        f'\n/join → an der Runde teilnehmen'
        f'\n/leave → Runde verlassen (keine Angst, du bleibst im Chat)'
        f'\n/random → nächste Person "zufällig" aus der Runde wählen'
        f'\n/true_random → nächste Person gleichverteilt zufällig aus der Runde wählen, ohne auf faire Verteilung zu achten'
        f'\n/choose @username → nächste Person wählen'
        f'\n/wop → zufällig Wahrheit oder Pflicht wählen'
        f'\n/do_w → Wahrheit wählen'
        f'\n/do_p → Pflicht wählen'
        f'\n/who → wiederholt, wer zur Zeit dran ist'
        f'\n/kick → die zuletzt gewählte Person aus dem Spiel werfen (bleibt aber im Chat)'
        f'\n/players → schreibt in den Chat wer alles an der Runde teilnimmt'
        f'\nMehr macht der Bot nicht. Man muss selber Fragen stellen, Fragen beantworten, oder kapieren wann man dran ist :P'
        f'\nhttps://github.com/BenWiederhake/der-wopper-bot'
        f'\nTexte ändern: {secret.MESSAGES_SHEET}'
        # For BotFather:
        # join - an der Runde teilnehmen
        # leave - Runde verlassen (keine Angst, du bleibst im Chat)
        # random - nächste Person zufällig aus der Runde wählen
        # choose - nächste Person wählen (braucht @username dahinter)
        # wop - zufällig Wahrheit oder Pflicht wählen
        # do_w - Wahrheit wählen
        # do_p - Pflicht wählen
        # who - wiederholt, wer zur Zeit dran ist
        # kick - die zuletzt gewählte Person aus dem Spiel werfen (bleibt aber im Chat)
        # players - schreibt in den Chat wer alles an der Runde teilnimmt
    )


def cmd_random_reply(command):
    def cmd_handler(update: Update, _context: CallbackContext):
        ongoing_game = ONGOING_GAMES.get(update.effective_chat.id)
        if ongoing_game is None:
            return  # No interactions permitted
        update.effective_message.reply_text(
            message(command).format(update.effective_user.first_name, update.effective_user.username, secret.MESSAGES_SHEET)
        )
    return cmd_handler


def cmd_for(command):
    def cmd_handler(update: Update, _context: CallbackContext):
        if update.message is None or update.message.text is None:
            return  # Don't consider Updates that don't stem from a text message.
        text = update.message.text.split(' ', 1)
        argument = text[1] if len(text) == 2 else ''

        ongoing_game = ONGOING_GAMES.get(update.effective_chat.id)
        if ongoing_game is None:
            return  # No interactions permitted
        maybe_response = logic.handle(ongoing_game, command, argument, update.effective_user.first_name, update.effective_user.username)
        save_ongoing_games()
        if maybe_response is None:
            return  # Don't respond at all
        update.effective_message.reply_text(
            message(maybe_response[0]).format(*maybe_response[1:])
        )
    return cmd_handler


def run():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Alive")

    load_ongoing_games()

    # Create the Updater and pass it your bot's token.
    updater = Updater(secret.TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("admin", cmd_admin))
    dispatcher.add_handler(CommandHandler("show_state", cmd_show_state))
    dispatcher.add_handler(CommandHandler("resetall", cmd_resetall))
    dispatcher.add_handler(CommandHandler("resethere", cmd_resethere))
    dispatcher.add_handler(CommandHandler("permit", cmd_permit))
    dispatcher.add_handler(CommandHandler("deny", cmd_deny))
    dispatcher.add_handler(CommandHandler("denyall", cmd_denyall))

    dispatcher.add_handler(CommandHandler("start", cmd_start))
    dispatcher.add_handler(CommandHandler("join", cmd_for('join')))
    dispatcher.add_handler(CommandHandler("leave", cmd_for('leave')))
    dispatcher.add_handler(CommandHandler("show_random", cmd_for('show_random')))
    dispatcher.add_handler(CommandHandler("random", cmd_for('random')))
    dispatcher.add_handler(CommandHandler("true_random", cmd_for('true_random')))
    dispatcher.add_handler(CommandHandler("wop", cmd_for('wop')))
    dispatcher.add_handler(CommandHandler("who", cmd_for('who')))
    dispatcher.add_handler(CommandHandler("kick", cmd_for('kick')))
    dispatcher.add_handler(CommandHandler("do_w", cmd_for('do_w')))
    dispatcher.add_handler(CommandHandler("do_p", cmd_for('do_p')))
    dispatcher.add_handler(CommandHandler("chicken", cmd_for('chicken')))
    dispatcher.add_handler(CommandHandler("choose", cmd_for('choose')))
    dispatcher.add_handler(CommandHandler("whytho", cmd_for('whytho')))
    dispatcher.add_handler(CommandHandler("uptime", cmd_for('uptime')))
    dispatcher.add_handler(CommandHandler("players", cmd_for('players')))

    for cmd_name in msg.RANDOM_REPLY:
        dispatcher.add_handler(CommandHandler(cmd_name, cmd_random_reply(cmd_name)))

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
    if len(sys.argv) == 1:
        run()
    elif len(sys.argv) == 2 and sys.argv[1] == '--dry-run':
        print(f'Dry-running from file {PERMANENCE_FILENAME}')
        load_ongoing_games()
        print(f'Loaded: {ONGOING_GAMES}')
    else:
        print(f'USAGE: {sys.argv[0]} [--dry-run]')
        exit(1)
