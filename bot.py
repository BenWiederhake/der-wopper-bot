#!/usr/bin/env python3
# Heavily inspired by chatmemberbot.py in the examples folder.

from atomicwrites import atomic_write
from collections import defaultdict
import json
import logging
import os
import secret  # See secret_template.py
import secrets
import sys
from telegram import Update
from telegram.ext import Application, CallbackContext, CommandHandler

import logic
import msg


logger = logging.getLogger(__name__)

PERMANENCE_FILENAME = 'wopper_data.json'

ONGOING_GAMES = dict()

MESSAGE_INDICES = dict()


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


def message(msg_id, chat_id):
    phrasebook = msg.MESSAGES[msg_id]
    if len(phrasebook) == 1:
        index = 0
    else:
        global MESSAGE_INDICES
        cache_key = (msg_id, chat_id)
        old_index = MESSAGE_INDICES.get(cache_key, None)
        if old_index is None:
            old_index = secrets.randbelow(len(phrasebook))
        index = old_index + 1 + (0 == secrets.randbelow(4))
        index %= len(phrasebook)
        MESSAGE_INDICES[cache_key] = index
    return phrasebook[index]


async def cmd_admin(update: Update, _context: CallbackContext) -> None:
    if update.effective_user.username != secret.OWNER:
        return

    await update.effective_message.reply_text(
        'The admin can do:'
        '\n/admin → show admin commands'
        '\n/show_state → show *all* internal state'
        '\n/resetall → reset all games'
        '\n/resethere → reset game in the current room'
        '\n/permit → permit games in the current room, if not already'
        '\n/deny → stop and deny games in the current room'
        '\n/denyall → stop and deny all games in all rooms'
    )


async def cmd_show_state(update: Update, _context: CallbackContext) -> None:
    if update.effective_user.username != secret.OWNER:
        return
    displayable_indices = defaultdict(dict)
    for ((k_str, k_id), v) in MESSAGE_INDICES.items():
        displayable_indices[k_str][k_id] = v
    displayable_games = {k: v.to_dict() for k, v in ONGOING_GAMES.items()}
    state_json_bytes = json.dumps([displayable_indices, displayable_games], separators=",:").encode()
    await update.effective_message.reply_document(
        state_json_bytes,
        filename="state_wopperbot.json",
        caption=f"{len(displayable_games)} games, {len(MESSAGE_INDICES)} counters",
    )


async def cmd_resetall(update: Update, _context: CallbackContext) -> None:
    global ONGOING_GAMES

    if update.effective_user.username != secret.OWNER:
        return

    for key in ONGOING_GAMES.keys():
        ONGOING_GAMES[key] = logic.OngoingGame()
    save_ongoing_games()
    await update.effective_message.reply_text(f'Alle Spiele zurückgesetzt. ({len(ONGOING_GAMES)} erlaubte Räume blieben erhalten.)')


async def cmd_resethere(update: Update, _context: CallbackContext) -> None:
    global ONGOING_GAMES

    if update.effective_user.username != secret.OWNER:
        return

    if update.effective_chat.id in ONGOING_GAMES.keys():
        ONGOING_GAMES[update.effective_chat.id] = logic.OngoingGame()
        save_ongoing_games()
        await update.effective_message.reply_text('Spiel in diesem Raum zurückgesetzt. Spieler müssen erneut /join-en.')
    else:
        await update.effective_message.reply_text('In diesem Raum sind noch keine Spiele erlaubt. Meintest du /permit?')


async def cmd_permit(update: Update, _context: CallbackContext) -> None:
    global ONGOING_GAMES

    if update.effective_user.username != secret.OWNER:
        return

    if update.effective_chat.id in ONGOING_GAMES.keys():
        await update.effective_message.reply_text('In diesem Raum kann man mit mir bereits Spiele spielen. Vielleicht meintest du /reset, /start, oder /join?')
    else:
        ONGOING_GAMES[update.effective_chat.id] = logic.OngoingGame()
        save_ongoing_games()
        await update.effective_message.reply_text('In diesem Raum kann man nun Wahrheit oder Pflicht mit meiner Hilfe spielen. Probier doch mal /start oder /join! :)')


async def cmd_deny(update: Update, _context: CallbackContext) -> None:
    global ONGOING_GAMES

    if update.effective_user.username != secret.OWNER:
        return

    if update.effective_chat.id in ONGOING_GAMES.keys():
        del ONGOING_GAMES[update.effective_chat.id]
        save_ongoing_games()
        await update.effective_message.reply_text('Spiel gelöscht.')
    else:
        await update.effective_message.reply_text('Spiel ist bereits gelöscht(?)')


async def cmd_denyall(update: Update, _context: CallbackContext) -> None:
    global ONGOING_GAMES

    if update.effective_user.username != secret.OWNER:
        return

    count = len(ONGOING_GAMES)
    ONGOING_GAMES = dict()
    save_ongoing_games()
    await update.effective_message.reply_text(f'Alle {count} Spiele gelöscht.')


