#!/usr/bin/python3

import msg


def do_export(messages):
    for msg_id, msg_coll in messages.items():
        if msg_id.endswith('_COMMENT'):
            continue

        comment = messages.get(msg_id + '_COMMENT', None)
        print(f'/{msg_id}')
        if comment:
            print(f'# {comment}')
        for msg_val in msg_coll:
            print(f'- {msg_val}')
        print()


def run():
    do_export(msg.MESSAGES)

    had_problem = False
    for key in msg.RANDOM_REPLY:
        if key not in msg.MESSAGES:
            print(f'"{key}" in msg.RANDOM_REPLY but not in msg.MESSAGES?!')
            had_problem = True

    if had_problem:
        exit(1)


if __name__ == '__main__':
    run()
