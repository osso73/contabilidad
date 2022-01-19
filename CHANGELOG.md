# Contabilidad changelog

Los cambios realizados en este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). Para los números de versión, utilizo únicamente 2 dígitos para los cambios mayores y menores.


## Nueva versión en curso, no publicada

### Añadido
- Documentación sobre el proyecto, según iss. #19.
- Popup para indicar errores (iss. #15).
- Ordenar las tablas pinchando en el título de la columna (iss. #16).
- Paginación en asientos y cuentas (iss. #11).
- Nueva pestaña de informes, con capacidad para generar informes de una cuenta o grupo de cuentas (iss #5).
- Campo etiqueta en las cuentas, para poder generar los informes.

### Cambiado
- Creación de cuentas, y filtro de cuentas, se puede también añadir etiquetas.


## v0.5 -  2021-12-29
Funcionalidad básica establecida:

- añadir y borrar cuentas y asientos (movimientos),
- cargar ficheros de cuentas y de movimientos
- filtrar cuentas y movimientos

Incluye los tests para comprobar estas funciones.


### Añadido
- Posibilidad de cargar las cuentas a partir de un fichero excel (iss. #2).
- Posibilidad de cargar movimientos simples y complejos a partir de una plantilla excel (iss. #3)
- Formularios para filtrar cuentas y asientos (iss. #6)

### Cambiado
- Menú lateral reemplazado por tabuladores. Varios cambios en el diseño (colores, tamaños, etc.)
- Impide borrar una cuenta con movimientos asociados

----

## v0.1 -  2021-12-08

Versión inicial. Funcionalidad básica: crear y borrar cuentas y asientos de forma manual, y modificación de los datos ya existentes.


### Añadido
- Modelos de datos para Cuenta y Asiento
- Vistas para ver, modificar y borrar los asientos y las cuentas
- Plantilla html basada en Bulma, y menús de navegación
- Tests unitarios
