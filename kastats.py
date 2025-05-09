#!/usr/bin/env python3

# Requires the following packages:
# - tabulate
# - click

import sys
import json

import click
from tabulate import tabulate

# Some interesting keys to use with the --keys command line option:
# - user.username
# - objectRef.resource
# - verb

def parse_logs(fname):
    events = []
    with open(fname) as fd:
        for line in fd.readlines():
            events.append(json.loads(line))
    return events

def dict_fetch(initial_dict, deep_key):
    h = initial_dict
    try:
        for k in deep_key.split("."):
            h = h[k]
        return h
    except:
        return None

def count_by(events, keys_l):
    result = {}
    for ev in events:
        comp_key = []
        for k in keys_l:
            comp_key.append(dict_fetch(ev, k))
        comp_key = tuple(comp_key)
        result[comp_key] = result.get(comp_key, 0) + 1
    return result
            
def display(results, keys_t):
    # results is a dictionary, where keys are tuples of values
    # corresponding to keys_l, and values counts of corresponding
    # events
    total_cnt = sum(results.values())
    headers = keys_t + ("count", "percent")
    table = []
    for k,v in sorted(results.items(), key=lambda x:x[1], reverse=True):
        percent = f"{v/total_cnt*100:.2f}"
        table.append(k + (v,percent)) # concatenate value to key tuple
    print(tabulate(table, headers=headers))
    print(f"\nTotal events count: {total_cnt}")

@click.command()
@click.argument('filename')
@click.option('--keys', '-k', multiple=True, default=["verb"], help='List of keys to count against. Can be used multiple times. Default to ["verb"].')
def main(filename, keys):
    """Processes and displays statistics about FILENAME audit logs file."""
    events = parse_logs(filename)
    result = count_by(events, keys)
    display(result, keys)

if __name__ == "__main__":
    main()
