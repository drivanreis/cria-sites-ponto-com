@echo off
cd ..
cd ..
echo Criando ambiente virtual em .venv...
python -m venv .venv

echo Ativando ambiente virtual...
call .venv\Scripts\activate

echo Instalando dependências...
pip install -r ..\requirements.txt

echo Ambiente configurado com sucesso!
pause
exit /b 0