#!/bin/bash

cd "$(dirname "$0")"

rm -f athene-cli-browser-ext.zip
zip -r athene-cli-browser-ext.zip manifest.json *.js
