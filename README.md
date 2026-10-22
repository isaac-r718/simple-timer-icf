# ICF Timer

Temporizador de escritorio en Python y Tkinter. Tiene una portada con el logo,
una pantalla para elegir la duración y una pantalla de ejecución con cuenta
regresiva, pausa, reinicio y tiempo extra.

## Requisitos

- Python 3.10 o posterior.
- Tkinter, incluido con la mayoría de las instalaciones de Python para Windows.

## Ejecutar

Desde esta carpeta, ejecuta:

```powershell
python Timer.py
```

El programa usa `assets/ICF.png` para mostrar el logo. Si el archivo no está,
la portada muestra un botón de texto en su lugar. El logo no se distribuye en
este repositorio: solo debes añadirlo si tienes autorización para usarlo.

## Uso

1. Haz clic en el logo para entrar al menú.
2. Ajusta la duración con los botones `+` y `-`. Los aumentos aparecen en la
   fila superior y las reducciones en la inferior.
3. Pulsa **Iniciar timer**.
4. En la pantalla del timer, usa **Pausar**, **Reiniciar** o **Finalizar**.
   También puedes sumar o restar un minuto mientras está activo.
5. Al llegar a cero, el tiempo extra aparece parpadeando en rojo encima del
   contador principal. Si añades tiempo durante el tiempo extra, el contador
   principal lo cuenta y el tiempo extra continúa visible.

Atajos: **Espacio** pausa o continúa el timer; **F11** alterna pantalla
completa y **Esc** sale de pantalla completa.

## Licencia

El código de `Timer.py` se distribuye bajo la licencia MIT; consulta
[LICENSE](./LICENSE). El logo `assets/ICF.png`, los nombres y las marcas de ICF
no están incluidos en esa licencia y conservan sus derechos correspondientes.
