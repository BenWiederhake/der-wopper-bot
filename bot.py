#!/usr/bin/env python3
# Heavily inspired by chatmemberbot.py in the examples folder.

import logging
import secret  # See secret_template.py
import secrets
from telegram import Chat, ChatMember, ChatMemberUpdated, ParseMode, Update
from telegram.ext import CallbackContext, ChatMemberHandler, CommandHandler, Updater
import logic
from logic import WOP_TO_WOP


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
    'random_not_involved': [
        'Warte noch etwas, {0}. Sobald @{2} fertig ist mit der Wahrheit/Pflicht an {1}, darf @{2} weitermachen mit /random. Alternativ, schreibe /kick um @{2} aus der Runde zu schmeißen.',
    ],
    'random_already_chosen': [
        'Du hast doch schon jemanden gewählt, {0}? Und zwar @{1}!',
    ],
    'wop_nobodychosen': [
        'Ich bin verwirrt {0}, aber eigentlich ist zur Zeit niemand dran. Ich sag jetzt mal {1}, hilft das?'
    ],
    'wop_nonchosen': [
        'Sorry {0}, aber gerade ist @{1} dran, Wahrheit oder Pflicht zu wählen.'
    ],
    'wop_again': [
        'Du hast doch schon gefragt, {0}? Ich bleibe bei {1}. Jetzt ist @{2} dran!',
    ],
    'wop_result_w': [
        'WAHRHEIT! @{1} darf eine Frage stellen, und du musst die Wahrheit sagen, {0}.'
    ],
    'wop_result_p': [
        'PLICHT! @{1} darf dir eine Aufgabe stellen, und du musst sie ausführen, {0}.'
    ],
    'who_nobody': [
        'Sorry {0}, ich bin verwirrt. Im Moment ist niemand dran. Probiere doch mal /join und /random.',
    ],
    'who_no_chooser': [
        'Sorry {0}, ich bin verwirrt. Zwar wurde @{1} gewählt, aber die andere Person fehlt. Probiere doch mal /random.',
    ],
    'who_no_chosen': [
        'Im Moment ist @{0} dran, einen neuen Spieler mit /random zu wählen.',
    ],
    'who_no_wop': [
        'Im Moment ist entweder @{1} dran, Wahrheit oder Pflicht zu wählen; oder @{0} muss sich eine Frage/Aufgabe ausdenken; oder @{1} muss darauf reagieren.',
    ],
    'who_wop_w': [
        'Im Moment ist @{1} dran, denn {0} hat Wahrheit gewählt. Wenn du fertig bist, wähle mit /random den nächsten Spieler!',
    ],
    'who_wop_p': [
        'Im Moment ist @{1} dran, denn {0} hat Pflicht gewählt. Wenn du fertig bist, wähle mit /random den nächsten Spieler!',
    ],
    'players_nobody': [
        'Sorry {0}, im Moment spielt keiner. PLICHT: Alle müssen /join schreiben, und irgendjemand schreibt /random! :D',
    ],
    'players_one_self': [
        'Du spielst gerade mit dir selbst, {0}. Mach wenigstens die Kamera an!',
        'Sorry, du bist ganz alleine, {0}. :( Mag jemand mitmachen? Einfach /join schreiben! :D',
    ],
    'players_one_other': [
        'Im Moment spielt {1} mit sich selbst. Komm schon {0}, komm dazu und schreibe /join! :D',
        'Im Moment spielt nur {1}. Mach mit und schreibe /join! :D',
    ],
    'players_few_self': [
        'Die Runde besteht lediglich aus {1}. Überrede doch ein paar Leute dazu, zu joinen, {0}!',
        'Es spielen zur Zeit nur {1}. Mach mit, und /join :D',
    ],
    'players_few_other': [
        'Die Runde besteht lediglich aus {1}. Magst du mitmachen, {0}? /join ;)',
        'Es spielen zur Zeit nur {1}. Mach mit, und /join :D',
    ],
    'players_many_self': [  # {0} ist der Name des Fragenden
        'Die Runde besteht aus {1}.',
    ],
    'players_many_other': [  # {0} ist der Name des Fragenden
        'Die Runde besteht aus {1}.',
    ],
    'kick_nonplayer': [
        'Sorry {0}, aber du spielst nicht mit, also darfst du nicht Andere rauswerfen. Probier doch mal /join.',
    ],
    'kick_no_chosen': [
        'Sorry {0}, aber im Moment ist niemand dran, also kann ich die Person auch nicht kicken. Probier doch mal /random!',
    ],
    'kick': [
        'Tschüss @{1}! {0} hat dich rausgekickt. Du kannst gerne wieder /join-en.',
        'Okaydokey {0}, @{1} ist nicht mehr dabei.',
    ],
    'uptime': [
        'Der Bot war hier das erste mal {0} aktiv. Jetzt ist es {1}.',
    ],
    'unknown_command': [
        'Häh? Kann mal jemand {} dessen Pillen bringen, danke.',
    ],
}


