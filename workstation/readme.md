#http://gillesfabio.com/blog/2011/03/01/rvm-for-pythonistas-virtualenv-for-rubyists/

we could have a repo called omnia hooks such that:

git clone omnia-hooks.git hooks did the needful.

Or, we can have a omnia-tools repo that had a hooks dir inside it, and you'd cp -a (path)/hooks to hooks/


it depends on whether or not there are any other tools needed.

Setup can be:
workspace=path-to-workspace
mkdir -p $workspace/projects $workspace/venvs $workspace/hooks.

Add this to your bash_profile:

```
function enable-virtualenvwrapper {
    export WORKON_HOME=$workspace/venvs
    export PROJECT_HOME=$workspace/projects
    export VIRTUALENVWRAPPER_HOOK_DIR=$workspace/hooks
    source /usr/local/bin/virtualenvwrapper.sh
}
```
git clone omnia-tools.git hooks; cp -a omnia-tools/hooks $workspace/hooks
# end of setup

* Then when you want to work:
enable-virtualenvwrapper
workon ...
mkproject uid (reactr)
git clone $INFRASTRUCTURE_REPO