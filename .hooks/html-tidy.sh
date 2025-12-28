#!/bin/bash

set -u
dir=$(dirname "$0")

tidy -config "$dir/html-tidy.conf" "$@"
status=$?

# Only exit nonzero if there were errors
if [[ $status -gt 1 ]]; then
    exit $status
fi
