# Getting the code

Clone the repo, retrieving the submodules as well

```
git clone git@github.com:reactiveops/pentagon.git
cd pentagon
git submodule init
git submodule update
```

```
(kubernetes-demo) 870 justin:kubernetes-demo$ git clone git@github.com:reactiveops/pentagon.git testing-submods
Cloning into 'testing-submods'...
remote: Counting objects: 227, done.
remote: Compressing objects: 100% (8/8), done.
remote: Total 227 (delta 2), reused 0 (delta 0), pack-reused 218
Receiving objects: 100% (227/227), 56.96 KiB | 0 bytes/s, done.
Resolving deltas: 100% (53/53), done.
Checking connectivity... done.
(kubernetes-demo) 871 justin:kubernetes-demo$ cd testing-submods/
(kubernetes-demo) 872 justin:testing-submods$ git submodule init
Submodule 'vendor/kubernetes' (git@github.com:kubernetes/kubernetes.git) registered for path 'vendor/kubernetes'
(kubernetes-demo) 873 justin:testing-submods$ git submodule update
Cloning into 'vendor/kubernetes'...
remote: Counting objects: 302553, done.
remote: Compressing objects: 100% (53/53), done.
remote: Total 302553 (delta 43), reused 18 (delta 18), pack-reused 302482
Receiving objects: 100% (302553/302553), 277.38 MiB | 10.63 MiB/s, done.
Resolving deltas: 100% (198221/198221), done.
Checking connectivity... done.
Submodule path 'vendor/kubernetes': checked out 'e7503fde8ec6b3911dc7e22cae2619dc5bcec351'
(kubernetes-demo) 874 justin:testing-submods$
(kubernetes-demo) 874 justin:testing-submods$ cd vendor/kubernetes/
(kubernetes-demo) 875 justin:kubernetes$ git status
HEAD detached at e7503fd
nothing to commit, working directory clean
(kubernetes-demo) 876 justin:kubernetes$ git branch
* (HEAD detached at e7503fd)
  master
(kubernetes-demo) 877 justin:kubernetes$ #that's the latest commit of https://github.com/kubernetes/kubernetes/releases/tag/v1.2.7-beta.0
```
