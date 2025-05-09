KALT stands for Kubernetes Audit Logs Toolkit

The aim is to write a few scripts to analyse existing `audit.log`
files to help writing meaningful `audit_policy.yml` focusing on useful
Kubernetes events.

- kastats.py displays occurence statistics, grouped by provided keys,
  possibly filtering the output. See `kastats.py --help`.

Example:

```
$ kastats.py --keys verb --select objectRef.resource=secrets --limit 10 lab-audit.log
verb      count    percent
------  -------  ---------
watch       259      85.48
get          18       5.94
list         13       4.29
create        7       2.31
delete        6       1.98

Total events count: 303
```
