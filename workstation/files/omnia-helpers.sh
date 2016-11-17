function enable-virtualenvwrapper {
    export WORKON_HOME=$HOME/workspace/venvs
    export PROJECT_HOME=$HOME/workspace/projects
    export VIRTUALENVWRAPPER_HOOK_DIR=$HOME/workspace/hooks
    export OMNIA_COOKIECUTTERS=$HOME/workspace/cookiecutters

    source /usr/local/bin/virtualenvwrapper.sh
}
