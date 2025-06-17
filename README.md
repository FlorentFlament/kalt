KALT stands for Kubernetes Audit Logs Toolkit

A tool to analyse existing `audit.log` files, possibly helping to
write meaningful `audit_policy.yml`.

# Install

```
$ pip install pykalt
```

# Usage

```
$ kalt --help
Usage: kalt [OPTIONS] FILENAMES...

  Processes and displays statistics about FILENAMES audit log files.

Options:
  -k, --keys TEXT      List of keys to count against. Can be used multiple
                       times. Defaults to ["verb"].
  -f, --filters TEXT   List of key=value used to select a subset of audit
                       logs. Can be used multiple times. Example: --filter
                       "objectRef.resource=secrets" --filter "verb=get", the
                       operator must be in ['=','!=','>=','<=','+=','-='].
                       Defaults to [].
  -l, --limit INTEGER  Limit the output to the nth biggest results. Example:
                       --limit 10. Defaults to 0, meaning no limit.
  -d, --dump           Dump events rather than displaying statistics.
  -g, --groups         Group by user.groups.
  --help               Show this message and exit.
```

# Filters

Possible filters:

- key=value : keeps events for which the event[key] is equal to value
- key!=value : keeps events for which the event[key] is different than value
- key>=value : keeps events for which the event[key] is greater or equal than value (i.e for datetimes)
- key<=value : keeps events for which the event[key] is lesser or equal than value
- key+=value : keeps events for which the event[key] is a list and value is in it
- key-=value : keeps events for which the event[key] is a list and value is not in it


# Example

```
$ kalt -f 'user.groups+=system:serviceaccounts' -k user.username -k verb -k objectRef.resource -l 10 audit.log
user.username                                                       verb    objectRef.resource       count    percent
------------------------------------------------------------------  ------  ---------------------  -------  ---------
system:serviceaccount:kube-system:resourcequota-controller          get                                370      35.92
system:serviceaccount:kube-system:generic-garbage-collector         get                                370      35.92
system:serviceaccount:kube-system:snapshot-webhook                  watch   volumesnapshotclasses       48       4.66
system:serviceaccount:default:e5383c71-a248-4790-b6f2-18ccda0a024f  create  pods                        32       3.11
system:serviceaccount:vmware-system-csi:vsphere-csi-webhook         watch   configmaps                  28       2.72
system:serviceaccount:default:e5383c71-a248-4790-b6f2-18ccda0a024f  get                                 27       2.62
system:serviceaccount:kube-system:coredns                           watch   endpointslices              26       2.52
system:serviceaccount:kube-system:coredns                           watch   namespaces                  26       2.52
system:serviceaccount:kube-system:coredns                           watch   services                    26       2.52
system:serviceaccount:pks-system:fluent-bit                         get     pods                        25       2.43

Events count: 1030 (1.81% of 56915 events)
Period: 0 days, 2 hours and 32 mins; from "2025-06-03 11:33:07" to "2025-06-03 13:05:32"
```
