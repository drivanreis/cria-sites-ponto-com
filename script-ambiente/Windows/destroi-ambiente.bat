@echo off
REM Script para destruir o ambiente virtual no Windows.
REM Se o ambiente virtual estiver ativo, ele será desativado antes de ser removido.
REM EXECUTE ESSE SCRIPT NO CMD, NÃO NO POWERSHELL!

echo Verificando se o ambiente virtual está ativo...
if defined VIRTUAL_ENV (
    echo Ambiente virtual detectado em %VIRTUAL_ENV%.
    echo Desativando o ambiente virtual...
    call deactivate
    REM Após desativar, as variáveis associadas deverão ser limpas.
) else (
    echo O ambiente virtual não está ativo.
)

echo Navegando para a raiz do projeto...
REM Supondo que este script esteja em script-ambiente\Windows, voltamos dois níveis:
cd ..\..
echo Diretório atual: %CD%

echo Destruindo ambiente virtual...
rmdir /S /Q ".venv"
if %errorlevel% neq 0 (
    echo Erro ao tentar deletar o ambiente virtual.
    exit /b %errorlevel%
)
echo Ambiente virtual removido com sucesso!
pause
exit /b 0
