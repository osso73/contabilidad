# Estructura del repositorio

Este repositorio tiene la siguiente estructura:

```
git
 ├──analysis
 ├──conta
 │    ├──conta
 │    └──main
 └──docs
```

- `analysis`: contiene algunos archivos utilizados para pruebas, o análisis de plantillas y formatos. También un notebook de Jupyter donde pruebo algunas funciones antes de implementarlas en el programa.
- `conta`: es la carpeta con toda la estructura de django. Dentro de ella tenemos dos carpetas principales:
  - `conta`: contiene la configuración global del sitio web
  - `main`: es una aplicación dentro de django, que es la que contiene realmente toda la aplicación.
- `docs`: toda la documentación, estructurada en ficheros .md, para generar las páginas de ayuda mediante `mkdocs`.

La estructura de directorios es la propia de un proyecto django. Ver la documentación de django para más información. Además de la estructura por defecto, he creado algún fichero o carpeta nueva:

- `tests`: en esta carpeta están todos los ficheros de tests. Incluye también una subcarpeta con ficheros que se utilizan para hacer los tests, para subir plantillas y ficheros de cuentas (con o sin errores).
- `functions.py`: este fichero contiene funciones para el procesado de datos, adicionales a las funciones dentro del fichero de `views.py`.
