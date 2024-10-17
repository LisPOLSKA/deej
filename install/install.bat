@echo off
copy mixer.exe "%appdata%\Microsoft\Windows\Start Menu\Programs\Startup"
xcopy assets "%UserProfile%\deej\assets" /E /H /C /I /Y
copy deej.exe %UserProfile%\deej
copy config.yaml %UserProfile%\deej
start /d "%appdata%\Microsoft\Windows\Start Menu\Programs\Startup" mixer.exe