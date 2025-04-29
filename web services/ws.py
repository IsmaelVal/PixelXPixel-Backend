import pymssql
from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import hashlib

app = Flask(__name__)
CORS(app)

app.secret_key = 'your_secret_key'  # Replace with a strong, random secret key

SERVER = 'localhost'
DATABASE = 'master'
USERNAME = 'sa'
PASSWORD = 'YourPassword123!'

# Diccionario para claves primarias correctas
PRIMARY_KEYS = {
    "usuario": "idusuario",
    "boleto": "idboleto",
    "casillapixel": "idpixel",
    "imagen": "idimagen",
    "pregunta": "idpregunta",
    "evento": "idevento"
}

def get_db_connection():
    try:
        conn = pymssql.connect(
            server=SERVER, port=1433, database=DATABASE, user=USERNAME, password=PASSWORD)
        return conn
    except Exception as e:
        print(f"Error conectando a BD: {e}")
        return None


def verify_password(stored_password_hash, provided_password):
    hashed_provided_password = hashlib.sha1(
        provided_password.encode()).hexdigest()
    return stored_password_hash == hashed_provided_password

@app.route('/usuariored', methods=['POST'])
def registro_red_social():
    """
    Recibe JSON { usuario: <nombreFacebook>, contacto: 'Facebook' }
    y guarda (o recupera) ese usuario en tu tabla 'usuario'.
    Devuelve: { mensaje: ..., idUsuario: <nuevo o existente> }
    """
    try:
        data = request.get_json()
        nombre_fb = data.get('usuario')
        contacto  = data.get('contacto')  # aquí siempre 'Facebook'

        if not nombre_fb or not contacto:
            return jsonify({'error': 'Faltan campos obligatorios'}), 400

        conn   = get_db_connection()
        cursor = conn.cursor(as_dict=True)

        # 1) Si ya existe un username igual, devolvemos su id:
        cursor.execute("SELECT idusuario FROM usuario WHERE username = %s", (nombre_fb,))
        existe = cursor.fetchone()
        if existe:
            conn.close()
            return jsonify({
                'mensaje': 'Usuario ya registrado',
                'idUsuario': existe['idusuario']
            }), 200

        # 2) Si no existe, insertamos uno nuevo (sin contraseña)
        cursor.execute(
            "INSERT INTO usuario (username, contrasena, puntaje) VALUES (%s, %s, %s)",
            (nombre_fb, '', 0)
        )
        conn.commit()

        # 3) Obtenemos el último id insertado
        cursor.execute("SELECT @@IDENTITY AS idusuario")
        nuevo = cursor.fetchone()['idusuario']
        conn.close()

        return jsonify({
            'mensaje': 'Registrado exitosamente',
            'idUsuario': nuevo
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Se requiere usuario y contraseña'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(
                "SELECT username, contrasena FROM usuario WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and verify_password(user['contrasena'], password):
                session['username'] = username
                return jsonify({'mensaje': 'Autenticacion exitosa'}), 200
            else:
                return jsonify({'error': 'Usuario o password incorrectas'}), 401
        except Exception as e:
            return jsonify({'error': f'Error en BD {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

# --- Servicios CRUD para la tabla 'personajes' ---

# Obtener todos los personajes

@app.route('/test', methods=['GET'])
def get_all():
    data = request.json
    table = data['table']
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM ' + table)
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)

@app.route('/test/<table>/<int:id>', methods=['GET'])
def get_one(table, id):
    try:
        if table not in TABLES:
            return jsonify({'error': 'Tabla no válida'}), 400

        if table not in PRIMARY_KEYS:
            return jsonify({'error': 'Clave primaria no definida para esta tabla'}), 400

        primary_key = PRIMARY_KEYS[table]

        conn = get_db_connection()
        cursor = conn.cursor(as_dict=True)

        query = f"SELECT * FROM {table} WHERE {primary_key} = %s"
        cursor.execute(query, (id,))
        data = cursor.fetchone()
        conn.close()

        if data:
            return jsonify(data)
        else:
            return jsonify({'mensaje': 'Registro no encontrado'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# Añadir info

TABLES = {
    "usuario": ["username", "contrasena", "puntaje"],
    "boleto": ["tipo", "idusuario_usuario"],
    "casillapixel": ["estado", "posicion", "idimagen_imagen", "idusuario_usuario", "idpregunta_pregunta"],
    "imagen": ["respuesta", "horarespuesta", "idevento_evento"],
    "pregunta": ["opcionA", "opcionB", "opcionC", "opcionD", "opcioncorrecta", "numVecesRespondida", "pregunta"],
    "evento": ["horainicio", "horafin"]
}

@app.route('/test', methods=['POST'])
def create():
    try:
        data = request.json
        table = data.get('table')

        # Verificar si la tabla es válida
        if table not in TABLES:
            return jsonify({'error': 'Tabla no válida'}), 400

        # Obtener los campos y validar que todos están en la petición
        fields = TABLES[table]
        values = [data.get(field) for field in fields]

        # Hashear la contraseña si es usuario
        if table == 'usuario':
            contrasena_index = fields.index('contrasena')
            raw_password = values[contrasena_index]
            values[contrasena_index] = hashlib.sha1(raw_password.encode()).hexdigest()

        if None in values:
            return jsonify({'error': 'Faltan campos en la petición'}), 400

        # Construir la consulta SQL
        query = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(fields))})"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return jsonify({'mensaje': f'Registro insertado en {table}'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Actualizar 

@app.route('/test/<table>/<int:id>', methods=['PUT'])
def update(table, id):
    try:
        # Validar tabla
        if table not in TABLES:
            return jsonify({'error': 'Tabla no válida'}), 400

        if table not in PRIMARY_KEYS:
            return jsonify({'error': 'Clave primaria no definida para esta tabla'}), 400

        data = request.json
        fields = TABLES[table]

        # Preparar los campos a actualizar
        updates = {field: data.get(field) for field in fields if field in data}
        if not updates:
            return jsonify({'error': 'No hay datos para actualizar'}), 400

        # Construir SET y valores
        set_clause = ', '.join([f"{key} = %s" for key in updates.keys()])
        values = list(updates.values()) + [id]

        # Usar el nombre real de la primary key
        primary_key = PRIMARY_KEYS[table]

        query = f"UPDATE {table} SET {set_clause} WHERE {primary_key} = %s"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return jsonify({'mensaje': f'Registro en {table} actualizado correctamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Eliminar 
@app.route('/test/<table>/<int:id>', methods=['DELETE'])
def delete(table, id):
    try:
        if table not in TABLES:
            return jsonify({'error': 'Tabla no válida'}), 400

        if table not in PRIMARY_KEYS:
            return jsonify({'error': 'Clave primaria no definida para esta tabla'}), 400

        primary_key = PRIMARY_KEYS[table]

        conn = get_db_connection()
        cursor = conn.cursor()

        query = f"DELETE FROM {table} WHERE {primary_key} = %s"
        cursor.execute(query, (id,))
        conn.commit()
        conn.close()

        return jsonify({'mensaje': f'Registro en {table} eliminado correctamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)