async def cmd_start(update: Update, _context: CallbackContext) -> None:
    await update.effective_message.reply_text(
        f'Hi {update.effective_user.first_name}!'
        f'\n/join → an der Runde teilnehmen'
        f'\n/leave → Runde verlassen (keine Angst, du bleibst im Chat)'
        f'\n/random → nächste Person "zufällig" aus der Runde wählen'
        f'\n/true_random → nächste Person gleichverteilt zufällig aus der Runde wählen, ohne auf faire Verteilung zu achten'
        f'\n/choose @username → nächste Person wählen'
        f'\n/wop → zufällig Wahrheit oder Pflicht wählen'
        f'\n/do_w → Wahrheit wählen'
        f'\n/do_p → Pflicht wählen'
        f'\n/do_idc → Der Fragesteller darf Wahrheit oder Pflicht wählen'
        f'\n/nope → Sich vor der Aufgabe drücken'
        f'\n/who → wiederholt, wer zur Zeit dran ist'
        f'\n/kick → die zuletzt gewählte Person aus dem Spiel werfen (bleibt aber im Chat)'
        f'\n/players → schreibt in den Chat wer alles an der Runde teilnimmt'
        f'\nMehr macht der Bot nicht. Man muss selber Fragen stellen, Fragen beantworten, oder kapieren wann man dran ist :P'
        f'\nhttps://github.com/BenWiederhake/der-wopper-bot'
        f'\nTexte ändern: {secret.MESSAGES_SHEET}'
        f'\n(Außerdem gibt\'s noch /uptime, /show_random, /whytho, /how, /where, /why.)'
        # For BotFather:
        # join - an der Runde teilnehmen
        # leave - Runde verlassen (keine Angst, du bleibst im Chat)
        # random - nächste Person zufällig aus der Runde wählen
        # start - Hier geht's los! :D
        # choose - nächste Person wählen (braucht @username dahinter)
        # wop - zufällig Wahrheit oder Pflicht wählen
        # do_w - Wahrheit wählen
        # do_p - Pflicht wählen
        # do_idc - Wahrheit/Pflicht beides okay
        # nope - Aufgabe ablehnen, Ersatz bekommen
        # who - wiederholt, wer zur Zeit dran ist
        # kick - Person aus dem Spiel werfen (bleibt aber im Chat)
        # players - schreibt in den Chat wer alles an der Runde teilnimmt
    )


def cmd_random_reply(command):
    async def cmd_handler(update: Update, _context: CallbackContext):
        ongoing_game = ONGOING_GAMES.get(update.effective_chat.id)
        if ongoing_game is None:
            return  # No interactions permitted
        await update.effective_message.reply_text(
            message(command, update.effective_chat.id).format(update.effective_user.first_name, update.effective_user.username, secret.MESSAGES_SHEET)
        )
    return cmd_handler


def cmd_for(command):
    async def cmd_handler(update: Update, _context: CallbackContext):
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
        await update.effective_message.reply_text(
            message(maybe_response[0], update.effective_chat.id).format(*maybe_response[1:])
        )
    return cmd_handler


def run():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # OPTIONAL: set higher logging level for httpx to avoid all GET and POST requests being logged
    # logging.getLogger("httpx").setLevel(logging.WARNING)
    logger.info("Alive")

    load_ongoing_games()

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(secret.TOKEN).build()

    application.add_handler(CommandHandler("admin", cmd_admin))
    application.add_handler(CommandHandler("show_state", cmd_show_state))
    application.add_handler(CommandHandler("resetall", cmd_resetall))
    application.add_handler(CommandHandler("resethere", cmd_resethere))
    application.add_handler(CommandHandler("permit", cmd_permit))
    application.add_handler(CommandHandler("deny", cmd_deny))
    application.add_handler(CommandHandler("denyall", cmd_denyall))

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_start))
    application.add_handler(CommandHandler("join", cmd_for('join')))
    application.add_handler(CommandHandler("leave", cmd_for('leave')))
    application.add_handler(CommandHandler("show_random", cmd_for('show_random')))
    application.add_handler(CommandHandler("random", cmd_for('random')))
    application.add_handler(CommandHandler("true_random", cmd_for('true_random')))
    application.add_handler(CommandHandler("wop", cmd_for('wop')))
    application.add_handler(CommandHandler("who", cmd_for('who')))
    application.add_handler(CommandHandler("kick", cmd_for('kick')))
    application.add_handler(CommandHandler("do_w", cmd_for('do_w')))
    application.add_handler(CommandHandler("do_p", cmd_for('do_p')))
    application.add_handler(CommandHandler("do_idc", cmd_for('do_idc')))
    application.add_handler(CommandHandler("chicken", cmd_for('chicken')))
    application.add_handler(CommandHandler("nope", cmd_for('chicken')))
    application.add_handler(CommandHandler("choose", cmd_for('choose')))
    application.add_handler(CommandHandler("whytho", cmd_for('whytho')))
    application.add_handler(CommandHandler("uptime", cmd_for('uptime')))
    application.add_handler(CommandHandler("players", cmd_for('players')))
    application.add_handler(CommandHandler("unknown_command", cmd_for('unknown_command')))  # By popular opinion

    for cmd_name in msg.RANDOM_REPLY:
        application.add_handler(CommandHandler(cmd_name, cmd_random_reply(cmd_name)))

    # Run the bot until the user presses Ctrl-C
    logger.info("Begin idle loop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


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
