# Fabio González Waschkowitz

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/HolaMundo', methods=['GET'])

def ejecutar_sql(peticion):
    #Datos de conexión
    host = "localhost"              # Ejemplo 'localhost'
    port = "5432"                   # Puerto por defecto de PostgreSQL
    dbname = "alexsoft"             # Nombre de la base de datos
    user = "postgres"               # Usuario de la base de datos
    password = "postgres"           # Constraseña del usuario

    try:
        #Establecer la conexión
        connection = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
        )

        # Crear un cursor para ejecutar consultas
        cursor = connection.cursor()

        # Consulta SQL (por ejemplo, selecciona todos los registros de una tabla llamada "usuarios")
        cursor.execute(peticion)

        # Obtener columnas para construir claves del JSON
        columnas = [desc[0] for desc in cursor.description]

        #Convertir resultados a JSON
        resultados = cursor.fetchall()
        empleados = [dict(zip(columnas, fila)) for fila in resultados]

        # Cerrar el cursor y la conexión
        cursor.close
        connection.close()

        return jsonify(empleados)

    except psycopg2.Error as e:
        return jsonify({"error": "motivo del error: " + str(e)}), 500


# Login
@app.route('/gestor/login', methods=['POST'])
def login():
   body_request = request.json
   user = body_request["user"]
   passwd = body_request["passwd"]
   is_logged= ejecutar_sql(
       f"SELECT * FROM public.\"gestor\" WHERE usuario = '{user}' AND passwd = '{passwd}';"
   )

   if len(is_logged.json) == 0:
       return jsonify({"msg": "login error"})

   empleado = ejecutar_sql(
       f"SELECT * FROM public.\"Empleado\" WHERE id = '{is_logged.json[0]['empleado']};"
   )

   return jsonify(
       {
           "id_empleado": empleado.json[0]["id"],
           "id_gestor": is_logged.json[0]["id"],
           "nombre": empleado.json[0]['nombre'],
           "email": empleado.json[0]['email']
       }
   )


# Crear proyecto
@app.route('/crear/proyecto', methods=['POST'])
def crear_proyecto():
   try:
       body_request = request.json
       nombre = body_request['nombre']
       descripcion = body_request['descripcion']
       fecha_inicio = body_request['fecha_inicio']
       fecha_finalizacion = body_request['fecha_finalizacion']
       cliente = body_request['cliente']

       query = f'''
       INSERT INTO public."Proyecto" (
           nombre, descripcion, fecha_creacion, fecha_inicio, fecha_finalizacion, cliente
       ) VALUES (
           '{nombre}',
           '{descripcion}',
           CURRENT_TIMESTAMP,
           '{fecha_inicio}',
           '{fecha_finalizacion}',
           {cliente}
       )
       RETURNING id;
       '''
       proyecto = ejecutar_sql(query)

       return jsonify({"id": proyecto[0]['id'], "mensaje": "Proyecto creado"}), 201

   except psycopg2.Error as e:
       return jsonify({"error": "Motivo del error: " + str(e)}), 500


# Asignar gestor a proyecto
@app.route('/asignarGestor/aProyecto', methods=['POST'])
def asignar_gestor_a_proyecto():
    try:
        body_request = request.json
        gestor_id = body_request['gestor']
        proyecto_id = body_request['proyecto']

        gestor_query = f"SELECT id FROM public.\"Gestor\" WHERE id = {gestor_id};"
        proyecto_query = f"SELECT id FROM public.\"Proyecto\" WHERE id = {proyecto_id};"

        if not ejecutar_sql(gestor_query) or not ejecutar_sql(proyecto_query):
            return jsonify({"error": "Gestor o Proyecto no existe"}), 404

        query = f"""
        INSERT INTO public."GestoresProyecto" (gestor, proyecto, fecha_asignacion)
        VALUES ({gestor_id}, {proyecto_id}, CURRENT_TIMESTAMP);
        """
        ejecutar_sql(query)

        return jsonify({"mensaje": f"Gestor {gestor_id} asignado al proyecto {proyecto_id}"}), 201

    except psycopg2.Error as e:
        return jsonify({"error": "Motivo del error: " + str(e)}), 500

