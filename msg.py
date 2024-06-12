#!/usr/bin/env false

import secret

RANDOM_REPLY = {'how', 'kill', 'where', 'why'}

MESSAGES = {
    'welcome': [
        'Alles klar, {0}!',
        'Na dann, viel Spaß, {0}!',
        'Au weia, {0} ist mit von der Partie, das kann ja heiter werden!',
        'Schön, dass du dabei bist, {0}!',
        '{0}! Es ist eine Falle!',
        'Ahoi {0}!',
        'Hi {0}! Du verpflichtest dich also zur Wahrheit? ;)',
        'Hi {0}! Du bewahrheitest dich also zur Pflicht? ;)',
        'Oh, {0}! Gnihihi!',
        'Herzlich Willkommen {0}.',
        'Oh, ein neuer Mensch :)',
        'Wir haben Nachwuchs bekommen!',
    ],
    'welcome_no_username': [
        'Sorry {0}, aber du musst einen @username haben, sonst komme ich nicht damit klar. :(',
    ],
    'already_in': [
        'Du bist doch schon drin, {0}! :D',
        'Geht nicht, du bist schon drin, {0}.',
        'Alzheimer, {0}? Du bist schon drin ;)',
        'Klar! Das geht sehr einfach, du bist nämlich schon drin, {0}! :D',
        'Du möchtest gleich zweimal mitmachen, {0}? Ganz schön motiviert heute!',
    ],
    'leave': [
        'Och, schade. Na bis dann, {0}!',
        'Na toll, ihr habt {0} erfolgreich vergrault!',
        '{0} möchte uns verlassen! Schade, dann bis zum nächsten Mal.',
        'Ja dann GEH DOCH ZU NETTO! https://www.youtube.com/watch?v=YSMCC4sGkSo',
        'Aww, dann eben nicht mehr.',
        'Bis zum nächsten Mal, {0}!',
        'Es war mir ein Vergnügen. Bis dann, {0}! :)',
        'Brudi muss los!',
        'Flieht, ihr Narren!',
        'Was, du möchtest schon gehen, {0}?!',
        '{0}, lass uns gemeinsam in den Sonnenuntergang laufen! <3',
        'Aber du kannst uns doch nicht einfach so alleine lassen!',
        'Sicher, dass du nicht lieber kommen möchtest?',
        'Don\'t LEAF me!',
    ],
    'leave_COMMENT': '{0} ist der Vorname der angesprochenen Person',
    'leave_chooser_dunno': [
        'Tschüss {0}! Tja, damit ist keiner mehr dran. Macht mal jemand /random, bitte?',
        'Ohne {0} ist garniemand mehr dran. Kann jemand bitte /random machen?',
    ],
    'leave_chooser_dunno_COMMENT': '{0} ist der Vorname der angesprochenen Person',
    'leave_chooser_handover': [
        'Ciao {0}! Das heißt für @{1}: Wenn du fertig bist, einfach mit /random weitermachen.',
    ],
    'leave_chooser_handover_COMMENT': '{0} ist der Vorname der angesprochenen Person, {1} der Username des verbleibenden Aufgaben-Erledigenden',
    'leave_chosen_dunno': [
        'Äh, ja, tschüss {0}. Und wer macht jetzt weiter? Könnte jemand bitte /random machen?',
        'Du kannst mich doch nicht einfach so alleine lassen, {0}! Schnell, kann jemand bitte /random machen?!',
    ],
    'leave_chosen_dunno_COMMENT': '{0} ist der Vorname der angesprochenen Person',
    'leave_chosen_flee': [
        'Soso, {0} flieht. Dann würde ich sagen @{1} macht direkt nochmal mit /random weiter, oder?',
        'Tja, ohne {0} kommt @{1} halt nochmal dran. Weiter geht\'s mit /random.',
    ],
    'leave_chosen_flee_COMMENT': '{0} ist der Vorname der angesprochenen Person, {1} der Username des verbleibenden Aufgaben-Stellenden',
    'already_left': [
        'Pöh! Du warst sowieso nicht in der Runde, {0}!',
        'Mehr als "nicht dabei" geht nicht {0}.',
        'Zweimal gehen ist fast schon wegrennen. Magst du uns so wenig?',
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
        '@{0} hat das große Los gezogen und ist dran: Wahrheit oder Pflicht? /do_w /do_p oder /wop?',
        'Weiter geht\'s mit @{0}: Wahrheit oder Pflicht? /do_w /do_p oder /wop?',
        'Gleich hören wir eine Wahrheit oder eine Pflicht von @{0}! /do_w /do_p oder /wop?',
        'Die Qual der Wahl, was möchtest du @{0}? Pflicht oder Wahrheit? /do_w /do_p oder /wop?',
    ],
    'random_not_involved': [
        'Warte noch etwas, {0}. Sobald @{2} fertig ist mit der Wahrheit/Pflicht an {1}, darf @{2} weitermachen mit /choose @username oder /random. Alternativ, schreibe /kick um @{2} aus der Runde zu schmeißen.',
    ],
    'random_already_chosen': [
        'Du hast doch schon jemanden gewählt, {0}? Und zwar @{1}!',
        'Das hättest du dir vorher überlegen müssen {0}. Jetzt ist @{1} schon dran.',
    ],
    'random_nowop': [
        'Einen Moment, @{0}! Zuerst muss du zwischen Wahrheit (/do_w), Pflicht (/do_p), oder Zufall (/wop) wählen. Und {1} gibt dir dann die entsprechende Aufgabe.',
        'Hast du schon eine Wahrheit oder Pflicht für {1} gemacht? Bitte wähle Wahrheit (/do_w), Pflicht (/do_p), oder Zufall (/wop), @{0}! ;)',
    ],
    'random_nowop_COMMENT': '@{0} ist der Spieler der noch zwischen Wahrheit/Pflicht/Zufall entscheiden muss, und {1} ist der Vorname des aufgabenstellenden Spielers.',
    'wop_nobodychosen': [
        'Ich bin verwirrt {0}, eigentlich ist zur Zeit niemand dran. Ich sag jetzt mal {1}, hilft das?',
        '{0}, du hast das goldene Ahnungslos gezogen. Magst du vielleicht {1} machen?',
    ],
    'wop_nobodychosen_COMMENT': '{1} ist \'Wahrheit\' oder \'Pflicht\'',
    'wop_nonchosen': [
        'Sorry {0}, aber gerade ist @{1} dran, Wahrheit oder Pflicht zu wählen.',
    ],
    'wop_again': [
        'Das steht doch schon fest, {0}? Es bleibt bei {1}. Jetzt entscheidet @{2} die Aufgabe!',
    ],
    'wop_result_w': [
        'WAHRHEIT! @{1} darf eine Frage stellen, und du musst die Wahrheit sagen, {0}. (Oder sag /nope.)',
        'WAHRHEIT! @{1} stellt eine Frage, und {0} muss ehrlich antworten. Danach geht\'s mit /random weiter.',
    ],
    'wop_result_p': [
        'PFLICHT! @{1} darf dir eine Aufgabe stellen, und du musst sie ausführen, {0}. (Oder schreibe /nope und mach was Anderes.)',
        'PFLICHT! @{1} sagt an, und {0} muss tun. Danach geht\'s mit /random weiter.',
        'Die PFLICHT ruft! @{1} sagt dir, was zu tun ist!',
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
        'Gerade wählt @{0} zwischen Wahrheit (/do_w), Pflicht (/do_p), oder Zufall (/wop). (Danach wird dann {1} eine Frage/Aufgabe stellen.)',
    ],
    'who_no_wop_COMMENT': '{0} ist der Username woppenden Person, {1} ist der Vorname der aufgebenden Person.',
    'who_wop_w': [
        'Im Moment ist @{1} dran, denn es wurde Wahrheit gewählt, und muss jetzt {0} eine Frage beantworten. Wenn ihr fertig seid, darf @{1} mit /random den nächsten Spieler wählen. :)',
    ],
    'who_wop_p': [
        'Im Moment ist @{1} dran, denn es wurde Pflicht gewählt, und muss jetzt eine Aufgabe für {0} erledigen. Wenn ihr fertig seid, darf @{1} mit /random den nächsten Spieler wählen. :)',
    ],
    'players_nobody': [
        'Sorry {0}, im Moment spielt keiner. PFLICHT: Alle müssen /join schreiben, und irgendjemand schreibt /random! :D',
        'Sorry {0}, im Moment spielt keiner. PFLICHT: Schreibe coolere, tollere Bot-Nachrichten in dieses Dokument ein! :D {1}',
    ],
    'players_nobody_COMMENT': '{0} ist der Name des Fragenden und {1} ist der Link auf dieses Dokument',
    'players_one_self': [
        'Du spielst gerade mit dir selbst, {0}. Mach wenigstens die Kamera an!',
        'Sorry, du bist ganz alleine, {0}. :( Mag jemand mitmachen? Einfach /join schreiben! :D',
        'It\'s like you\'re my mirror, my mirror staring back at me… 🎶 Wenn noch jemand /join schreibt funktioniert das alles besser!',
        'All by my seeelf… 🎶  Du musst noch jemanden suchen, der auch /join schreibt.',
        'Sorry, es gibt gerade keine anderen Spieler, {0} :( Du könntest dir in der Zwischenzeit tolle neue Nachrichten ausdenken, und sie dort eintragen: {2}',
    ],
    'players_one_self_COMMENT': '{0} ist der Name des Fragenden, {1} ist der einzige Spielende, und {2} ist der Link auf dieses Dokument',
    'players_one_other': [
        'Im Moment spielt {1} mit sich selbst. Komm schon {0}, komm dazu und schreibe /join! :D',
        'Im Moment spielt nur {1}. Mach mit und schreibe /join! :D',
    ],
    'players_one_other_COMMENT': '{0} ist der Name des Fragenden, {1} ist der einzige Spielende, und {2} ist der Link auf dieses Dokument',
    'players_few_self': [
        'Die Runde besteht lediglich aus {1}. Überrede doch ein paar Leute dazu, zu joinen, {0}!',
        'Es spielen zur Zeit nur {1}. Will jemand mitmachen? /join :D',
    ],
    'players_few_self_COMMENT': '{0} ist der Name des Fragenden, {1} ist die Komma-verbundene Liste der Vornamen der Spieler:innen.',
    'players_few_other': [
        'Die Runde besteht lediglich aus {1}. Magst du mitmachen, {0}? /join ;)',
        'Es spielen zur Zeit nur {1}. Mach mit, und /join :D',
    ],
    'players_few_other_COMMENT': '{0} ist der Name des Fragenden, {1} ist die Komma-verbundene Liste der Vornamen der Spieler:innen.',
    'players_many_self': [
        'Die Runde besteht aus {2} Leuten: {1}.',
        'Satte {2} Spieler:innen: {1}.',
    ],
    'players_many_self_COMMENT': '{0} ist der Name des Fragenden, {1} ist die Komma-verbundene Liste der Vornamen der Spieler, {2} ist die Anzahl Spieler:innen.',
    'players_many_other': [
        'Die Runde besteht aus {2} Leuten: {1}.',
        'Satte {2} Spieler:innen: {1}.',
    ],
    'players_many_other_COMMENT': '{0} ist der Name des Fragenden, {1} ist die Komma-verbundene Liste der Vornamen der Spieler, {2} ist die Anzahl Spieler:innen.',
    'kick_nonplayer': [
        'Sorry {0}, aber du spielst nicht mit, also darfst du nicht Andere rauswerfen. Probier doch mal /join.',
        'Nur Menschen die mitspielen dürfen andere Mitspielende hier treten. Mit /join kannst du mitspielen!',
    ],
    'kick_no_chosen': [
        'Sorry {0}, aber im Moment ist niemand dran, also kann ich die Person auch nicht kicken. Probier doch mal /random!',
    ],
    'kick_self': [
        'I\'m sorry, {0}, I\'m afraid I can\'t let you do that: Du hast versucht dich selbst zu kicken. Du könntest auch einfach mit /random weitermachen?',
        'Eigentlich bist ja im Moment *du* dran, {0}! 🤔 Weiter geht\'s mit /random.',
        'Du trittst dir selbst in den Hintern, {0}, im wahrsten Sinne des Wortes! Probier doch mal /random.',
    ],
    'kick_self_COMMENT': '{0} ist der Vorname der Person, die sich selbst kicken will.',
    'kick': [
        'Tschüss @{1}! {0} hat dich rausgekickt. Du kannst gerne wieder /join-en, @{1}.',
        'Okaydokey {0}, @{1} ist nicht mehr dabei.',
        'Okay, ich kicke @{1}. Wer zu spät kommt, den bestraft das Leben! (Du kannst aber gerne wieder /join-en!)',
        '@{1} exit stage left.',
        'Tschüss @{1}! Bis zur nächsten Runde :D (Oder sofort wieder /join-en?)',
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
        'Ich kenne wohl noch nicht alle Namen und Personen richtig. Wen meintest du, {0}? Vielleicht kenne ich ja den @Usernamen, zum Beispiel @{1}.',
    ],
    'dox_choose_first': [
        'Sorry {0}, aber zuerst müssen die Personen feststehen. Probier doch mal /random!',
    ],
    'dox_no_chooser': [
        'Ohne Auftrag-Geber gibt es keine Wahrheit oder Pflicht. Mach doch einfach mit /random weiter, @{0}! :)',
        'Sorry @{0}, aber es gibt keine Wahrheit oder Pflicht ohne Fragen- oder Aufgaben-Steller. Weiter geht\'s mit /random.',
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
        'Soso, {0} wählt Wahrheit. @{1}, welche Wahrheit möchtest du über {0} wissen? (Oder mach /nope und beantworte was Anderes.)',
        '@{1}, was würdest du gerne von {0} wissen? Danach geht\'s mit /random weiter.',
    ],
    'dox_p': [
        'Eine Pflicht für {0}, bitte! @{1}, was soll {0} denn machen? (Oder /nope zu dieser Pflicht, dann bekommst du eine Andere.)',
        '{0} muss jetzt was tun! @{1}, was soll {0} denn machen? Danach geht\'s mit /random weiter.',
    ],
    'do_idc_w': [
        '{0} Wahrheit für @{1}',
    ],
    'do_idc_p': [
        'Pflicht {0} für @{1}',
    ],
    'where': [
        'Genau hier, in *diesem* Chat, {0}!',
        'In diesem einfach zu bearbeitendem Dokument: {2}',
        'Schau doch mal in {2} , {0}.',
    ],
    'where_COMMENT': '{0} ist der Name des Fragenden, {1} der @username, und {2} ist der Link auf dieses Dokument',
    'why': [
        'Because … FUN! :D',
        'Because I said so!',
        'Du könntest hier eine bessere Antwort einfügen: {2}',
    ],
    'why_COMMENT': '{0} ist der Name des Fragenden, {1} der @username, und {2} ist der Link auf dieses Dokument',
    'how': [
        'Noch hat niemand die Regeln geschrieben :( Hier kann man meinen Text ändern: {2}',
        'Bisher gibt es keine Anleitung. Aber man kann eine schreiben, in diesem Dokument: {2}. Es ist sehr gut.',
        'Vorsicht! Ich How zurück!',
    ],
    'how_COMMENT': '{0} ist der Name des Fragenden, {1} der @username, und {2} ist der Link auf dieses Dokument',
    'kill': [
        'Boah bist du brutal, {0}! Meintest du vielleicht /kick?',
        'Hier wird niemand umgebracht, {0}! Höchstens rausgeworfen, mit /kick.',
    ],
    'kill_COMMENT': '{0} ist der Name des Fragenden, {1} der @username, und {2} ist der Link auf dieses Dokument',
    'chicken_not_involved': [
        'Tut mir Leid, {0}, aber du bist gerade nicht dran. Probier mal /random oder /who.',
    ],
    'chicken_not_involved_COMMENT': '{0} ist der Vorname der angesprochenen Person',
    'chicken_wrong_side': [
        'Nee, andersrum, {0}! Wenn @{1} nicht will und sich vor der Aufgabe drücken will, kann es /nope benutzen.',
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
        'Wenn ich mal groß und stark bin kann ich das auch!',
        '🥺',
    ],
    'debug1': [
        '{0}',
    ],
}
