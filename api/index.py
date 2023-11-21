import base64
import json
import mimetypes
import os
import tempfile
from datetime import timedelta

from flask import Flask, request, send_file, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from _mega.mega import Mega

app = Flask(__name__)
mega = Mega()
m = mega.login(os.getenv('EMAIL'), os.getenv('PASS'))
file_mapping = {}
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Cambia esto por una clave real en producción
jwt = JWTManager(app)

app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    # Valida las credenciales del usuario (este es solo un ejemplo)
    if username != os.getenv('JWT_USERNAME') or password != os.getenv('JWT_PASSWORD'):
        return jsonify({"msg": "Credenciales incorrectas"}), 401

    expires = timedelta(hours=8)  # El token expira después de 8 hora
    access_token = create_access_token(identity=username, expires_delta=expires)

    return jsonify(access_token=access_token)

def update_file_mapping():
    files = m.get_files()
    global file_mapping
    file_mapping = {file_key: file_info for file_key, file_info in files.items()}

def decrypt_attr(attr):
    # Asumiendo que 'attr' es una cadena codificada en base64
    try:
        decoded_attr = base64.urlsafe_b64decode(attr + '==').decode('utf-8')
        # Interpretar la cadena como JSON y obtener el nombre del archivo o carpeta
        return json.loads(decoded_attr[4:])['n']
    except Exception as e:
        print("Error al decodificar:", e)
        return None

@app.route('/')
def home():
    return 'It works!!'


@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_to_mega():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Subir archivo a MEGA
        upload_response = m.upload(filepath)

        # Obtener la file_key del archivo subido
        if 'f' in upload_response and len(upload_response['f']) > 0:
            uploaded_file_key = upload_response['f'][0]['h']
        else:
            # Opcional: Eliminar el archivo del sistema local después de la carga
            os.remove(filepath)
            return jsonify({'error': 'Error al subir el archivo'}), 500

        # Opcional: Eliminar el archivo del sistema local después de la carga
        os.remove(filepath)

        # Actualizar el mapeo de archivos
        update_file_mapping()

        return jsonify({'success': 'File uploaded successfully', 'file_key': uploaded_file_key}), 200

@app.route('/download/<file_key>', methods=['GET'])
@jwt_required()
def download_file(file_key):
    if file_key not in file_mapping:
        update_file_mapping()

    if file_key in file_mapping:
        file_info = file_mapping[file_key]
        file_info_tuple = (file_key, file_info)

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                print("Usando directorio temporal:", temp_dir)
                abs_temp_dir = os.path.abspath(temp_dir)
                file_path = m.download(file_info_tuple, abs_temp_dir)
                mime_type, _ = mimetypes.guess_type(file_path)

                print("Archivo descargado en:", file_path)

                return send_file(
                    file_path,
                    mimetype=mime_type,
                    as_attachment=True,
                    download_name=os.path.basename(file_path)
                )
        except Exception as e:
            print("Error durante la descarga:", e)
            return {'error': 'Error interno del servidor'}, 500
    else:
        return {'error': 'Archivo no encontrado'}, 404

@app.route('/delete/<file_key>', methods=['DELETE'])
@jwt_required()
def delete_file(file_key):
    print("Delete")
    if file_key not in file_mapping:
        print("Archivo no encontrado, actualizando indices")
        update_file_mapping()

    if file_key in file_mapping:
        print("Archivo encontrado")
        file_info = file_mapping[file_key]
        file_info_tuple = (file_key, file_info)
        print("Tupla: ", file_info_tuple)

        try:
            print("Borrando")
            m.delete(file_info_tuple[0])
            return {'message': 'Archivo eliminado correctamente'}, 200
        except Exception as e:
            return {'error': 'Error al eliminar el archivo', 'details': str(e)}, 500
    else:
        return {'error': 'Archivo no encontrado'}, 404

@app.route('/list', methods=['GET'])
@jwt_required()
def list_files():
    files = m.get_files()
    file_list = []
    for file_key, file_info in files.items():
        # Verificar si es un archivo (tipo 0) o una carpeta (tipo 1)
        if file_info['t'] in [0, 1]:
            file_name = None
            if isinstance(file_info['a'], dict):
                # Caso donde 'a' es un diccionario y contiene 'n'
                file_name = file_info['a'].get('n')
            elif isinstance(file_info['a'], str):
                # Caso donde 'a' es una cadena codificada
                file_name = decrypt_attr(file_info['a'])

            if file_name:
                file_list.append({
                    'key': file_key,
                    'name': file_name,
                    'size': file_info.get('s', 'N/A'),
                    'type': 'Folder' if file_info['t'] == 1 else 'File'
                })

    return {'files': file_list}

@app.route('/details', methods=['GET'])
@jwt_required()
def details():
    details = m.get_user()
    quota = m.get_quota()
    space = m.get_storage_space(kilo=True)

    return {'details ': details, 'quota':quota, 'space':space}

if __name__ == '__main__':
    app.run(debug=True)
    update_file_mapping()
