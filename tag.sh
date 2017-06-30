#!/bin/bash
if [ "$TRAVIS_BRANCH" == "master" ]; then
    CURR_VERSION=$(cat VERSION)
    git config --global user.email "builds@travis-ci.com"
    git config --global user.name "Travis CI"
    git tag "$CURR_VERSION"
    git push --tags --quiet "https://${GH_TOKEN}@github.com/piratar/wasa2il.git"
fi