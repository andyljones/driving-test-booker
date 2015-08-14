#!/usr/bin/env bash
source $HOME/.profile
cd "${0%/*}"
source activate test-scraper
python scratch.py
source deactivate
