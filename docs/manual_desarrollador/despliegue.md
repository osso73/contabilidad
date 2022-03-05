# Despliegue en producción

Tal como dice la [documentacion](https://docs.djangoproject.com/en/4.0/howto/deployment/) de Dango, el servidor incluido como parte de Django nos sirve para ir haciendo las pruebas y ver cómo queda la aplicación según la vamos desarrollando, pero para utilizarlo en un entorno de producción, es decir para su uso habitual, es recomendable utilizar un servidor web como apache o nginx, que son mucho más robustos y seguros. Como explican en Django, existen varias opciones para hacer el despliegue. Aquí voy a explicar cómo lo he hecho, utilizando un servidor nginx como servidor web, y Gunicorn como servidor WSGI, instalado sobre un jail en FreeBSD. Para este proyecto utilizo la base de datos por defecto sqlite, pero también se puede utilizar una base de datos más robusta, mariadb por ejemplo. Voy a incluir un capítulo al final explicando cómo hacer el despliegue utilizando una base de datos mariadb.

Veremos no sólo los paquetes de software que hay que desplegar y configurar en el servidor (en el jail), sino también las adaptaciones que tenemos que hacer en nuestra configuración. Estas modificaciones ya están hechas en la versión que hay en github, pero tendrás que adaptarlos en función del despliegue que vayas a hacer.


## Configuración inicial de paquetes

Una vez creado el jail, actualizamos la configuración, y creamos un directorio donde vamos a desplegar nuestros(s) proyecto(s) de django:

```bash
pkg update
mkdir -p /home/django/projects
```

Esta carpeta será donde copiaremos nuestro proyecto. Yo utilizo el mismo servidor para desplegar varias aplicaciones django, por eso tengo la carpeta "projects", dentro de la cual crearé mi carpeta de "contabilidad". Si solo lo utilizas para este proyecto, puedes poner la "contabilidad" directamente en la carpeta de django. Para copiar los ficheros a esta carpeta utiliza el método que consideres más adecuado. En mi caso, monto un sistema de ficheros en la carpeta "projects", y ese sistema lo puedo acceder desde mis máquinas linux o windows para copiar ficheros en él.

Ahora instalamos los paquetes que necesitamos. Estos son python, junto con pip, nginx y sqlite para la base de datos. Django y Gunicorn son paquetes de python que instalaremos dentro del servidor virtual que crearemos para nuestro proyecto. De esta forma podemos tener varios proyectos django en el mismo servidor.

```bash
pkg install -y python nginx
python -m ensurepip
pip3 install --upgrade pip
pkg install -y sqlite3 py38-sqlite3
```

Atención a que el paquete de sqlite corresponda a la versión de python instalada en el sistema; en nuestro caso, la 3.8.


## Creación y configuración de usuario

Vamos a crear un usuario django que será el que ejecute el servidor. De esta forma no tenemos que utilizar el usuario root, y es más seguro.

Creamos el grupo y el usuario, y le asignamos la carpeta que hemos creado antes:

```bash
pw groupadd django -g 1000
pw useradd django -u 1000 -g django -s /bin/sh -c "django project" -d /home/django
chown -R django:django /home/django
```


## Ficheros django y configuración

Ahora copiamos los ficheros de nuestro proyecto a la carpeta que hemos creado antes, con el método que decidas. Solo hay que copiar la carpeta `conta` dentro de nuestro proyecto, que es la que contiene el proyecto django. Además el fichero `requirements.txtx` para poder crear el entorno virtual. Puedes copiarlo en la carpeta de `conta`.

A continuación hay que hacer algunos ajustes.


### Creación del entorno virtual

Primero creamos el entorno virtual:

```
cd /home/django/projects/conta
python -m venv .venv
```

Ahora activamos en entorno, e instalamos los paquetes, tanto los necesarios para el proyecto, como el gunicorn:

```bash
source .venv/bin/activate.csh
pip install -r requirements.txt
pip install gunicorn
```

### Ficheros estáticos

Los ficheros estáticos serán servidos directamente por nuestro servidor nginx, ya que gunicorn solo va a servir las páginas dinámicas. Por esta razón tenemos que hacer ajustar la configuración de django, añadiendo esta línea:

```python
STATIC_ROOT = BASE_DIR / 'static'
STATIC_URL = '/static/'
```

Esta configuración ya está en el repositorio de django, por lo que no hace falta añadirlo. Después hay ejecutar este comando desde la carpeta de nuestro proyecto:

```bash
python manage.py collectstatic
```

Este comando recoge todos los ficheros estáticos de nuestro proyecto, y los agrupa en una carpeta `static` dentro de nuestro proyecto. De esta forma podremos configurar nginx para servir estos ficheros.

Atención: si más adelante haces cambios en tu proyecto tendrás que correr este comando otra vez, para actualizar los ficheros estáticos.


### Settings de producción

En un entorno de producción hay que cambiar alguna configuración para que el entorno sea más seguro, según las [recomendaciones](https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/) de django. Para no tener que estar cambiando estas configuraciones cada vez que copio los ficheros al entorno productivo, lo que hago es crear un fichero de settings de producción, que llamo `settings_production.py`, y cambio la configuración de `wsgi.py` para apuntar a este fichero en lugar de apuntar al estándar `settings.py`. Este nuevo fichero importará todos los settings que tenemos en `settings.py`, y luego cambiará los que necesitamos cambiar. De esta forma, cuando estoy desarrollando seguiré utilizando el fichero estándar, y en producción tendré la configuración más segura. Este fichero ya está creado en el repositorio de github, pero hay que configurarlo con los valores adecuados. Está en el mismo directorio que `settings.py`, y tiene este contenido:

```python
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['IP DEL SERVIDOR', 'DOMINIO']
CSRF_TRUSTED_ORIGINS = ['https://DOMINIO']

with open('/usr/local/etc/conta/secret_key') as f:
    SECRET_KEY = f.read().strip()
```

Debes utilizar la IP de tu servidor, y el DOMINIO donde estará corriendo el servidor. Además la clave secreta es conveniente tenerla en otra carpeta que no esté dentro del proyecto, para evitar que se pueda acceder desde la web. Por esta razón la guardamos en un fichero que leemos desde django.

Ahora tenemos que crear este fichero. Vamos a crear primero la carpeta donde guardamos varias configuraciones para nuestro proyecto:

```bash
mkdir -p /usr/local/etc/conta
vi /usr/local/etc/conta/secret_key
```

La clave secreta ([SECRET_KEY](https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-SECRET_KEY)) es una secuencia única de carácteres, y suficientemente larga. Una clave única se puede obtener por ejemplo de: [http://uuid.online](http://uuid.online) (o por cualquier otro método). Guarda la clave en ese fichero, para ser leída por django.


## Configuración de gunicorn

Comprobar primero que gunicorn funciona. Ejecutar el comando:

```bash
gunicorn conta.wsgi -b IP:8000
```

Utilizando la IP del servidor. Comprobar que el servidor en: http://IP:8000 funciona correctamente (atención, las imágenes no se verán, ni los archivos CSS, por ser archivos estáticos: el servidor gunicorn no sirve archivos estáticos).

Una vez comprobado que funciona, vamos a crear la configuración para lanzar gunicorn como demonio al arrancar la máquina.

Primero tenemos que crear el fichero de configuración de gunicorn. Utilizaremos la carpeta que ya hemos creado, vamos a llamar ese fichero `/usr/local/etc/locallibrary/gunicorn_conf.py`. El contenido de este fichero debe ser el siguiente:

```python
command = '/home/django/projects/conta/.venv/bin/gunicorn'
pythonpath = '/home/django/projects/conta'
bind = 'IP:8000'
workers = 3
user = 'django'
group = 'django'
daemon = True
wsgi_app = 'conta.wsgi'
pidfile = '/var/run/gunicorn.conta.pid'
```

Sustituye la IP por la ip del servidor. Aquí estamos indicando los parámetros para la ejecución de gunicorn. Ahora tenemos que crear un servicio de arranque, y lo haremos en la carpeta `/usr/local/etc/rc.d`. Esta carpeta ya ha sido creada al instalar nginx, ya que contiene el fichero de arranque de nginx. Vamos a crear el fichero `/usr/local/etc/rc.d/conta`, con el siguiente contenido:

```bash
#!/bin/sh

# PROVIDE: locallibrary
# REQUIRE: netif

. /etc/rc.subr

name="conta"
rcvar="${name}_enable"

pidfile="/var/run/gunicorn.conta.pid"
extra_commands="status"
start_cmd="/home/django/projects/conta/.venv/bin/gunicorn -c /usr/local/etc/conta/gunicorn_conf.py ; echo $name is now running on PID $(cat $pidfile)"
stop_cmd="kill $(cat $pidfile) ; echo $name is not running. ; rm $pidfile"
status_cmd="if [ -e $pidfile ]; then echo $name is running on PID $(cat $pidfile). ; return 1; fi; echo $name is not running. ; return 0"

load_rc_config $name
run_rc_command "$1"
```

Para más información sobre estos comandos, consultar la documentación [Practical rc.d scripting in BSD](https://docs.freebsd.org/en/articles/rc-scripting/).

Ahora tenemos que hacer este fichero ejecutable, y configurar el servicio para que arranque automáticamente:

```bash
chmod +x /usr/local/etc/rc.d/conta
sysrc conta=YES
```

Ahora podemos arrancar el servicio con el comando:

```bash
service conta start
```

Otros comandos disponibles son:

```bash
service conta stop    # para el servicio
service conta status  # para saber el estado, si está arrancado o no
```

## Configuración nginx

Ahora tenemos que configurar nginx para servir las páginas. Aquí describo una configuración sin certificados, ya que en mi caso utilizo un _reverse proxy_ que es donde tengo configurado el certificado y protocolo https. Si no utilizas un _reverse proxy_, es conveniente que incluyas la configuración con certificados en este servidor.

En primer lugar, edita el fichero `/usr/local/etc/nginx/nginx.con`, reemplaza su contenido por el siguiente:

```
worker_processes  1;

events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;

    # Import server blocks for all subdomains
    include "vdomains/*.conf";
}
```

Ahora hay que crear una carpeta `/usr/local/etc/nginx/vdomains`, que contendrá los servidores para cada uno de los proyectos que tengamos.

El primero que crearemos será el servidor por defecto. Crea el fichero `/usr/local/etc/nginx/vdomains/default.conf`, con la siguiente configuración:

```
server {
	# if no Host match, close the connection to prevent host spoofing
	listen 80 default_server;
	return 444;
}
```

Esta configuración hace que si llega una petición que no encaja con ninguno de los servidores configurados, cierra la conexión.

Y ahora creamos el servidor para nuestro proyecto. Crea el fichero `/usr/local/etc/nginx/vdomains/conta.conf`, con la siguiente configuración:

```
server {
	listen       80;
	server_name  DOMAIN;

	access_log /var/log/nginx/conta.access.log;
	error_log /var/log/nginx/conta.error.log;

	location / {
		proxy_pass http://IP:8000;
		proxy_set_header Host $host;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
	}

	location /static/ {
		alias   /home/django/projects/conta/static/;
	}
}
```

Reemplaza IP por la ip de tu servidor, y DOMAIN por el dominio que utilices para alojar el servidor.

Fíjate en la configuración para los ficheros estáticos: las peticiones que empiezan con el _path_ `/static/` son servidas directamente por nginx, utilizando como directorio raíz el directorio donde hemos puesto los ficheros estáticos antes. Las demás peticiones son redirigidas a nuestro servidor gunicorn.

Ahora configuramos el servicio nginx para arrancar automáticamente, y lo arrancamos:

```bash
sysrc nginx_enable=yes
service nginx start
```

Si más adelante haces cambios en la configuración de nginx, puedes forzar la relectura de la configuración con el siguiente comando:

```bash
service nginx reload
```

Con esto estaría todo configurado para su correcto funcionamiento. No olvides utilizar un _reverse proxy_ para asegurar una conexión segura https, o bien cambiar la configuración de nginx para utilizar certificados y forzar el acceso a través de https.


## Uso de mariadb

Para una aplicación con pocos accesos, la base de datos sqlite es más que suficiente. Pero si esperas tener muchos accesos, o simplemente quieres hacerla más robusta, puedes utilizar mariadb como base de datos. Aquí explico los cambios necesarios para realizarlo.


### Instalación de mariadb

Primero hay que instalar mariadb:

```bash
pkg install -y mariadb105-server  # utiliza la última versión disponible
pip install mysqlclient
```

Editar el fichero `/usr/local/etc/mysql/my.cnf`, y sustituir la siguiente línea:

```
# línea a reemplazar:
socket  = /var/run/mysql/mysql.sock

# nueva línea:
socket  = /tmp/mysql.sock
```

Ahora configuramos el servicio para empezar automáticamente, y lo arrancamos:

```bash
sysrc mysql_enable=yes
service mysql-server start
```

### Securización de mariadb, y creación de la base de datos

Lanzamos el siguiente script para securizar la configuración de mariadb, según recomendación del fabricante:

```bash
mysql_secure_installation --socket=/tmp/mysql.sock
```

Acepta todos los valores por defecto, y crea un password de root para acceder a mariadb. Este password tendrás que utilizarlo en el siguiente paso. Este escript implementa las mejores prácticas para securizar la base de datos. Ahora vamos a deshabilitar también el acceso remoto a la base de datos:

```bash
sysrc mysql_args="--bind-address=127.0.0.1"
service mysql-server restart
```

A continuación creamos la base de datos:

```bash
mysql -u root -p
```

Entra el password de root que acabas de crear, y ahora entra los siguientes comandos para crear la base de datos:

```
CREATE DATABASE conta CHARACTER SET UTF8;
CREATE USER 'accountant'@'localhost' IDENTIFIED BY 'accountant-password';
GRANT ALL ON conta.* TO 'accountant'@'localhost';
FLUSH PRIVILEGES;
exit
```

Utiliza el nombre de base de datos, usuario y password de tu gusto. Estos los necesitaremos luego para la configuración de django.


### Configuración de Django - base de datos

Ahora tenemos que actualizar los ajustes de nuestro proyecto. Abre el fichero `settings.py` de nuestro proyecto, y reemplaza la antigua configuración por la nueva:

```python
#### antigua configuración (la que viene por defecto) #####
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

##### nueva configuración #####
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'conta',
        'USER': 'accountant',
        'PASSWORD': 'accountant-password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```

Aquí es donde ponemos los valores que hemos utilizado antes. Para mayor seguridad, podemos poner el usuario y password de la base de datos en otro directorio, igual que hemos hecho con la clave secreta. En ese caso cambiamos la configuración de la siguiente forma, crando también un fichero nuevo:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/usr/local/etc/conta/mariadb.cnf',
        },
    }
}

# /usr/local/etc/conta/mariadb.cnf
[client]
database = conta
user = accountant
password = accountant-password
default-character-set = utf8
```

Una vez realizados estos cambios en la configuración, hay que correr las migraciones:

```bash
python manage.py makemigrations
python manage.py migrate
```

Y finalmente volver a crear un superusuario:

```
python manage.py createsuperuser
```

## Referencias

Para crear esta guía, he consultado los siguientes artículos y documentación:

- [Django project documentation](https://docs.djangoproject.com)
- [Django deployment checklist](https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/)
- [Gunicorn configuration](https://docs.gunicorn.org/en/latest/deploy.html)
- [Practical rc.d scripting in BSD](https://docs.freebsd.org/en/articles/rc-scripting/)
- [How To Use MySQL or MariaDB with your Django Application on Ubuntu 14.04](https://www.digitalocean.com/community/tutorials/how-to-use-mysql-or-mariadb-with-your-django-application-on-ubuntu-14-04)
