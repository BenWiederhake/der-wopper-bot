#!/usr/bin/env python3
# Heavily inspired by chatmemberbot.py in the examples folder.

import logging
import secret  # See secret_template.py
import secrets
from telegram import Chat, ChatMember, ChatMemberUpdated, ParseMode, Update
from telegram.ext import CallbackContext, ChatMemberHandler, CommandHandler, Updater

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
}


def message(msg_id):
    return secrets.choice(MESSAGES[msg_id])


# bot_data is a dict of:
# * 'chat_rounds', which is a dict of:
#   * keys: chat ID
#   * values: dict of:
#     * 'joined_users', value is a set of @username's (yes, can be changed, therefore it's insecure, meh)
#     * 'last_chooser', value is either None or the telegram.User of the last choosing person
#     * 'last_chosen', value is either None or the telegram.User of the last chosen person

def get_chat_round(bot_data, chatID):
    chats = bot_data.setdefault('chat_rounds', dict())
    return chats.setdefault(chatID, {'joined_users': set(), 'last_chosen': None, 'last_chooser': None})


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
    text = (
        f"Im Moment sind die Spieler {['@' + u for u in chat_round['joined_users']]} in der Runde."
        f"\nZuletzt hat {'@' + last_chooser.username if last_chooser else 'keiner'} gewählt."
        f"\nZuletzt wurde {'@' + last_chosen.username if last_chosen else 'keiner'} gewählt."
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
    if update.effective_user.username in joined_users:
        update.effective_message.reply_text(
            message('already_in').format(update.effective_user.first_name)
        )
    else:
        joined_users.add(update.effective_user.username)
        update.effective_message.reply_text(
            # TODO: More creative responses
            message('welcome').format(update.effective_user.first_name)
        )


def cmd_leave(update: Update, context: CallbackContext) -> None:
    chat_round = get_chat_round(context.bot_data, update.effective_chat.id)
    joined_users = chat_round['joined_users']
    if update.effective_user.username in joined_users:
        update.effective_message.reply_text(
            f'Och, schade. Na bis dann, {update.effective_user.first_name}!'
        )
        joined_users.remove(update.effective_user.username)
    else:
        update.effective_message.reply_text(
            f'Pöh! Du warst sowieso nicht in der Runde, {update.effective_user.first_name}!'
        )


def cmd_missing(update: Update, context: CallbackContext) -> None:
    update.effective_message.reply_text(
        f'Häh? Kann mal jemand {update.effective_user.first_name} dessen Pillen bringen, danke.'
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
    dispatcher.add_handler(CommandHandler("random", cmd_missing))
    dispatcher.add_handler(CommandHandler("wop", cmd_missing))
    dispatcher.add_handler(CommandHandler("who", cmd_missing))
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
