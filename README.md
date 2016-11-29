# Pentagon

Infrastructure to spin up ReactiveOps style Kubernetes clusters.

## Setup VirtualEnvWrapper

* Clone this repo `git clone `git@github.com:reactiveops/pentagon.git`
* `pushd workstation`
* `./setup.sh`
* `source ~/.bash_profile`
* `mkproject <projectname>` for an example, see [hillghost](https://github.com/reactiveops/hillghost-infrastructure)



*TODO: Update everything below*
~~Various bits of information are available in [docs/](docs/). You may particularly wish to review [notes.md](docs/notes.md).
 Currently this spins up a cluster in only one AZ. Spreading it around will require additional thought and an eye toward [Running in Multiple Zones](http://kubernetes.io/docs/admin/multiple-zones/).~~



See [docs/kops.md](docs/kops.md)

# startproject

```
$ pentagon-startproject -n foo
```
