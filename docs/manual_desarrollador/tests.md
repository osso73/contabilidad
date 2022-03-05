# Tests

## Paquetes utilizados y estructura

Para hacer los tests del entorno, utilizo el framework de pytest, y la librería [WebTest](https://docs.pylonsproject.org/projects/webtest) para hacer tests que utilizan formularios, lo cual me permite validar las funciones post, y alguna función más avanzada que las del entorno test de django. También utlizo el programa [Coverage](https://coverage.readthedocs.io/), para identificar la cobertura de los tests.

Los tests están organizados en 3 carpetas, para agruparlos:

- _models_: contiene los tests para validar los modelos de datos creados
- _views_: contiene los tests para validar las views. A través de las views se testean todas las demás funciones de procesado de datos, también las incluidas en `functions.py`.
- _functions_: contiene los tests unitarios para las funciones del fichero `functions.py`. Aunque ya está parcialmente testeado a través de las views, es interesante tener tests unitarios para cada función, para poder detectar posibles problemas.

Dentro de cada carpeta he creado un fichero para cada función o clase (sea vista, modelo o función). La única excepción es en la carpeta functions, donde he agrupado las funciones por funcionalidad, ya que de esta forma puedo utilizar los mismos fixtures.

Las `fixtures` que aplican a varios tests las defino dentro de cada carpeta, aunque estoy pensando en consolidarlas todas en un único fichero para todos los tests. Las `fixtures` que son muy específicas de una función o clase, las defino dentro de su clase.

Hay una clase para cada vista, y una clase para cada modelo, y una clase para cada función. Dentro de la clase se hacen todos los tests relacionados con la vista, modelo o función.


## Configuración

La configuración de `coverage` está en el fichero `conta/.coverage.rc`. Ahí están los parámetros utilizados. Lo más importante es identificar los ficheros a excluir, para poder obtener una cobertura del 100% de nuestro código, dejando fuera los ficheros de configuración y otros estándares de django.

La configuración de `pytest` está en el fichero `conta/pytest.ini`. El fichero da los parámetros a utilizar para el comando pytest, y define el fichero de configuración a utilizar. Puedes apuntar al fichero estándar, pero para agilizar los tests es mejor crear una configuración de test con la base de datos en memoria, en lugar de la base de datos en disco.

El siguiente fichero importante es el de la configuración (settings) para los tests, en la misma carpeta que el fichero estándar, `conta/settings_test.py`.


## Ejecución

Para ejecutar los tests, ir al directorio del programa de django y ejecutar `pytest`:

```bash
cd /conta
pytest
```

Esto permite luego obtener un informe de la cobertura en formato html en la carpeta `conta/htmlcov`, con un fichero `conta/htmlcov/index.html` que contiene información detallada de qué líneas de código no han sido testeadas. De esta forma nos aseguramos de testear todos los casos, funciones, y ramas de nuestro programa.

Para ejecutar solo algunos tests, hay que utilizar la opción `-k` de pyest, con una cadena o patrón. En ese caso, sólo se ejecutarán los tests que tengan la cadena en su nombre. Ojo, eso incluye también la carpeta y el nombre de archivo. Se pueden usar operadores and y or, así:

```bash
cd /conta
pytest -k "test_cargar_cuentas and TestExtraerCuenta"
```
