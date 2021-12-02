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
        'Alles klar, {0}!',
        'Na dann viel Spaß, {0}!',
        'Au weia, {0} ist mit von der Partie, das kann ja heiter werden!',
        'Schön, dass du dabei bist, {0}!',
        '{0}! Es ist eine Falle!',
    ],
    'already_in': [
        'Du bist doch schon drin, {0}! :D',
        'Geht nicht, du bist schon drin, {0}.',
        'Alzheimer, {0}? Du bist schon drin ;)',
    ],
    'leave': [
        'Och, schade. Na bis dann, {0}!',
        'Na toll, Ihr habt {0} erfolgreich vergrault!',
        '{0} möchte uns verlassen! Schade, dann bis zum nächsten Mal.',
    ],
    'already_left': [
        'Pöh! Du warst sowieso nicht in der Runde, {0}!',
        'Wenn der Kuchen redet, schweigen die Krümel, {0}!',
        'Mehr als "nicht dabei" geht nicht {0}.',
    ],
    'nonplayer': [
        'Du bist der Runde noch nicht beigetreten, {0}. Probier doch mal /join!',
        'I\'m sorry, {0}, I\'m afraid I can\'t let you do that. Du bist noch nicht der Runde beigetreten. Kleiner Tipp: Benutze /join! ;)',
    ],
    'random_singleplayer': [
        'Du spielst gerade alleine, {0}. Hmm, wen wähle ich da bloß? Oh, ich hab\'s! Ich wähle *dich*, {0}!',
        'Du spielst gerade mit dir selbst, {0}. Ist das jetzt eine win-win Situation?',
        'Alleine spielen ist doof! Frag doch ein paar Leute, ob sie mitmachen wollen. Vielleicht findet sich ja wer :)',
    ],
    'random_chosen': [
        'I choose you, @{0}! Du musst jetzt Wahrheit oder Pflicht wählen: /do_w /do_p Du kannst auch zufällig wählen, mit /wop.',
        '@{0} hat das große Los gezogen und ist dran: Wahrheit oder Pflicht? /do_w /do_p Oder /wop?',
    ],
    'random_not_involved': [
        'Warte noch etwas, {0}. Sobald @{2} fertig ist mit der Wahrheit/Pflicht an {1}, darf @{2} weitermachen mit /choose @username oder /random. Alternativ, schreibe /kick um @{2} aus der Runde zu schmeißen.',
    ],
    'random_already_chosen': [
        'Du hast doch schon jemanden gewählt, {0}? Und zwar @{1}!',
        'Das hättest du dir vorher überlegen müssen {0}. Jetzt ist @{1} schon dran.',
    ],
    'wop_nobodychosen': [ # {1} ist 'Wahrheit' oder 'Pflicht'
        'Ich bin verwirrt {0}, eigentlich ist zur Zeit niemand dran. Ich sag jetzt mal {1}, hilft das?',
        '{0}, du hast das goldene Ahnungslos gezogen. Magst du vielleicht {1} machen?',
    ],
    'wop_nonchosen': [
        'Sorry {0}, aber gerade ist @{1} dran, Wahrheit oder Pflicht zu wählen.',
    ],
    'wop_again': [
        'Das steht doch schon fest, {0}? Es bleibt bei {1}. Jetzt entscheidet @{2}!',
    ],
    'wop_result_w': [
        'WAHRHEIT! @{1} darf eine Frage stellen, und du musst die Wahrheit sagen, {0}.',
    ],
    'wop_result_p': [
        'PLICHT! @{1} darf dir eine Aufgabe stellen, und du musst sie ausführen, {0}.',
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
        'Im Moment ist @{1} dran, denn es hat Wahrheit gewählt, und muss jetzt {0} eine Frage beantworten. Wenn ihr fertig seid, darf @{1} mit /random den nächsten Spieler wählen. :)',
    ],
    'who_wop_p': [
        'Im Moment ist @{1} dran, denn es hat Pflicht gewählt, und muss jetzt eine Aufgabe für {0} erledigen. Wenn ihr fertig seid, darf @{1} mit /random den nächsten Spieler wählen. :)',
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
        'Der Bot war hier das erste Mal {0} aktiv. Jetzt ist es {1}.',
    ],
    'chosen_empty': [
        'Und wen, {0}? Der /choose-Befehl braucht ein Argument, z.B. @{1}.',
    ],
    'chosen_self': [
        'Tut mir Leid, aber du kannst dich nicht selbst wählen, {0}. Probier doch mal /random.'
    ],
    'chosen_chosen': [
        '@{0}! {1} hat dich gewählt. Wahrheit oder Pflicht? /do_w /do_p Oder doch lieber zufällig? /wop',
    ],
    'unknown_user': [
        'Hmm, das verstehe ich leider nicht, {0}. Probier\'s doch mal mit dem @username, also zum Beispiel @{1}.',
    ],
    'dox_choose_first': [
        'Sorry {0}, aber zuerst müssen die Personen feststehen. Probier doch mal /random!',
    ],
    'dox_wrong_side': [
        'Sorry {0}, aber @{1} wählt Wahrheit oder Pflicht, und du darfst eine Frage/Aufgabe stellen!',
    ],
    'dox_not_involved': [
        'Sorry {0}, aber gerade ist @{1} dran. Und {2} stellt dann dementsprechend eine Frage oder Aufgabe.',
    ],
    'dox_already_w': [
        'Tja {0}, du hast schon Wahrheit gewählt. Jetzt musst du eine Frage von @{1} beantworten.',
    ],
    'dox_already_p': [
        'Tja {0}, du hast schon Pflicht gewählt. Jetzt musst du eine Aufgabe für @{1} erledigen.',
    ],
    'dox_w': [
        'Soso, {0} wählt Wahrheit. @{1}, welche Wahrheit möchtest du über {0} wissen?',
    ],
    'dox_p': [
        'Eine Pflicht für {0}, bitte! @{1}, was soll {0} denn machen?',
    ],
    'unknown_command': [
        'Häh?',
        'Was?',
        'Bestimmt weiß ich eines Tages, was das bedeuten soll.',
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
        f'\n/random → nächste Person zufällig aus der Runde wählen'
        f'\n/choose @username → nächste Person wählen'
        f'\n/wop → zufällig Wahrheit oder Pflicht wählen'
        f'\n/do_w → Wahrheit wählen'
        f'\n/do_p → Pflicht wählen'
        f'\n/who → wiederholt, wer zur Zeit dran ist'
        f'\n/kick → die zuletzt gewählte Person aus dem Spiel werfen (bleibt aber im Chat)'
        f'\n/players → schreibt in den Chat wer alles an der Runde teilnimmt'
        f'\nMehr macht der Bot nicht. Man muss selber Fragen stellen, Fragen beantworten, oder kapieren wann man dran ist :P'
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


def cmd_reset(update: Update, context: CallbackContext) -> None:
    if update.effective_user.username != secret.OWNER:
        return

    context.bot_data.clear()
    update.effective_message.reply_text('… I have no memory of this place.')


def cmd_for(command):
    def cmd_handler(update: Update, context: CallbackContext):
        if update.message is None or update.message.text is None:
            return  # Don't consider Updates that don't stem from a text message.
        text = update.message.text.split(' ', 1)
        argument = text[1] if len(text) == 2 else ''

        ongoing_game = get_chat_round(context.bot_data, update.effective_chat.id)
        maybe_response = logic.handle(ongoing_game, command, argument, update.effective_user.first_name, update.effective_user.username)
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
    dispatcher.add_handler(CommandHandler("do_w", cmd_for('do_w')))
    dispatcher.add_handler(CommandHandler("do_p", cmd_for('do_w')))
    dispatcher.add_handler(CommandHandler("choose", cmd_for('choose')))
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
