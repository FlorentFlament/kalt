#!/usr/bin/env python3

# Requires the following packages:
# - tabulate
# - click

import sys
import json
import itertools

import click
from tabulate import tabulate

# Some interesting keys to use with the --keys command line option:
# - user.username
# - user.groups
# - objectRef.resource
# - verb
#
# Filters (--filters) can filter events based on scalars (like
# user.username) of lists (like user.groups).

def parse_logs(fname):
    events = []
    with open(fname) as fd:
        line = fd.readline()
        while line:
            yield json.loads(line)
            line = fd.readline()

def dict_fetch(initial_dict, deep_key):
    h = initial_dict
    try:
        for k in deep_key.split("."):
            h = h[k]
        return h
    except:
        return None

def filter_by(events, filters_sl):
    """
    filter_sl is a list of filter strings.
    Each string has the form:
    - key=value : keeps events for which the key is equal to value
    - key!=value : keeps events for which the key is different than value
    - key+value : keeps events for which the key is a list and value is in it
    - key-value : keeps events for which the key is a list and value is not in it
    """
    def build_filter(fts):
        if '+=' in fts:
            k,v = fts.split('+=')
            return lambda x:v in dict_fetch(x, k)
        elif '-=' in fts:
            k,v = fts.split('-=')
            return lambda x:v not in dict_fetch(x, k)
        elif '!=' in fts:
            k,v = fts.split('!=')
            return lambda x:v != dict_fetch(x, k)
        elif '=' in fts:
            k,v = fts.split("=")
            return lambda x:v == dict_fetch(x, k)
        else:
            raise(Exception(f"Operator not found in filter string: {fts}"))

    # Build compound filter
    for fts in filters_sl:
        events = filter(build_filter(fts), events)
    return events

def count_by(events, keys_l):
    result = {}
    for ev in events:
        comp_key = []
        for k in keys_l:
            comp_key.append(dict_fetch(ev, k))
        comp_key = tuple(comp_key)
        result[comp_key] = result.get(comp_key, 0) + 1
    return result

def display_stats(results, keys_t, limit):
    # results is a dictionary, where keys are tuples of values
    # corresponding to keys_l, and values counts of corresponding
    # events
    total_cnt = sum(results.values())
    headers = keys_t + ("count", "percent")
    table = []
    if limit == 0:
        limit = len(results)
    for k,v in sorted(results.items(), key=lambda x:x[1], reverse=True)[:limit]:
        percent = f"{v/total_cnt*100:.2f}"
        table.append(k + (v,percent)) # concatenate value to key tuple
    print(tabulate(table, headers=headers))
    print(f"\nTotal events count: {total_cnt}")

def dump_ev(events, limit):
    subset = events if limit == 0 else itertools.islice(events, 0, limit)
    for ev in subset:
        print(json.dumps(ev))

@click.command()
@click.argument('filename')
@click.option('--keys', '-k', multiple=True, default=["verb"], help='List of keys to count against. Can be used multiple times. Defaults to ["verb"].')
@click.option('--filters', '-f', multiple=True, default=[], help='List of key=value used to select a subset of audit logs. Can be used multiple times. Example: --filter "objectRef.resource=secrets" --filter "verb=get", Defaults to [].')
@click.option('--limit', '-l', default=0, help='Limit the output to the nth biggest results. Example: --limit 10. Defaults to 0, meaning no limit.')
@click.option('--dump', '-d', is_flag=True, help='Dump events rather than statistics.')
def main(filename, keys, filters, limit, dump):
    """Processes and displays statistics about FILENAME audit logs file."""
    events = filter_by(parse_logs(filename), filters)

    if dump:
        dump_ev(events, limit)
    else:
        display_stats(count_by(events, keys), keys, limit)

if __name__ == "__main__":
    main()
