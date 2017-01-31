function enable-virtualenvwrapper {
    export WORKON_HOME=$HOME/workspace/venvs
    export PROJECT_HOME=$HOME/workspace/projects
    export VIRTUALENVWRAPPER_HOOK_DIR=$HOME/workspace/hooks

    source /usr/local/bin/virtualenvwrapper.sh
}
