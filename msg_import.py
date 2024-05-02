#!/usr/bin/python3

import msg
import sys


def parse_data(data):
    messages = dict()
    current_key = None

    for line in data.split('\n'):
        line = line.rstrip('\t\r ')
        if not line or line == '-':
            current_key = None
            continue

        if not current_key:
            assert line[0] == '/', line
            current_key = line[1:]
            assert current_key not in messages, (current_key, line)
            messages[current_key] = []
            continue
        assert line[0] != '/', (current_key, line)

        if line[0] == '#':
            comment_key = f'{current_key}_COMMENT'
            assert comment_key not in messages, (comment_key, line)
            messages[comment_key] = line[1:].strip()
            continue

        assert line[0] == '-', (current_key, line)
        messages[current_key].append(line[1:].strip())

    return messages


def escape(s):
    return s.replace('\\', '\\\\').replace("'", "\\'")


def pretty_print(messages):
    print('MESSAGES = {')
    for key, values in messages.items():
        if key.endswith('_COMMENT'):
            print(f"    '{key}': '{escape(values)}',")
            continue

        if key == 'chicken_w':
            print("    'chicken_w': secret.MESSAGES_CHICKEN_W,")
        if key == 'chicken_p':
            print("    'chicken_p': secret.MESSAGES_CHICKEN_P,")
        print(f"    '{key}': [")
        for v in values:
            print(f"        '{escape(v)}',")
        print("    ],")
    print("}")


def handle_import(data):
    parsed_data = parse_data(data)
    old_keys = set(msg.MESSAGES.keys())
    new_keys = set(parsed_data.keys())

    print('#!/usr/bin/env false')
    print()
    print('import secret')
    print()
    delimiter = "', '"
    print(f'RANDOM_REPLY = {{\'{delimiter.join(sorted(msg.RANDOM_REPLY))}\'}}')
    print()
    if old_keys != new_keys:
        print(f'# WARNING: Lost keys {old_keys.difference(new_keys)}, new keys {new_keys.difference(old_keys)}')
    pretty_print(parsed_data)


def run():
    data = sys.stdin.read()
    handle_import(data)


if __name__ == '__main__':
    run()
