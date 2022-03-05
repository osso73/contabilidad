# Mecanismo de funcionamiento

## Teoría

Esta aplicación funciona con los mismos principios de contabilidad que pueda utilizar una empresa, pero de forma muy simplificada. Básicamente, tenemos 3 tipos de información:

1. Los movimientos: son las transacciones de dinero. Registran el movimiento de dinero entre dos o más cuentas. Los movimientos se agrupan por asiento, siendo cada asiento de uno o más movimientos.

2. Las cuentas: son las que contienen el dinero. Puede haber cuentas de gastos, es decir que registran los gastos que tenemos, como por ejemplo: "Gastos de la casa", "Comida", "Ropa", o "Viajes"; otras cuentas de ingresos, como por ejemplo: "Nómina del trabajo", o "Intereses del banco" o "Alquiler recibido"; y otras donde hay entradas y salidas de dinero, como son las cuentas de los bancos, tarjetas, etc.

3. Las etiquetas: se aplican a las cuentas, y permiten agrupar las cuentas para hacer los informes. Por ejemplo, podemos agrupar todas las cuentas de gastos bajo la etiqueta "gastos". Cada cuenta puede tener varias etiquetas.

En cada movimiento o transacción _sale_ o _entra_ dinero de una cuenta. _Salir_ significa que el dinero se resta del total que tiene la cuenta; _entrar_ significa que se suma el dinero. La diferencia entre entradas y salidas se denomina el saldo de la cuenta.

Cada movimiento consta del número de asiento al que pertenece, la fecha, una descripción, los campos _debe_ y _haber_, y la cuenta involucrada en el movimiento. En cada movimiento, sólo uno de los campos _debe_ o _haber_ tiene un valor, y además debe ser positivo; el otro vale 0. Si el campo _debe_ es el que tiene el valor distinto de 0, significa que el dinero _sale_ de la cuenta en ese movimiento; si es el campo _haber_, entonces el dinero _entra_ a la cuenta.


## Estructura de las cuentas

La estructura que se define de cuentas es muy importante para poder obtener información de los datos que entramos. Si esta estructura no es correcta, la información que obtenemos al hacer los informes no es interesante. Debemos tener el nivel de detalle adecuado: si agregamos muchos gastos en una sola cuenta, no sabremos bien cómo se distribuyen los gastos o ingresos; si somos demasiado detallados, será más difícil obtener una fotos general de los gastos (aunque se pueden agrupar por etiquetas, no tiene demasiado sentido entrar en un sistema muy complejo).

Vamos a definir 3 tipos de cuentas, como hemos comentado antes: las de gastos, las de ingresos, y las que llamo de _balance_, donde tenemos tanto entradas como salidas.


### Ingresos

Estas son las más sencillas, ya que corresponden a las fuentes de ingresos que tenemos. Creamos una cuenta para cada fuente de ingresos, de esta forma podremos ver cómo contribuye cada fuente a nuestro patrimonio. Ejemplos que encontramos en este apartado son:

  - nómina del lugar donde trabajamos. En caso de ser varias personas en la unidad familiar, crear una cuenta para cada uno. Y en caso de tener varios trabajos, también crear varias cuentas.

  - intereses bancos. Se puede desglosar en varias cuentas (por banco, u otros criterios) si se quiere tener más detalle.

  - regalos. Eso puede ser otra fuente de ingresos que queremos identificar.

  - alquiler recibido. En caso de tener más de una propiedad en alquiler, tiene sentido crear una cuenta por propiedad.

  - rendimiento fondos / acciones: esta cuenta debería ser en general una cuenta de ingresos, aunque también puede tener pérdidas. Se pueden varias, por ejemplo para separar rendimientos de acciones de los de fondos, o por banco, etc. A gusto de cada uno.


### Balance

Estas cuentas también son relativamente sencillas, ya que deberían reflejar las cuentas y tarjetas que tengamos. En general hay que definir:

  - una cuenta para cada cuenta bancaria que tenemos. De esta forma podremos comprobar después el extracto del banco si corresponde a los movimientos que tenemos registrados.

  - una cuenta para cada tarjeta de crédito. Ojo, las tarjetas de débito no, ya que estas cargan directamente a la cuenta del banco. Por tanto, pagar con una tarjeta de débito es equivalente a pagar con la cuenta asociada. Las tarjetas de crédito son las que pagan los gastos, y a final de mes reciben los fondos para quedarse a 0, cuando el banco nos carga el importe de la tarjeta (es decir, en ese momento el dinero pasa de una de las cuentas a la tarjeta)

  - una cuenta para cada mecanismo de pago que tengamos, entendiendo los mecanismos como una forma de acumular dinero que luego puedo gastar. Por ejemplo: paypal, tarjetas via-T, tarjetas de pre-pago, botes para compartir gastos, etc.

  - cada préstamo bancario o hipoteca debería tener su cuenta asociada. De esta forma vemos cúanto debemos, y cómo se va reduciendo la deuda al hacer pagos.

  - también puede ser interesante crear una cuenta para deudas (i.e. dinero que nos han prestado y deberíamos devolver), y préstamos que hemos hecho (y esperamos que nos devuelvan). También podría ser la misma cuenta, aunque es más sencillo que estén separadas. De esta forma podemos ver fácilmente cuánto dinero nos deben, y cuánto debemos (igual que en el caso de la hipoteca). Cuando todas las deudas y préstamos estén saldados, el saldo debe ser 0.


