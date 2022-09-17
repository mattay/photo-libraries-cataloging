echo 'Installing ExifTool'
brew install ExifTool

echo 'Installing python requirements'
pipenv run pip install --requirement requirements.txt #> /dev/null

