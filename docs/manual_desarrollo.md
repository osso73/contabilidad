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


# Tests

Para hacer los tests del entorno, he seguido el paquete proporcionado por django, basado en Unittest. Además utilizo la librería [WebTest](https://docs.pylonsproject.org/projects/webtest) para hacer tests que utilizan formularios, lo cual me permite validar las funciones post, y alguna función más avanzada que las del entorno test de django.

De momento tengo los tests organizados en dos ficheros:
- `test_models.py`: contiene los tests para validar los modelos de datos creados
- `test_views.py`: contiene los tests para validar las views. A través de las views se testean todas las demás funciones de procesado de datos, también las incluidas en `functions.py`.

Hay una clase para cada vista, y una clase para cada modelo. Dentro de la clase se hacen todos los tests relacionados con la vista o modelo.

También utlizo el programa [Coverage](https://coverage.readthedocs.io/), para identificar la cobertura de los tests. La configuración de `coverage` está en el fichero `.coverage.rc`. Gracias a esta configuración, se pueden ejecutar los tests simplemente con el comando:

```bash
coverage run
```

Esto permite luego obtener un informe de la cobertura, ejecutando los siguientes comandos:

```bash
coverage report   # para un informe en la consola
coverage html     # genera un informe detallado en html
```

El segundo comando crea una carpeta `htmlcov`, con un fichero `htmlcov/index.html` que contiene información detallada de qué líneas de código no han sido testeadas. De esta forma nos aseguramos de testear todos los casos, funciones, y ramas de nuestro programa.
