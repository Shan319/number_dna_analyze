@echo off

@REM install requirements
py -m pip install --upgrade pip
py -m pip install -r requirements.txt

@REM launch the app
py main.py