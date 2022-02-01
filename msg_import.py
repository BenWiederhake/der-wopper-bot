#!/usr/bin/python3

import msg
import sys


def parse_data(data):
    messages = dict()
    current_key = None
    current_entry = 0
    for line in data.split('\n'):
        line = line.rstrip('\t')
        if not line:
            current_key = None
            current_entry = 0
            continue
        parts = line.split('\t')
        assert 1 <= len(parts) <= 2, (line, current_key, current_entry)
        if current_entry == 0:
            assert parts[0].startswith('/'), (current_entry, line)
            assert current_entry == 0, (line, current_key, current_entry)
            current_key = parts[0][1:]
            if len(parts) == 2:
                messages[current_key + '_COMMENT'] = parts[1]
            assert current_key not in messages, (line, current_key)
            messages[current_key] = []
        elif len(parts) == 1:
            assert parts[0] == str(current_entry), (line, current_key, current_entry)
        elif len(parts) == 2:
            assert parts[0] == str(current_entry), (line, current_key, current_entry)
            messages[current_key].append(parts[1])
        else:
            raise AssertionError((line, current_key, current_entry))
        current_entry += 1
    return messages


def escape(s):
    return s.replace('\\', '\\\\').replace("'", "\\'")


def pretty_print(messages):
    print('MESSAGES = {')
    for key, values in messages.items():
        if key.endswith('_COMMENT'):
            print(f"    '{key}': '{escape(values)}',")
            continue

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
    print(f'RANDOM_REPLY = {msg.RANDOM_REPLY}')
    print()
    if old_keys != new_keys:
        print(f'# WARNING: Lost keys {old_keys.difference(new_keys)}, stray keys {new_keys.difference(old_keys)}')
    pretty_print(parsed_data)


def run():
    data = sys.stdin.read()
    handle_import(data)


if __name__ == '__main__':
    run()
