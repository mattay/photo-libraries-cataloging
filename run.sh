#!/bin/bash

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
  
  pipenv run python ./main.py missing stats --print0 \
  | xargs -0 stat -f "%z%t%B%t%c%t%m%t%a%t%N" \
  | pipenv run python ./main.py collect stats

  END=$(date +%s)
  elapsed $START $END
}


# Grab exif info
collect_exif() {
  echo "Collecting exifs..."
  START=$(date +%s)

  pipenv run python ./main.py missing exifs \
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
  | pipenv run python ./main.py collect exifs

  END=$(date +%s)
  elapsed $START $END
}


# Grab Checksums
collect_checksums() {
  echo "Collecting checksums..."
  START=$(date +%s)

  pipenv run python ./main.py missing checksums --print0 \
  | xargs -0 cksum \
  | pipenv run python ./main.py collect checksums

  END=$(date +%s)
  elapsed $START $END
}


collect() {
  collect_stats
  collect_exif
  collect_checksums
}


rules(){
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

# find_in_paths
# collect
rules
# profile_rules

# -exec stat {} +


# --- Find Files ---
# pipenv run python ./main.py search --filesearch
# --- Collect File stats and Library information ---
# pipenv run python ./main.py search --collectstats
# pipenv run python ./main.py --version
# pipenv run python ./main.py copies
# pipenv run python ./main.py duplicates
# pipenv run python ./main.py libraries
# Output a list of mappings for use in observable.
# pipenv run python ./main.py mappings
# pipenv run python ./main.py clean --thumbnails
# cat info.log
