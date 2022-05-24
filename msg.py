#!/usr/bin/env false

import secret

RANDOM_REPLY = {'how', 'where', 'why'}

MESSAGES = {
    'welcome': [
        'Alles klar, {0}!',
        'Na dann viel Spaß, {0}!',
        'Au weia, {0} ist mit von der Partie, das kann ja heiter werden!',
        'Schön, dass du dabei bist, {0}!',
        '{0}! Es ist eine Falle!',
        'Ahoi {0}!',
        'Hi {0}! Du verpflichtest dich also zur Wahrheit? ;)',
        'Hi {0}! Du bewahrheitest dich also zur Pflicht? ;)',
    ],
    'welcome_no_username': [
        'Sorry {0}, aber du musst einen @username haben, sonst komme ich nicht damit klar. :(',
    ],
    'already_in': [
        'Du bist doch schon drin, {0}! :D',
        'Geht nicht, du bist schon drin, {0}.',
        'Alzheimer, {0}? Du bist schon drin ;)',
        'Klar! Das geht sehr einfach, du bist nämlich schon drin, {0}! :D',
    ],
    'leave': [
        'Och, schade. Na bis dann, {0}!',
        'Na toll, Ihr habt {0} erfolgreich vergrault!',
        '{0} möchte uns verlassen! Schade, dann bis zum nächsten Mal.',
        'Ja dann GEH DOCH ZU NETTO! https://www.youtube.com/watch?v=YSMCC4sGkSo',
        'Aww, dann eben nicht mehr.',
        'Bis zum nächsten Mal, {0}!',
        'Es war mir ein Vergnügen. Bis dann, {0}! :)',
        'Brudi muss los!',
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
        'Weiter geht\'s mit @{0}: Wahrheit oder Pflicht? /do_w /do_p Oder /wop?',
        'Gleich hören wir eine Wahrheit oder eine Pflicht von @{0}! /do_w /do_p Oder /wop?',
    ],
    'random_not_involved': [
        'Warte noch etwas, {0}. Sobald @{2} fertig ist mit der Wahrheit/Pflicht an {1}, darf @{2} weitermachen mit /choose @username oder /random. Alternativ, schreibe /kick um @{2} aus der Runde zu schmeißen.',
    ],
    'random_already_chosen': [
        'Du hast doch schon jemanden gewählt, {0}? Und zwar @{1}!',
        'Das hättest du dir vorher überlegen müssen {0}. Jetzt ist @{1} schon dran.',
    ],
    'wop_nobodychosen': [
        'Ich bin verwirrt {0}, eigentlich ist zur Zeit niemand dran. Ich sag jetzt mal {1}, hilft das?',
        '{0}, du hast das goldene Ahnungslos gezogen. Magst du vielleicht {1} machen?',
    ],
    'wop_nobodychosen_COMMENT': '{1} ist \'Wahrheit\' oder \'Pflicht\'',
    'wop_nonchosen': [
        'Sorry {0}, aber gerade ist @{1} dran, Wahrheit oder Pflicht zu wählen.',
    ],
    'wop_again': [
        'Das steht doch schon fest, {0}? Es bleibt bei {1}. Jetzt entscheidet @{2}!',
    ],
    'wop_result_w': [
        'WAHRHEIT! @{1} darf eine Frage stellen, und du musst die Wahrheit sagen, {0}. (Oder sei ein feiges Huhn mit /chicken.)',
        'WAHRHEIT! @{1} stellt eine Frage, und {0} muss ehrlich antworten. Danach geht\'s mit /random weiter.',
    ],
    'wop_result_p': [
        'PLICHT! @{1} darf dir eine Aufgabe stellen, und du musst sie ausführen, {0}. (Oder sei ein feiges Huhn mit /chicken.)',
        'PLICHT! @{1} sagt an, und {0} muss tun. Danach geht\'s mit /random weiter.',
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
        'Im Moment ist @{1} dran, Wahrheit oder Pflicht zu wählen. (Oder falls schon gewählt wurde ohne /do_w / /do_p zu benutzen, dann muss @{0} sich eine Frage/Aufgabe ausdenken.)',
    ],
    'who_wop_w': [
        'Im Moment ist @{1} dran, denn es wurde Wahrheit gewählt, und muss jetzt {0} eine Frage beantworten. Wenn ihr fertig seid, darf @{1} mit /random den nächsten Spieler wählen. :)',
    ],
    'who_wop_p': [
        'Im Moment ist @{1} dran, denn es wurde Pflicht gewählt, und muss jetzt eine Aufgabe für {0} erledigen. Wenn ihr fertig seid, darf @{1} mit /random den nächsten Spieler wählen. :)',
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
        'Es spielen zur Zeit nur {1}. Will jemand mitmachen? /join :D',
    ],
    'players_few_other': [
        'Die Runde besteht lediglich aus {1}. Magst du mitmachen, {0}? /join ;)',
        'Es spielen zur Zeit nur {1}. Mach mit, und /join :D',
    ],
    'players_many_self': [
        'Die Runde besteht aus {1}.',
    ],
    'players_many_self_COMMENT': '{0} ist der Name des Fragenden',
    'players_many_other': [
        'Die Runde besteht aus {1}.',
    ],
    'players_many_other_COMMENT': '{0} ist der Name des Fragenden',
    'kick_nonplayer': [
        'Sorry {0}, aber du spielst nicht mit, also darfst du nicht Andere rauswerfen. Probier doch mal /join.',
    ],
    'kick_no_chosen': [
        'Sorry {0}, aber im Moment ist niemand dran, also kann ich die Person auch nicht kicken. Probier doch mal /random!',
    ],
    'kick': [
        'Tschüss @{1}! {0} hat dich rausgekickt. Du kannst gerne wieder /join-en.',
        'Okaydokey {0}, @{1} ist nicht mehr dabei.',
        'Okay, ich kicke @{1}. Wer zu spät kommt, den bestraft das Leben!',
    ],
    'uptime': [
        'Der Bot war hier das erste Mal {0} aktiv. Jetzt ist es {1}.',
    ],
    'chosen_empty': [
        'Und wen, {0}? Der /choose-Befehl braucht ein Argument, z.B. @{1} (nur halt … jemand Anderes).',
    ],
    'chosen_self': [
        'Tut mir Leid, aber du kannst dich nicht selbst wählen, {0}. Probier doch mal /random.',
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
        'Soso, {0} wählt Wahrheit. @{1}, welche Wahrheit möchtest du über {0} wissen? (Oder sei ein feiges Huhn mit /chicken.)',
        '@{1}, was würdest du gerne von {0} wissen? Danach geht\'s mit /random weiter.',
    ],
    'dox_p': [
        'Eine Pflicht für {0}, bitte! @{1}, was soll {0} denn machen? (Oder sei ein feiges Huhn mit /chicken.)',
        '{0} muss jetzt was tun! @{1}, was soll {0} denn machen? Danach geht\'s mit /random weiter.',
    ],
    'where': [
        'Genau hier, in *diesem* Chat, {0}!',
        'In diesem einfach zu bearbeitendem Dokument: {2}',
    ],
    'where_COMMENT': '{0} ist der Name des Fragenden, {1} der @username, und {2} ist der Link auf dieses Dokument',
    'why': [
        'Because … FUN! :D',
        'Because I said so!',
    ],
    'why_COMMENT': '{0} ist der Name des Fragenden, {1} der @username, und {2} ist der Link auf dieses Dokument',
    'how': [
        'Noch hat niemand die Regeln geschrieben :( Hier kann man meinen Text ändern: {2}',
        'Vorsicht! Ich How zurück!',
    ],
    'how_COMMENT': '{0} ist der Name des Fragenden, {1} der @username, und {2} ist der Link auf dieses Dokument',
    'chicken_not_involved': [
        'Tut mir Leid, {0}, aber du bist gerade nicht dran. Probier mal /random oder /who.',
    ],
    'chicken_not_involved_COMMENT': '{0} ist der Vorname der angesprochenen Person',
    'chicken_wrong_side': [
        'Nee, andersrum, {0}! Wenn @{1} ein feiges Hühnchen ist und sich vor der Aufgabe drücken will, kann es /chicken benutzen.',
    ],
    'chicken_wrong_side_COMMENT': '{0} ist der Vorname der angesprochenen Person, {1} ist der username (ohne @) der Person die gerade dran ist',
    'chicken_too_early': [
        'Zu früh, {0}! Zuerst wählst du eine Wahrheit oder eine Pflicht (mit /do_w, /do_p, pder zufällig mit /wop), dann bekommst du eine Aufgabe, und wenn du dann entscheidest ein feiges Hühnchen zu sein, *dann* kannst du /chicken benutzen.',
        'Bist du etwa präventiv ein feiges Huhn, {0}? Du hast ja noch nichtmal gewählt ob es Wahrheit oder Pflicht sein soll! /do_w /do_p /wop',
    ],
    'chicken_too_early_COMMENT': '{0} ist der Vorname der angesprochenen Person',
    'chicken_w': secret.MESSAGES_CHICKEN_W,
    'chicken_w_COMMENT': '{0} ist der Link auf dieses Dokument, {1} ist der Besitzer',
    'chicken_p': secret.MESSAGES_CHICKEN_P,
    'chicken_p_COMMENT': '{0} ist der Link auf dieses Dokument',
    'unknown_command': [
        'Häh?',
        'Was?',
        'Bestimmt weiß ich eines Tages, was das bedeuten soll.',
        'Ich habe nicht genügend Erfahrung, um diese Aufgabe auszuführen.',
    ],
    'debug1': [
        '{0}',
    ],
}