def message(msg_id):
    return secrets.choice(MESSAGES[msg_id])


# bot_data is a dict of:
# * 'ongoing_games', which is a dict of:
#   * keys: chat ID
#   * values: logic.OngoingGame

def get_chat_round(bot_data, chatID):
    chats = bot_data.setdefault('ongoing_games', dict())
    return chats.setdefault(chatID, logic.OngoingGame())


def cmd_show_state(update: Update, context: CallbackContext) -> None:
    update.effective_message.reply_text(str(context.bot_data))


def cmd_start(update: Update, context: CallbackContext) -> None:
    update.effective_message.reply_text(
        f'Hi {update.effective_user.first_name}!'
        f'\n/join → an der Runde teilnehmen'
        f'\n/leave → Runde verlassen (keine Angst, du bleibst im Chat)'
        f'\n/random → neue (andere) Person aus der Runde wählen'
        f'\n/wop → zufällig Wahrheit oder Pflicht wählen'
        f'\n/who → wiederholt, wer zur Zeit dran ist'
        f'\n/kick → die zuletzt gewählte Person aus dem Spiel werfen (bleibt aber im Chat)'
        f'\n/players → schreibt in den Chat wer alles an der Runde teilnimmt'
        f'\nMehr macht der Bot nicht. Man muss selber Fragen stellen, Fragen beantworten, oder kapieren wann man dran ist :P'
        # For BotFather:
        # join - an der Runde teilnehmen
        # leave - Runde verlassen (keine Angst, du bleibst im Chat)
        # random - neue (andere) Person aus der Runde wählen
        # wop - zufällig Wahrheit oder Pflicht wählen
        # who - wiederholt, wer zur Zeit dran ist
        # kick - die zuletzt gewählte Person aus dem Spiel werfen (bleibt aber im Chat)
        # players - schreibt in den Chat wer alles an der Runde teilnimmt
    )


def cmd_reset(update: Update, context: CallbackContext) -> None:
    if update.effective_user.username != secret.OWNER:
        return

    context.bot_data.clear()
    update.effective_message.reply_text('… I have no memory of this place.')


def cmd_for(command):
    def cmd_handler(update: Update, context: CallbackContext):
        ongoing_game = get_chat_round(context.bot_data, update.effective_chat.id)
        maybe_response = logic.handle(ongoing_game, command, '', update.effective_user.first_name, update.effective_user.username)
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

    # Create the Updater and pass it your bot's token.
    updater = Updater(secret.TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # FIXME: In chats schreiben, wenn neu gestartet

    dispatcher.add_handler(CommandHandler("show_state", cmd_show_state))
    dispatcher.add_handler(CommandHandler("reset", cmd_reset))
    dispatcher.add_handler(CommandHandler("start", cmd_start))
    dispatcher.add_handler(CommandHandler("join", cmd_for('join')))
    dispatcher.add_handler(CommandHandler("leave", cmd_for('leave')))
    dispatcher.add_handler(CommandHandler("random", cmd_for('random')))
    dispatcher.add_handler(CommandHandler("wop", cmd_for('wop')))
    dispatcher.add_handler(CommandHandler("who", cmd_for('who')))
    dispatcher.add_handler(CommandHandler("kick", cmd_for('kick')))
    dispatcher.add_handler(CommandHandler("players", cmd_for('players')))

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
