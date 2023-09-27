#!/bin/bash

# Globals
APP_MAIN=./src/photologue/main.py
APP_CONFIG=./src/photologue/config.py

# Monitor the time it takes for a command to run.
elapsed () {
  start=$1
  end=$2

  elapsedTime=$((end-start))
  hours=$((${elapsedTime}/3600))
  min=$((${elapsedTime}/60))
  sec=$((${elapsedTime}%60))

  if [ "$elapsedTime" -le 60 ]; then
      timer_show="${elapsedTime} s."

  elif [ "$elapsedTime" -gt 60 ] && [ "$elapsedTime" -le 180 ]; then
      timer_show="${min} min. ${sec} s."

  else
      if [ "$hours" -gt 0 ]; then
          min=$((${min}%60))
          timer_show="${hours} h. ${min} min. ${sec} s."
      else
          timer_show="${min} min. ${sec} s."
      fi
  fi

  printf "Completed in ${timer_show}\n\n"
}

find_extentions () {
  local find_name=""
  local first=1
  local IFS=$'\n'

  for e in $EXTENTIONS
  do
    if [[ $first -eq 1 ]]
    then
      first=0
      find_name="-name \"*$e\""
    else
      find_name="$find_name -o -name \"*$e\""
    fi
  done

  find_name="$find_name"

  echo $find_name
}

# Determin file library status
# Filter out proxy files
find_in_paths() {
  local IFS=$'\n'

  # Fetching Paths
  PATHS=$(yq eval '.import.volumes.[].[]' "$APP_CONFIG")

  # Fetching extentions
  EXTENTIONS=$(yq eval '.import.extentions[]' "$APP_CONFIG")

  # check we have the values we need
  if [[ -z "$PATHS" ]]
  then
    echo "No paths have been definded under import > volumes in $APP_CONFIG"
    exit 1
  elif [[ -z "$EXTENTIONS" ]]
  then
    echo "No file extentions have been defined under import > extentions $APP_CONFIG"
    exit 1
  fi

  for p in $PATHS
  do
    START=$(date +%s)
    echo "Finding images in ${p}"

    expression=$(printf " -name '*%s' -o" $EXTENTIONS | sed 's/-o$//')

    find "${p}" -type f "${expression}" \
    | pipenv run python ${APP_MAIN} collect files

    END=$(date +%s)
    elapsed $START $END
  done
}


# # #
# #     Profiling
#
profile_find_in_paths(){
  local IFS=$'\n'

  file_profiled=profiling/profile_find_in_paths.dat
  p="/Volumes/Padawan/_Pictures/Aperture Library Collections"
  echo "Finding images in ${p}"

  find ${p} -name "*.PEF" -o -name "*.jpg" -o -name "*.JPG" -o -name "*.jpeg" -o -name "*.DNG" -o -name "*.RW2" \
  | pipenv run python -m cProfile -o ${file_profiled} ${APP_MAIN} collect files

  snakeviz ${file_profiled}
}


# # #
# #     Collecting
#

# Grab file stat
collect_stats() {
  echo "Collecting stats..."
  START=$(date +%s)

  pipenv run python ${APP_MAIN} missing stats --print0 \
  | xargs -0 stat -f "%z%t%B%t%c%t%m%t%a%t%N" \
  | pipenv run python ${APP_MAIN} collect stats

  END=$(date +%s)
  elapsed $START $END
}

# Grab exif info
collect_exif() {
  echo "Collecting exifs..."
  START=$(date +%s)

  pipenv run python ${APP_MAIN} missing exifs \
  | exiftool -@ - -T \
  -DateTimeOriginal \
  -FileModifyDate \
  -Make\
  -Model \
  -ColorSpace \
  -XResolution \
  -YResolution \
  -ResolutionUnit \
  -Quality \
  -ImageHeight \
  -ImageWidth \
  -Software \
  -filepath \
  | pipenv run python ${APP_MAIN} collect exifs

  END=$(date +%s)
  elapsed $START $END
}

# Grab Checksums
collect_checksums() {
  echo "Collecting checksums..."
  START=$(date +%s)

  pipenv run python ${APP_MAIN} missing checksums --print0 \
  | xargs -0 cksum \
  | pipenv run python ${APP_MAIN} collect checksums

  END=$(date +%s)
  elapsed $START $END
}

#  Delete log files
clear_logs() {
  find ./logs -name "*.log" -delete
}


# # #
# #     Commands
#

command_collect() {
  find_in_paths
  collect_stats
  collect_exif
  collect_checksums
}

command_process(){
  echo "Processing Camera Images..."
  START=$(date +%s)

  pipenv run python ${APP_MAIN} process

  END=$(date +%s)
  elapsed $START $END
}

command_clear_logs  () {
  clear_logs
}

command_lint() {
  SRC=src

  echo "mypy"
  pipenv run mypy ${SRC}

  echo "flake8"
  pipenv run flake8 ${SRC}
}

command_test() {
  echo "pytest"
  pipenv run pytest
}

command_profile() {
  echo "Profiling"
  profile_find_in_paths
}

command_cleanup() {
  echo "Cleanup"
  pipenv run python ${APP_MAIN} cleanup
}

command_summary() {
  echo "Sumamry"
  pipenv run python ${APP_MAIN} summary
}


# # #
# #     Main
#

main_help() {
  echo "run.sh <COMMAND>"
  echo ""
  echo "COMMAND"
  echo $'\tcleanup'
  echo $'\tclearlogs'
  echo $'\tcollect'
  echo $'\tlint'
  echo $'\tprocess'
  echo $'\tsummary'
  echo $'\ttest'
}

main() {
  COMMAND=$1

  # Check config file is avaliable
  if [[ ! -f "$APP_CONFIG" ]]; then
    echo "YAML file not found: $APP_CONFIG"
    return 1
  fi

  if [[ $COMMAND == "collect" ]]
  then
    command_collect

  elif [[ $COMMAND == "process" ]]
  then
    command_process

  elif [[ $COMMAND == "lint" ]]
  then
    command_lint

  elif [[ $COMMAND == "test" ]]
  then
    command_test

  elif [[ $COMMAND == "clearlogs" ]]
  then
    command_clear_logs

  elif [[ $COMMAND == "profile" ]]
  then
    command_profile

  elif [[ $COMMAND == "summary" ]]
  then
    command_summary

  elif [[ $COMMAND == "cleanup" ]]
  then
    command_cleanup

  else
    main_help
  fi

}


# # #
# #     => Starts here <=
#
COMMAND=$1

mkdir -p log

if [[ ! -z "$COMMAND" ]]
then
  main $COMMAND
else
  main_help
fi
