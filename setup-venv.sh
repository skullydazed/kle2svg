#!/bin/sh

# Determine our python version
if [ -z "$PYTHON_VERSION" ]; then
    if python3 --version > /dev/null; then
        PYTHON_VERSION=3
    elif python3.5 --version > /dev/null; then
        PYTHON_VERSION=3.5
    elif python3.4 --version > /dev/null; then
        PYTHON_VERSION=3.5
    elif python3.3 --version > /dev/null; then
        PYTHON_VERSION=3.5
    elif python3.2 --version > /dev/null; then
        PYTHON_VERSION=3.5
    elif python3.1 --version > /dev/null; then
        PYTHON_VERSION=3.5
    elif python3.0 --version > /dev/null; then
        PYTHON_VERSION=3.5
    elif python2.7 --version > /dev/null; then
        PYTHON_VERSION=2.7
    else
        echo 'Can not determine python version. Please set PYTHON_VERSION!'
	exit 1
    fi
fi

# Do some sanity checking
if ! [ -f setup.py -a -f kle2svg.py ]; then
    echo 'You must run this in the top level of kle2svg!'
    exit 1
elif [ -d .kle2svg-$PYTHON_VERSION -a "$1" != "-f" ]; then
    echo 'Not replacing existing virtualenv. Use -f to override.'
    exit 1
elif ! virtualenv --version 2>&1 > /dev/null; then
    echo "You must install virtualenv first!"
    echo
    echo "Try: sudo easy_install virtualenv"
    exit 1
elif [ -n "$VIRTUAL_ENV" ]; then
    echo "You must 'deactivate' your current virtualenv before running this!"
    exit 1
fi

# If necessary, wipe away the old virtualenv
if [ -d .kle2svg-$PYTHON_VERSION ]; then
    while true; do
        echo "About to remove the existing virtualenv. OK to proceed?"
        read answer

        case $answer in
            yes|YES)
                rm -rf .kle2svg-$PYTHON_VERSION activate-$PYTHON_VERSION
                break
                ;;
            no|NO)
                echo "Can't proceed while existing virtualenv is in the way."
                exit 1
                ;;
            *)
                echo 'Please answer "yes" or "no".'
                ;;
        esac
    done
fi

# Create the new virtualenv
virtualenv -p python$PYTHON_VERSION .kle2svg-$PYTHON_VERSION || exit
ln -s .kle2svg-$PYTHON_VERSION/bin/activate activate-$PYTHON_VERSION || exit

# Setup the environment
source activate-$PYTHON_VERSION || exit
pip install -r requirements.txt || exit

# If they also have kle2xy checked out use that locally
if [ -d ../kle2xy ]; then
    pip uninstall kle2xy
    pip install -e ../kle2xy || exit
fi

python setup.py develop || exit

cat << EOF
===============================================================================


Congratulations! VirtualEnv setup was completed successfully!

To get started activate your virtualenv:

    $ source $PWD/activate-$PYTHON_VERSION

EOF
