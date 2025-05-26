KALT stands for Kubernetes Audit Logs Toolkit

A tool to analyse existing `audit.log` files, possibly helping to
write meaningful `audit_policy.yml`.

# Install

```
$ pip install pykalt
```

# Usage

```
$ kalt -f 'objectRef.resource!=leases' -k user.username -k verb -k objectRef.resource -l 10 audit-*
user.username                                                verb    objectRef.resource      count    percent
-----------------------------------------------------------  ------  --------------------  -------  ---------
ncp                                                          update  nsxlocks                 8395      13.77
system:apiserver                                             get     endpoints                5047       8.28
system:apiserver                                             get     endpointslices           5047       8.28
kubelet                                                      get     nodes                    4946       8.11
system:serviceaccount:kube-system:resourcequota-controller   get                              3364       5.52
system:serviceaccount:kube-system:generic-garbage-collector  get                              3364       5.52
system:serviceaccount:kube-system:metrics-server             create  subjectaccessreviews     1728       2.83
kubelet                                                      watch   configmaps               1132       1.86
kubelet                                                      watch   secrets                   892       1.46
kubelet                                                      list    nodes                     840       1.38

Events count: 60957 (14.96% of 407338 events)
Period: 14.02 hours from 2025-05-22 17:22:43 to 2025-05-23 07:23:53
```