# Asignar cliente a proyecto
@app.route('/asignarCliente/Proyecto', methods=['POST'])
def asignar_cliente_a_proyecto():
    try:
        body_request = request.json
        cliente_id = body_request['cliente']

        cliente_query = f"SELECT id FROM public.\"Cliente\" WHERE id = {cliente_id};"
        if not ejecutar_sql(cliente_query):
            return jsonify({"error": "Cliente no existe"}), 404

        query = f"""
        INSERT INTO public."Proyecto" (nombre, descripcion, fecha_creacion, fecha_inicio, fecha_finalizacion, cliente)
        VALUES ('{body_request['nombre']}', '{body_request['descripcion']}', NOW(),
                '{body_request['fecha_inicio']}', '{body_request['fecha_finalizacion']}', {cliente_id});
        """
        ejecutar_sql(query)

        return jsonify({"mensaje": f"Cliente {cliente_id} asignado al proyecto '{body_request['nombre']}'"}), 201

    except psycopg2.Error as e:
        return jsonify({"error": "Motivo del error: " + str(e)}), 500

# Crear tareas a un proyecto
@app.route('/crearTareas/aProyecto', methods=['POST'])
def crear_tareas_a_proyecto():
    try:
        body_request = request.json
        nombre = body_request['nombre']
        descripcion = body_request['descripcion']
        estimacion = body_request['estimacion']
        fecha_creacion = body_request['fecha_creacion']
        fecha_finalizacion = body_request['fecha_finalizacion']
        programador = body_request['programador']
        proyecto = body_request['proyecto']

        query = f"""
        INSERT INTO public."Tarea" (nombre, descripcion, estimacion, fecha_creacion, fecha_finalizacion, programador, proyecto)
        VALUES ('{nombre}', '{descripcion}', {estimacion}, '{fecha_creacion}', '{fecha_finalizacion}', {programador}, {proyecto});
        """
        ejecutar_sql(query)

        return jsonify({"mensaje": "Tarea creada"}), 201

    except psycopg2.Error as e:
        return jsonify({"error": "Motivo del error: " + str(e)}), 500

# Asignar programador a proyecto
@app.route('/asignarProgramador/aProyecto', methods=['POST'])
def asignar_programador_a_proyecto():
    try:
        body_request = request.json
        programador_id = body_request['programador']
        proyecto_id = body_request['proyecto']

        programador_query = f"SELECT id FROM public.\"Programador\" WHERE id = {programador_id};"
        proyecto_query = f"SELECT id FROM public.\"Proyecto\" WHERE id = {proyecto_id};"

        if not ejecutar_sql(programador_query) or not ejecutar_sql(proyecto_query):
            return jsonify({"error": "Programador o Proyecto no existe"}), 404

        query = f"""
        INSERT INTO public."ProgramadoresProyecto" (programador, proyecto, fecha_asignacion)
        VALUES ({programador_id}, {proyecto_id}, CURRENT_TIMESTAMP);
        """
        ejecutar_sql(query)

        return jsonify({"mensaje": f"Programador {programador_id} asignado al proyecto {proyecto_id}"}), 201

    except psycopg2.Error as e:
        return jsonify({"error": "Motivo del error: " + str(e)}), 500


# Obtener programadores
@app.route('/programadores',methods=['GET'])
def obtener_programadores():
    try:
        resultado = ejecutar_sql(
            """
            SELECT * FROM public."Programador"
            ORDER BY id ASC 
            """
        )

        return resultado

    except psycopg2.Error as e:
        return jsonify({"error": "motivo del error: " + str(e)}), 500


# Obtener proyectos (activos o todos)
@app.route('/proyecto/proyectos',methods=['GET'])
def obtener_proyectos():
    try:
        resultado = ejecutar_sql(
            """
            SELECT * FROM public."Proyecto"
            ORDER BY id ASC 
            """
        )

        return resultado

    except psycopg2.Error as e:
        return jsonify({"error": "motivo del error: " + str(e)}), 500


# Obtener tareas de un proyecto (sin asignar o asignado)
@app.route('/tareasDeProyectos',methods=['GET'])
def obtener_tareas_de_un_proyecto():
    try:
        resultado = ejecutar_sql(
            """
            SELECT 
                t.id AS tarea_id,
                t.nombre AS tarea_nombre,
                t.descripcion AS tarea_descripcion,
                t.estimacion AS tarea_estimacion,
                t.fecha_creacion AS tarea_fecha_creacion,
                t.fecha_finalizacion AS tarea_fecha_finalizacion,
                t.programador AS tarea_programador,
                p.nombre AS proyecto_nombre,
                p.descripcion AS proyecto_descripcion
            FROM 
                public."Tarea" t
            JOIN 
                public."Proyecto" p ON t.proyecto = p.id
            WHERE 
                p.id = t.proyecto
            """
        )

        return resultado

    except psycopg2.Error as e:
        return jsonify({"error": "motivo del error: " + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)