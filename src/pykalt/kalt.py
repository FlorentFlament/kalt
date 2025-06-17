#!/usr/bin/env python3

import datetime
import importlib.metadata # To get the package version
import itertools
import json

import click
from tabulate import tabulate

# Filters (--filters) can filter events based on scalars (like
# user.username) of lists (like user.groups).
#
# Some interesting keys to use with the --filters command line option:
# - user.username
# - user.groups
# - objectRef.resource
# - verb

# Keep track of a few stats globally (could be moved to some class at
# some point)
datetime_first = None
datetime_last = None
events_count = 0

def parse_event_timestamp(ev):
    return datetime.datetime.strptime(ev["stageTimestamp"], "%Y-%m-%dT%H:%M:%S.%f%z")

def get_lines(filenames):
    """Yield lines of multiple files sequentially."""
    for fn in filenames:
        with open(fn) as fd:
            ln = fd.readline()
            while ln:
                yield ln
                ln = fd.readline()

def parse_logs(lines):
    global datetime_first, datetime_last, events_count
    line = next(lines)
    datetime_first = parse_event_timestamp(json.loads(line))
    for line in lines:
        events_count+= 1
        ev = json.loads(line)
        yield ev
    datetime_last = parse_event_timestamp(ev)

def dict_fetch(initial_dict, deep_key):
    h = initial_dict
    try:
        for k in deep_key.split("."):
            h = h[k]
        return h
    except:
        # A value equal to '' will be treated as a missing value
        return '' # Allows filtering on a missing value

def filter_by(events, filters_sl):
    """
    filters_sl is a list of filter strings.
    Each string has the form:
    - key=value : keeps events for which the event[key] is equal to value
    - key!=value : keeps events for which the event[key] is different than value
    - key>=value : keeps events for which the event[key] is greater or equal than value (i.e for datetimes)
    - key<=value : keeps events for which the event[key] is lesser or equal than value
    - key+=value : keeps events for which the event[key] is a list and value is in it
    - key-=value : keeps events for which the event[key] is a list and value is not in it
    """
    def build_filter(fts):
        if '+=' in fts:
            k,v = fts.split('+=')
            return lambda x:v in dict_fetch(x, k)
        elif '-=' in fts:
            k,v = fts.split('-=')
            return lambda x:v not in dict_fetch(x, k)
        elif '>=' in fts:
            k,v = fts.split(">=")
            # exemple: stageTimestamp>=2025-05-27
            # v = 2025-05-27
            return lambda x:dict_fetch(x, k) >= v
        elif '<=' in fts:
            k,v = fts.split("<=")
            return lambda x:dict_fetch(x, k) <= v
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

def count_by_group(events):
    result = {}
    for ev in events:
        for grp in dict_fetch(ev, "user.groups"):
            result[(grp,)] = result.get((grp,), 0) + 1
    return result

def display_stats(results, keys_t, limit):
    # results is a dictionary, where keys are tuples of values
    # corresponding to keys_l, and values counts of corresponding
    # events
    cnt = sum(results.values())
    headers = keys_t + ("count", "percent")
    table = []
    if limit == 0:
        limit = len(results)
    for k,v in sorted(results.items(), key=lambda x:x[1], reverse=True)[:limit]:
        percent = f"{v/cnt*100:.2f}"
        table.append(k + (v,percent)) # concatenate value to key tuple

    def hdt(dt):
        return datetime.datetime.strftime(dt, "%Y-%m-%d %H:%M:%S")

    # Displaying using a few globals
    print(tabulate(table, headers=headers))
    print(f"\nEvents count: {cnt} ({cnt*100/events_count:.2f}% of {events_count} events)")
    period = datetime_last - datetime_first
    print(f"Period: {period.days} days, {period.seconds/3600:.0f} hours and {(period.seconds%3600)/60:.0f} mins;"
          + f" from \"{hdt(datetime_first)}\" to \"{hdt(datetime_last)}\"")

def dump_ev(events, limit):
    subset = events if limit == 0 else itertools.islice(events, 0, limit)
    for ev in subset:
        print(json.dumps(ev))

@click.command()
@click.argument('filenames', nargs=-1, required=False)
@click.option('--keys', '-k', multiple=True, default=["verb"], help='List of keys to count against. Can be used multiple times. Defaults to ["verb"].')
@click.option('--filters', '-f', multiple=True, default=[], help='List of key=value used to select a subset of audit logs. Can be used multiple times. Example: --filter "objectRef.resource=secrets" --filter "verb=get", the operator must be in [\'=\',\'!=\',\'>=\',\'<=\',\'+=\',\'-=\']. Defaults to [].')
@click.option('--limit', '-l', default=0, help='Limit the output to the nth biggest results. Example: --limit 10. Defaults to 0, meaning no limit.')
@click.option('--dump', '-d', is_flag=True, help='Dump events rather than displaying statistics.')
@click.option('--groups', '-g', is_flag=True, help='Group by user.groups.')
@click.option('--version', '-v', is_flag=True, help='Display version and exit.')
def main(filenames, keys, filters, limit, dump, groups, version):
    """Processes and displays statistics about FILENAMES audit log files."""
    events = filter_by(parse_logs(get_lines(filenames)), filters)

    if version:
        print(f"kalt version: {importlib.metadata.version('pykalt')}")
    elif len(filenames) == 0:
        print("Error: FILENAMES are missing (use --help for usage).")
        exit(1)
    elif dump:
        dump_ev(events, limit)
    elif groups:
        display_stats(count_by_group(events), ("user.groups",), limit)
    else:
        display_stats(count_by(events, keys), keys, limit)

if __name__ == "__main__":
    main()
