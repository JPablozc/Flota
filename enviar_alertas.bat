@echo off

REM Activar el entorno virtual
call C:\Users\JuanPabloZapataChava\Flota\venv\Scripts\activate

REM Ir al proyecto
cd C:\Users\JuanPabloZapataChava\Flota

REM Ejecutar el comando
python manage.py enviar_alertas_documentos --dias 30

REM Desactivar el entorno virtual
deactivate
