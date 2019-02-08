# How to contribute

Issues, whether bugs, tasks, or feature requests are essential for keeping Pentagon (and ReactiveOps in general) great. We believe it should be as easy as possible to contribute changes that
get things working in your environment. There are a few guidelines that we
need contributors to follow so that we can have a chance of keeping on
top of things.
o

## Setting up your development environment

1. Clone this repo and cd into it
    ```
    git clone git@github.com:reactiveops/pentagon.git
    cd pentagon
    ```
2. Create a virtual environment and source it. You need to source everytime you want to develop pentagon.
    ```
    virtualenv venv 
    source venv/bin/activate
    ```
3. Finally, do `pip install -e . ` to install pentagon into the venv. The `-e` means that it will take any of your file changes into account.


## Getting Started

* Submit a ticket for your issue, assuming one does not already exist.
  * Clearly describe the issue including steps to reproduce when it is a bug.
  * Apply the appropriate labels, whether it is bug, feature, or task.

## Making Changes

* Create a feature branch from where you want to base your work.
  * This is usually the master branch.
  * To quickly create a topic branch based on master; `git checkout -b
    feature master`. Please avoid working directly on the
    `master` branch.
* Try to make commits of logical units.
* Make sure you have added the necessary tests for your changes (coming soon).
* Make sure you have added any required documentation changes.

## Making Trivial Changes

### Documentation

For changes of a trivial nature to comments and documentation, it is not
always necessary to create a new issue in GitHub. In these cases, a branch with pull request is sufficient.

## Submitting Changes

* Push your changes to a topic branch.
* Submit a pull request.
* Update the issue with the `PR-available` label to mark that you have submitted code and are ready for it to be reviewed, and include a link to the pull request in the ticket.


Attribution
===========
Portions of this text are copied from the [Puppet Contributing](https://github.com/puppetlabs/puppet/blob/master/CONTRIBUTING.md) documentation.
