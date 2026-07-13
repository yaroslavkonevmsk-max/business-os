@echo off
:: Business OS - One-Click Launcher
:: This file automatically runs the smart PowerShell launcher
:: Just double-click this file!

cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "start.ps1"
