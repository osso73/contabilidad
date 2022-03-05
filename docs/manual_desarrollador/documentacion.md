
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
