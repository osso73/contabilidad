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

## Paquetes utilizados y estructura

Para hacer los tests del entorno, utilizo el framework de pytest, y la librería [WebTest](https://docs.pylonsproject.org/projects/webtest) para hacer tests que utilizan formularios, lo cual me permite validar las funciones post, y alguna función más avanzada que las del entorno test de django. También utlizo el programa [Coverage](https://coverage.readthedocs.io/), para identificar la cobertura de los tests.

De momento tengo los tests organizados en dos ficheros:
- `test_models.py`: contiene los tests para validar los modelos de datos creados
- `test_views.py`: contiene los tests para validar las views. A través de las views se testean todas las demás funciones de procesado de datos, también las incluidas en `functions.py`.

Hay una clase para cada vista, y una clase para cada modelo. Dentro de la clase se hacen todos los tests relacionados con la vista o modelo.

## Configuración

La configuración de `coverage` está en el fichero `conta/.coverage.rc`. Ahí están los parámetros utilizados. Lo más importante es identificar los ficheros a excluir, para poder obtener una cobertura del 100% de nuestro código, dejando fuera los ficheros de configuración y otros estándares de django.

La configuración de `pytest` está en el fichero `conta/pytest.ini`. El fichero da los parámetros a utilizar para el comando pytest, y define el fichero de configuración a utilizar. Puedes apuntar al fichero estándar, pero para agilizar los tests es mejor crear una configuración de test con la base de datos en memoria, en lugar de la base de datos en disco.

El siguiente fichero importante es el de la configuración (settings) para los tests, en la misma carpeta que el fichero estándar, `conta/settings_test.py`.


## Ejecución

se pueden ejecutar los tests simplemente con el comando:
```bash
pytest
```

Esto permite luego obtener un informe de la cobertura en formato html en la carpeta `conta/htmlcov`, con un fichero `conta/htmlcov/index.html` que contiene información detallada de qué líneas de código no han sido testeadas. De esta forma nos aseguramos de testear todos los casos, funciones, y ramas de nuestro programa.


# Documentación

La documentación la he creado con el paquete [MkDocs](https://www.mkdocs.org/). Toda la documentación está dentro de la carpeta docs, y el fichero de configuración está en el directorio raíz: `mkdocs.yml`. Para cambiar la documentación en tu repositorio, recuerda actualizar este fichero para que apunte a tu repositorio.

Modifica, añade o quita la documentación que necesites. Antes de subir los cambios, puedes ver cómo queda ejecutando el siguiente comando desde el directorio raíz:

```bash
mkdocs serve
```

Y puedes ver la documentación en: https://127.0.0.1:8000

Una vez validada la documentación, la puedes subir automáticamente a tu repositorio con el comando:

```bash
mkdocs build
mkdocs gh-deploy
```

Esto creará las páginas web a partir de los documentos markdown del directorio docs, y utilizará el comando git para subir esta documentación a github, como una rama dentro de tu repositorio, para que esté disponible.
