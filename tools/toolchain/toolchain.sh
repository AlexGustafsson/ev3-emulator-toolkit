#!/usr/bin/env bash

# This script wraps the shell inside of a container so that the user does not have to
# mount files etc.

declare -a mounts
declare -a arguments
for (( i=1; i <= "$#"; i++ )); do
  path="$(realpath ${!i} 2>/dev/null)"
  if [[ -f "$path" ]]; then
    mounts+=("--mount type=bind,source=$path,target=/var/data/$i")
    # Replace the given path to its argument number instead,
    # that way we can easily reference it on another system
    arguments+=("/var/data/$i")
  else
    arguments+=("${!i}")
  fi
done

docker run --rm -it ${mounts[*]} ev3-emulator-toolkit/firmware "${arguments[*]}"
