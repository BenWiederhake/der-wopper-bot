#!/usr/bin/python3

import msg


def do_export(messages):
    for msg_id, msg_coll in messages.items():
        if msg_id.endswith('_COMMENT'):
            continue

        comment = messages.get(msg_id + '_COMMENT', None)
        if comment is None:
            comment_suffix = ''
        else:
            comment_suffix = '\t' + comment
        print('/' + msg_id + comment_suffix)
        for i, msg_val in enumerate(msg_coll):
            print('\t'.join((str(i + 1), msg_val)))
        for i in range(len(msg_coll), len(msg_coll) + 5):
            print(i + 1)
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
