# Histórico de eventos
Desde el conteo de los votos dentro del TSJE (Tribunal Superior de Justicia Electoral), se han detectado patrones e impugnado mesas, entendiendo como buscar estos patrones procedimos a crear una base de datos postgres y utilizar sql para analizar los datos.

En el proceso de analizar los datos, se vió necesario la apertura del sobre 4 para las mesas que detectamos, necesitamos ver el patron de la duracion del tiempo de cada votación, de lo contrario es vulnerable a que las autoridades de mesa hayan generado esos votos artificiales.

# Datos de la mesa
Departamento: 11

Distrito: 29

Zona: 0

Local: 11

Mesa: 2

# Analisis
Hemos detectado que teniendo la complicidad de las autoridades de mesa, es posible generar votos, también hemos verficado que el software de las urnas no guarda la fecha y la hora de cada voto.

En la mesa en cuestion, se tienen 389 votos y se tiene registrada la hora de recepcion del TREP (Transmision de Resultados Electorales Pre-eliminares) a las 2023-04-30 19:32:04, en el dia de la votacion se pudo observar que no era humanamente posible votar en menos de 3 minutos, 389 votos requieren aproximadamente 19 horas de votacion.

# Que necesitamos?
1 - Necesitamos ayuda de voluntarios que puedan confirmar que el software de las elecciones no registra la fecha y la hora de cada voto.

2 - Necesitamos ayuda para difundir el mensaje y explicar a la población que este sistema tiene una falla que permite la creación de votos artificiales.


# Una posible correción
[WIP - Add timetamp in the tag](https://github.com/johntitorpy/auditoria-elecciones-2023/pull/1#issue-1708809248)
