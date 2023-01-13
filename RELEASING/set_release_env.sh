#!/bin/bash

usage() {
    echo "usage (BASH): . set_release_env.sh <GITORADE_RC_VERSION> <PGP_KEY_FULLNAME>"
    echo "usage (ZSH): source set_release_env.sh <GITORADE_RC_VERSION> <PGP_KEY_FULLNAME>"
    echo
    echo "example: source set_release_env.sh 0.37.0rc1 myid@gmail.com"
}

if [ -z "$1" ] || [ -z "$2" ]; then
    usage
else
    if [[ ${1} =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)rc([0-9]+)$ ]]; then
        if [ -n "$ZSH_VERSION" ]; then
            VERSION_MAJOR="${match[1]}"
            VERSION_MINOR="${match[2]}"
            VERSION_PATCH="${match[3]}"
            VERSION_RC="${match[4]}"
        elif [ -n "$BASH_VERSION" ]; then
            VERSION_MAJOR="${BASH_REMATCH[1]}"
            VERSION_MINOR="${BASH_REMATCH[2]}"
            VERSION_PATCH="${BASH_REMATCH[3]}"
            VERSION_RC="${BASH_REMATCH[4]}"
        else
            echo "Unsupported shell type, only zsh and bash supported"
            exit 1
        fi

    else
        echo "unable to parse version string ${1}. Example of valid version string: 0.35.2rc1"
        exit 1
    fi
    export GITORADE_VERSION="${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}"
    export GITORADE_RC="${VERSION_RC}"
    export GITORADE_GITHUB_BRANCH="${VERSION_MAJOR}.${VERSION_MINOR}"
    export GITORADE_PGP_FULLNAME="${2}"
    export GITORADE_VERSION_RC="${GITORADE_VERSION}rc${VERSION_RC}"
    export GITORADE_RELEASE=gitorade-"${GITORADE_VERSION}"
    export GITORADE_RELEASE_RC=gitorade-"${GITORADE_VERSION_RC}"
    export GITORADE_RELEASE_TARBALL="${GITORADE_RELEASE}"-source.tar.gz
    export GITORADE_RELEASE_RC_TARBALL="${GITORADE_RELEASE_RC}"-source.tar.gz
    export GITORADE_TMP_ASF_SITE_PATH="/tmp/incubator-gitorade-site-${GITORADE_VERSION}"

    echo -------------------------------
    echo Set Release env variables
    env | grep ^GITORADE_
    echo -------------------------------
fi
