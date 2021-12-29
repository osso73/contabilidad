# Instalación

Esta es una aplicación web, desarrollada utilizando el framewrok de [Django](https://docs.djangoproject.com). Por tanto, para ejecutarla necesitas ponerla en un servidor web. En la documentación de Django, en el apartado de [Deployment](https://docs.djangoproject.com/en/4.0/howto/deployment/) podrás encontrar más detalles sobre cómo hacerlo.

En cualquier caso, puedes ver la aplicación utilizando el servidor web de Django. Como explica la documentación, este servidor es solo para hacer pruebas durante el desarrollo de la aplicación, no es apto para una puesta en producción.

Los pasos para instalar y ejecutar esta aplicación son los siguientes:

1. Clonar el repositorio en un directorio de tu equipo

```bash
git clone  https://github.com/osso73/contabilidad.git
```

2. Crear un entorno virtual, por ejemplo, utilizando el módulo `venv` de python.

```bash
python -m venv .env
.env\Scripts\activate.bat  # para un entorno de windows
source .env/bin/activate   # para un entorno linux
python -m pip install --upgrade pip
```


3. Instalar los paquetes necesarios. Estos están detallados en el fichero `requirements.txt`.

```bash
python -m pip install -r requirements.txt
```

4. Actualizar la base de datos. El fichero de la base de datos no está en el repositorio, por lo que se tiene crear a partir de las migraciones:

```bash
cd conta
python manage.py migrate
```

5. Lanzar la aplicación con el servidor web de Django, utilizando el comando `runserver`.

```bash
python manage.py runserver
```

Ahora puedes acceder a la aplicación en la dirección: http://127.0.0.1:8000.
