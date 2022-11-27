#!/bin/bash

APP=./src/photologue/main.py

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

  echo 'Fetching Paths'
  PATHS=$(pipenv run python ./config.py paths)

  # echo 'Fetching extentions'
  # EXTENTIONS=$(pipenv run python ./config.py extentions)

  # check we have the values we need
  if [[ -z "$PATHS" ]]
  then
    echo "No PATHS"
    exit 1
  # elif [[ -z "$EXTENTIONS" ]]
  # then
  #   echo "No EXTENTIONS"
  #   exit 1
  fi

  for p in $PATHS
  do
    START=$(date +%s)
    echo "Finding images in ${p}"

    find ${p} -name "*.PEF" -o -name "*.jpg" -o -name "*.JPG" -o -name "*.jpeg" -o -name "*.DNG" -o -name "*.RW2" \
    | pipenv run python ./main.py collect files

    END=$(date +%s)
    elapsed $START $END
  done
}


# Grab file stat
collect_stats() {
  echo "Collecting stats..."
  START=$(date +%s)
  
  pipenv run python ${APP} missing stats --print0 \
  | xargs -0 stat -f "%z%t%B%t%c%t%m%t%a%t%N" \
  | pipenv run python ${APP} collect stats

  END=$(date +%s)
  elapsed $START $END
}


# Grab exif info
collect_exif() {
  echo "Collecting exifs..."
  START=$(date +%s)

  pipenv run python ${APP} missing exifs \
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
  | pipenv run python ${APP} collect exifs

  END=$(date +%s)
  elapsed $START $END
}


# Grab Checksums
collect_checksums() {
  echo "Collecting checksums..."
  START=$(date +%s)

  pipenv run python ${APP} missing checksums --print0 \
  | xargs -0 cksum \
  | pipenv run python ${APP} collect checksums

  END=$(date +%s)
  elapsed $START $END
}


command_collect() {
  collect_stats
  collect_exif
  collect_checksums
}


command_rules(){
  echo "Processing Rules..."
  START=$(date +%s)

  pipenv run python ./src/photologue/main.py rules

  END=$(date +%s)
  elapsed $START $END
}

profile_rules(){
  file_profiled=profiling/profile.dat
  pipenv run python -m cProfile -o ${file_profiled} ./main.py rules
  snakeviz ${file_profiled}
}


cleanup_logs() {
  find ./logs -name "*.log" -delete
}


command_cleanup  () {
  cleanup_logs
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


main_help() {
  echo "run.sh <COMMAND>"
  echo ""
  echo "COMMAND"
  echo $'\tcollect'
  echo $'\tprocess'
  echo $'\tlint'
  echo $'\ttest'
  echo $'\tcleanup'
}


main() {
  COMMAND=$1

  if [[ $COMMAND == "collect" ]]
  then
    command_collect
  
  elif [[ $COMMAND == "process" ]]
  then
    command_rules

  elif [[ $COMMAND == "lint" ]]
  then
    command_lint
  
  elif [[ $COMMAND == "test" ]]
  then
    command_test

  elif [[ $COMMAND == "cleanup" ]]
  then
    command_cleanup

  else
    main_help
  fi

}


COMMAND=$1
if [[ ! -z "$COMMAND" ]]
then
  main $COMMAND
else
  main_help
fi

