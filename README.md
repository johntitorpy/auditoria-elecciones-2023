# Datos de la mesa
Departamento: 11

Distrito: 29

Zona: 0

Local: 11

Mesa 2

# Analisis
Hemos detectado una vulnerabilidad de seguridad del software, con la cual es posible la carga de votos con la complicidad de las autoridades de la mesa, esto es posible debido a que el software tiene una falla que no registra la fecha y la hora de cada boleta al momento de crear el voto.
En la mesa en cuestion, se tienen 389 votos y se tiene registrada la hora de recepcion del TREP a las 2023-04-30 19:32:04, en el dia de la votacion se pudo observar que no era humanamente posible votar en menos de 3 minutos, 389 votos requieren aproximadamente 19 horas de votacion.
Hemos auditado el codigo fuente y llegamos a la conclusion de que no existe ninguna rutina o variable asignada que contenga la fecha y la hora del voto en su respectiva boleta, por eso necesitamos la apertura del sobre 4 para auditar el contenido de las boletas y verificar que las mismas no contienen la fecha y la hora grabadas en el chip RFID de las boletas.

# Una posible correción
[WIP - Add timetamp in the tag](https://github.com/johntitorpy/auditoria-elecciones-2023/pull/1#issue-1708809248)
