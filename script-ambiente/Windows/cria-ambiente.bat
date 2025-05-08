@echo off
REM Script para criar e ativar um ambiente virtual Python no Windows
REM EXECUTE ESSE SCRIPT NO CMD, NÃO NO POWERSHELL!
echo EXECUTE ESSE SCRIPT NO CMD, NÃO NO POWERSHELL!

cd ..
cd ..
echo Criando ambiente virtual em .venv...
python -m venv .venv

echo Ativando ambiente virtual...
.venv\Scripts\activate
if errorlevel 1 (
    echo Falha ao ativar o ambiente virtual.
    exit /b 1
)
echo Ambiente virtual ativado com sucesso!

echo Instalando dependências...
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
code .


echo Ambiente configurado com sucesso!
pause
exit /b 0