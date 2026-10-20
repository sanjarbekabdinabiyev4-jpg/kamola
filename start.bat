@echo off
title AlgoPlay Veb Ilovasi
echo ========================================================
echo          ALGORITHMS & CODING GAMIFIED (ALGOPLAY)
echo ========================================================
echo Sayt ishga tushirilmoqda...
echo Brauzerda oching: http://127.0.0.1:5050
echo Admin kirish: http://127.0.0.1:5050/admin/login
echo Login: admin  ^|  Parol: admin777
echo ========================================================
py app.py 2>nul || python app.py
pause
