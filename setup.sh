echo 'Installing ExifTool'
brew install ExifTool sqlite

echo 'Installing python requirements'
pipenv run pip install --requirement requirements.txt #> /dev/null