### Gastos

Esta categoría es la más complicada y difícil de definir, ya que depende mucho de la granularidad que se quiera tener. Por ejemplo, puedo definir una cuenta de gastos de viaje, que incluya todos los gastos; o bien cuentas distintas para gastos de transporte, gastos de alojamiento, gastos de comidas, gastos de visitas; o bien incluso dentro de transporte distinguir el medio de transporte (una cuenta para aviones, otra para tren, etc.).

Se puede tener un nivel de granularidad distinto en cada cosa: quizás quiero tener mucho detalle en los viajes, porque hago muchos y luego puedo analizar cómo he gastado el dinero; y menos detalle en los gastos médicos, y tener una sola cuenta para todos los gastos médicos (farmacia, consultas, ingresos hospital, vacunas, PCRs, etc.).

Algunos ejemplos de cuentas pueden ser:

  - gastos educación
  - gastos comida
  - gastos ropa
  - etc.


## Ejemplos

### Ejemplo 1. Compro un jersey

Pongamos que compro un jersey con mi tarjeta, la transacción se representa con un asiento simple, es decir un asiento con dos movimientos: uno asociado a la cuenta de la tarjeta, con el valor del jersey en el debe (es decir, el dinero sale de la cuenta de la tarjeta), y otro movimiento asociado a la cuenta "Ropa" con el valor del jersey en el haber (el dinero entra en la cuenta "Ropa"). Cuando pida un informe de la cuenta "Ropa", podré ver todos los movimientos donde entra dinero en esa cuenta, y sumando sabré lo que me he gastado en ropa (por día, por semana, por mes, etc.).


### Ejemplo 2. Hipoteca.

Cuando compro un piso, pongamos que me cuesta 100.000€. Yo pago 20.000€ de la cuenta de ahorro, y el banco me da una hipoteca por 80.000€. Esto se representa con un asiento complejo, de 3 movimientos:

  - De la cuenta "Cuenta Ahorro" salen 20.000€, es decir tengo 20,000€ en el debe (lógicamente esto requeriría que la cuenta tuviera un saldo superior a 20.000€, pero eso no lo comprueba la aplicación).
  - De la cuenta "Hipoteca" salen 80.000€, por tanto también en el debe.
  - Y tenemos 100.000€ que entran a la cuenta "Gastos casa", por tanto en el haber.

Tanto en el debe como en el haber tenemos un total de 100.000€.

Ahora la cuenta "Hipoteca" tiene un saldo negativo de 80.000€. Eso es lo que debemos al banco. Cada mes iremos pagando la cuota de la hipoteca, lo cual será otra vez un asiento complejo de 3 movimientos. Pongamos que la cuota es de 1.000 €:

  - De la cuenta "Cuenta Nómina" salen 1.000€, es decir están en su debe
  - A la cuenta "Intereses hipoteca" entran la parte de los intereses (que será variable, ya que depende del interés de cada mes, y de la cantidad de capital restante). Pongamos que es 400€. Este valor irá en el haber.
  - A la cuenta "Hipoteca" entrará la parte de capital, para ir amortizando la deuda que tengo pendiente. Por tanto pongo 600€ en el haber.

Ahora tengo también en el debe y en el haber la misma cantidad, 1.000€. Cuando pida un informe sobre la cuenta "Hipoteca", obtengo que tenía 80.000€ en el debe, y 600€ en el haber. Por tanto, mi saldo restante es de 79,400€. Es la deuda que tengo pendiente. A medida que pasen los meses, esa deuda se irá decrementando con la aportación de las cuotas.


### Ejemplo 3. Saldo inicial

Para que salgan bien las cuentas, debemos partir de un saldo inicial. Es decir, cuando empezamos a hacer la contabilidad, ya tengo algún dinero en las cuentas del banco, algunos gastos hechos en mis tarjetas, quizás una hipoteca a medio pagar, y algún fondo de inversión.

Todo eso se puede definir en un asiento inicial, donde se pone el valor de cada una de las cuentas:

  - El dinero que tengo en cuentas bancarias, paypal, tarjetas de prepago, etc. se pone en el haber de cada cuenta.

  - El dinero que he gastado con mi tarjeta de crédito se pone en el debe de la cuenta correspondiente.

  - En la cuenta "Hipoteca" se pone el valor de capital pendiente de amortizar en el debe.

  - Los fondos de inversión, acciones, etc. también se añade su valor en la fecha inicial de empezar la contabilidad, y se pone en el haber.

  - Para completar el asiento, se puede añadir un movimiento a una cuenta "Patrimonio inicial", de forma que el total del debe y el haber de este asiento sean iguales. Esta cuenta nos indica cuál es el valor neto de nuestro patrimonio al empezar la contabilidad, teniendo en cuenta todas las deudas, y todos los activos.
