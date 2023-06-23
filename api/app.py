from flask import Flask, make_response, request, jsonify
from flask_pymongo import PyMongo, ObjectId
from flask_cors import CORS
import pdfkit

from dotenv import load_dotenv
import os

load_dotenv()

Key = os.environ.get("KEY_GMAIL")
Url = os.environ.get("URL_DBM")

app = Flask(__name__)
#Dar dirección Local
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['MONGO_URI'] = Url

#Se declara la conexión con la variable mongo
mongo = PyMongo(app)

CORS(app) #Para que la comunicación entre backend y frontend sea estable

dbAlum = mongo.db['Alumnos']
dbApo = mongo.db['Apoderados']
dbDesc = mongo.db['Descuento']
dbHor = mongo.db['Horario']
dbPag = mongo.db['Pagos']
dbInfo = mongo.db['Informacion']

#Los que van a entrar modo admin o coordinador
dbSecre = mongo.db['Secretarias']
dbAdmin = mongo.db['Administrador']
dbCoor = mongo.db.Coordinador

#CREAR TOKEN
from datetime import datetime, timedelta
from flask import current_app
import jwt
import datetime

def generar_token(usuario):
    cod_administrador = usuario['cod_administrador']
    nombre = usuario['nombre']
    apellido = usuario['apellido']
    celular = usuario['celular']
    email = usuario['email']
    password = usuario['password']

    expiracion = datetime.utcnow() + timedelta(days=1)
    payload = {
        'cod_administrador': cod_administrador,
        'nombre': nombre,
        'apellido': apellido,
        'celular': celular,
        'email': email,
        'password': password,
        'exp': expiracion
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token


#CREAR ADMIN
@app.route('/registro-admin', methods=['POST'])
def crearAdmin():
    id = dbAdmin.insert_one({
        'cod_administrador': int(request.json['cod_administrador']),
        'nombre': request.json['nombre'],
        'apellido': request.json['apellido'],
        'celular': int(request.json['celular']),
        'email': request.json['email'],
        'password': request.json['password']
    })
    
    return jsonify(str(id.inserted_id))

@app.route('/administradores',   methods=['GET'])
def obtenerAdmins():
    administradores = [] #Se crea una lista para añadir los registros
    for doc in dbAdmin.find():
        administradores.append({
            'cod_administrador': doc['cod_administrador'],
            'nombre': doc['nombre'],
            'apellido': doc['apellido'],
            'celular': doc['celular'],
            'email': doc['email'],
            'password': doc['password']

        })
    return jsonify(administradores)


@app.route('/login', methods=['POST'])
def obtenerAdmin():
    data = request.get_json()
    cod_administrador = data['cod_administrador']
    cod_administrador = int(cod_administrador)
    email = data['email']
    password = data['password']
    
    administrador = dbAdmin.find_one({'cod_administrador': int(cod_administrador)})
    
    if not administrador:
        return jsonify({'error': 'El código de administrador es inválido'}), 400
    
    if administrador['email'] != email:
        return jsonify({'error': 'El correo electrónico es incorrecto'}), 400
    
    if administrador['password'] != password:
        return jsonify({'error': 'La contraseña es incorrecta'}), 400
    
    admin_data = {
        'cod_administrador': administrador['cod_administrador'],
        'nombre': administrador['nombre'],
        'apellido': administrador['apellido'],
        'celular': administrador['celular'],
        'email': administrador['email'],
        'password': administrador['password']
    }

    token = generar_token(admin_data)
    
    return jsonify({'token': token}), 200





@app.route('/administradores/<CODE>', methods=['DELETE'])
def borrarAdmins(CODE):
    dbAdmin.delete_one({'cod_administrador': int(CODE)})
    return jsonify({'mensaje': 'Administrador eliminado'})

@app.route('/administradores/<CODE>', methods=['PUT'])
def actualizarAdmins(CODE):
    #Se necesita el DNI para identificar que se va actualizar y el conjunto de datos a cambiar
    dbAdmin.update_one({'cod_administrador': int(CODE)}, {'$set': {
    'nombre': request.json['nombre'],
    'apellido': request.json['apellido'],
    'celular': request.json['celular'],
    'email': request.json['email'],
    'password': request.json['password']
    }})

    return jsonify({'mensaje': 'Administrador actualizado'})

#ALUMNOS
@app.route('/registro-e', methods=['POST'])
def crearAlumno():
    id = dbAlum.insert_one({
        'DNI': int(request.json['DNI']),
        'nombre': request.json['nombre'],
        'apellido': request.json['apellido'],
        'carrera': request.json.get('carrera', ''), #La funcion get busca si hay un dato y si no lo encuentra reemplaza por el segundo parametro vacio
        'celular': int(request.json.get('celular', 0)),
        'direccion': request.json['direccion'],
        'email': request.json['email'],
        'colegio': request.json['colegio'],
        'edad': int(request.json['edad'])
    })
    
    return jsonify(str(id.inserted_id))

@app.route('/alumnos', methods=['GET'])
def obtenerAlumnos():
    alumnos = [] #Se crea una lista para añadir los registros
    for doc in dbAlum.find():
        alumnos.append({
            'DNI': doc['DNI'],
            'nombre': doc['nombre'],
            'apellido': doc['apellido'],
            'carrera': doc['carrera'],
            'celular': doc['celular'],
            'direccion': doc['direccion'],
            'email': doc['email'],
            'colegio': doc['colegio'],
            'edad': doc['edad']
        })
    return jsonify(alumnos)

@app.route('/alumno/<DNI>', methods=['GET'])
def obtenerAlumno(DNI):
    alumno = dbAlum.find_one({'DNI': int(DNI)})
    if alumno:
        return jsonify({
            'DNI': alumno['DNI'],
            'nombre': alumno['nombre'],
            'apellido': alumno['apellido'],
            'carrera': alumno['carrera'],
            'celular': alumno['celular'],
            'direccion': alumno['direccion'],
            'email': alumno['email'],
            'colegio': alumno['colegio'],
            'edad': alumno['edad']
        })
    else:
        return jsonify({'error': 'Alumno no encontrado'})


@app.route('/alumnos/<DNI>', methods=['DELETE'])
def borrarAlumno(DNI):
    dbAlum.delete_one({'DNI': int(DNI)})
    return jsonify({'mensaje': 'Alumno eliminado'})

@app.route('/alumnos/<DNI>', methods=['PUT'])
def actualizarAlumno(DNI):
    #Se necesita el DNI para identificar que se va actualizar y el conjunto de datos a cambiar
    dbAlum.update_one({'DNI': int(DNI)}, {'$set': {
    'nombre': request.json['nombre'],
    'apellido': request.json['apellido'],
    'carrera': request.json['carrera'],
    'celular': request.json['celular'],
    'direccion': request.json['direccion'],
    'email': request.json['email'],
    'colegio': request.json['colegio'],
    'edad': request.json['edad']
    }})

    return jsonify({'mensaje': 'Alumno actualizado'})

#REGISTRAR DESCUENTO
@app.route('/registro-d', methods=['POST'])
def registrarDescuento():
    constancia_url = request.form['constancia_url'] if 'constancia_url' in request.form else request.json.get('constancia_url', '')
    descuento = float(request.form['descuento']) if 'descuento' in request.form else float(request.json.get('descuento', 0))

    id = dbDesc.insert_one({
        'tipo': request.form['tipo'] if 'tipo' in request.form else request.json.get('tipo', ''),
        'descuento': descuento,
        'constancia_url': constancia_url,
        'alumno_dni': int(request.form['alumno_dni']) if 'alumno_dni' in request.form else int(request.json.get('alumno_dni', 0))
    })

    return jsonify(str(id.inserted_id))


#APODERADOS
@app.route('/registro-a', methods=['POST'])
def crearApoderado():
    id = dbApo.insert_one({
        'DNI': int(request.json['DNI']),
        'nombre': request.json['nombre'],
        'apellido': request.json['apellido'],
        'celular': int(request.json['celular']),
        'alumno_dni': int(request.json['alumno_dni'])
    })
    
    return jsonify(str(id.inserted_id))

@app.route('/apoderados', methods=['GET'])
def obtenerApoderados():
    apoderados = [] #Se crea una lista para añadir los registros
    for doc in dbApo.find():
        apoderados.append({
            'DNI': doc['DNI'],
            'nombre': doc['nombre'],
            'apellido': doc['apellido'],
            'celular': doc['celular'],
            'alumno_dni': doc['alumno_dni']

        })
    return jsonify(apoderados)

@app.route('/apoderado/<DNI>', methods=['GET'])
def obtenerApoderado(DNI):
    apoderado = dbApo.find_one({'DNI': int(DNI)})
    print(apoderado)
    return jsonify({
        'DNI': apoderado['DNI'],
        'nombre': apoderado['nombre'],
        'apellido': apoderado['apellido'],
        'celular': apoderado['celular'],
        'alumno_dni': apoderado['alumno_dni']
    })

@app.route('/apoderados/<DNI>', methods=['DELETE'])
def borrarApoderado(DNI):
    dbApo.delete_one({'DNI': int(DNI)})
    return jsonify({'mensaje': 'Apoderado eliminado'})

@app.route('/apoderados/<DNI>', methods=['PUT'])
def actualizarApoderado(DNI):
    #Se necesita el DNI para identificar que se va actualizar y el conjunto de datos a cambiar
    dbApo.update_one({'DNI': int(DNI)}, {'$set': {
    'nombre': request.json['nombre'],
    'apellido': request.json['apellido'],
    'celular': request.json['celular'],
    'alumno_dni': request.json['alumno_dni']
    }})

    return jsonify({'mensaje': 'Apoderado actualizado'})

#CREAR SECRETARIA
@app.route('/registro-secre', methods=['POST'])
def crearSecretaria():
    id = dbSecre.insert_one({
        'cod_secretaria': int(request.json['cod_secretaria']),
        'nombre': request.json['nombre'],
        'apellido': request.json['apellido'],
        'celular': int(request.json['celular']),
        'email': request.json['email'],
        'password': request.json['password']
    })
    
    return jsonify(str(id.inserted_id))

@app.route('/secretarias', methods=['GET'])
def obtenerSecretarias():
    secretarias = [] #Se crea una lista para añadir los registros
    for doc in dbSecre.find():
        secretarias.append({
            'cod_secretaria': doc['cod_secretaria'],
            'nombre': doc['nombre'],
            'apellido': doc['apellido'],
            'celular': doc['celular'],
            'email': doc['email'],
            'password': doc['password']

        })
    return jsonify(secretarias)

@app.route('/secretaria/<CODE>', methods=['GET'])
def obtenerSecretaria(CODE):
    secretaria = dbSecre.find_one({'cod_secretaria': int(CODE)})
    print(secretaria)
    return jsonify({
        'cod_secretaria': secretaria['cod_secretaria'],
        'nombre': secretaria['nombre'],
        'apellido': secretaria['apellido'],
        'celular': secretaria['celular'],
        'email': secretaria['email'],
        'password': secretaria['password']
    })

@app.route('/secretarias/<CODE>', methods=['DELETE'])
def borrarSecretaria(CODE):
    dbSecre.delete_one({'cod_secretaria': int(CODE)})
    return jsonify({'mensaje': 'Secretaria eliminada'})

@app.route('/secretarias/<CODE>', methods=['PUT'])
def actualizarSecretaria(CODE):
    #Se necesita el DNI para identificar que se va actualizar y el conjunto de datos a cambiar
    dbSecre.update_one({'cod_secretaria': int(CODE)}, {'$set': {
    'nombre': request.json['nombre'],
    'apellido': request.json['apellido'],
    'celular': request.json['celular'],
    'email': request.json['email'],
    'password': request.json['password']
    }})

    return jsonify({'mensaje': 'Secretaria actualizada'})

#HORARIO
@app.route('/registro-h', methods=['POST'])
def registrarHorario():
    id = dbHor.insert_one({
        'tipo_horario': request.json['tipo_horario'],
        'precio': int(request.json['precio']),
        'especializacion': request.json['especializacion'], #La funcion get busca si hay un dato y si no lo encuentra reemplaza por el segundo parametro vacio
        'alumno_dni': int(request.json['alumno_dni'])
    })
    
    return jsonify(str(id.inserted_id))

#PAGOS
@app.route('/registro-p', methods=['POST'])
def registrarPago():

    cuotas = request.json.get('cuotas')
    if cuotas:
        cuotas_list = []
        for cuota in cuotas:
            cuota_dict = {
                'monto_cuota': int(cuota.get('monto_cuota')),
                'fecha_vencimiento': cuota.get('fecha_vencimiento'),
                'estado': cuota.get('estado')
            }
            cuotas_list.append(cuota_dict)
    else:
        cuotas_list = None

    id = dbPag.insert_one({
        'modo_pago': request.json['modo_pago'],
        'precio': request.json['precio'],
        'cuotas': cuotas_list,
        'fecha_pago': request.json.get('fecha_pago', None),
        'alumno_dni': int(request.json['alumno_dni'])
    })
    
    return jsonify(str(id.inserted_id))

#INFORMACION
@app.route('/guardar-info', methods=['POST'])
def guardar_info():
    data = request.json  # Obtener los datos enviados desde el frontend

    # Obtener los valores booleanos de servicios
    redes = data.get('redes', False)
    familiar = data.get('familiar', False)
    publicidad = data.get('publicidad', False)
    radio = data.get('radio', False)
    alumno = int(request.json['alumno_dni'])

    # Guardar los valores booleanos en la base de datos
    document = {
        'redes': redes,
        'familiar': familiar,
        'publicidad': publicidad,
        'radio': radio,
        'alumno_dni': alumno
    }
    result = dbInfo.insert_one(document)

    return jsonify(str(result.inserted_id))


from datetime import datetime
import pdfkit
from flask import Flask, make_response
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

#GENERAR PDF PARA ENVIAR
@app.route('/generar-pdf/<DNI>', methods=['GET'])
def generarPDF(DNI):
    alumno = dbAlum.find_one({'DNI': int(DNI)})
    dni = alumno['DNI']
    name = alumno['nombre']
    surname = alumno['apellido']
    carrera = alumno['carrera']
    direccion = alumno['direccion']
    email = alumno['email']
    colegio = alumno['colegio']
    edad = alumno['edad']

    horario = dbHor.find_one({'alumno_dni': int(DNI)})
    tipo_horario = horario['tipo_horario']
    precio = horario['precio']
    especializacion = horario['especializacion']

    pagos = dbPag.find_one({'alumno_dni': int(DNI)})
    mPago = pagos['modo_pago']

    if mPago == 'Crédito':
        cuotas = pagos['cuotas']
    else:
        cuotas = []

    apoderados = dbApo.find_one({'alumno_dni': int(DNI)})
    nameApo = apoderados['nombre']
    surnameApo = apoderados['apellido']
    phoneApo = apoderados['celular']

    descuento = dbDesc.find_one({'alumno_dni': int(DNI)})
    tipoD = descuento['tipo']
    Mdescuento = descuento['descuento']

    template = """
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Factura</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.5;
            }}

            h1, h3, h4, h5, h6 {{
                color: #333333;
            }}

            ul {{
                list-style-type: none;
                padding-left: 0;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}

            th, td {{
                border: 1px solid #dddddd;
                padding: 8px;
                text-align: left;
            }}

            th {{
                background-color: #f9f9f9;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <h1>FACTURA</h1>
        <h3>Gracias {surname}, {name} por su preferencia en esta academia. También se le enviarán sus datos al correo: {email}</h3>
        <h4>Miembro apoderado a quien acudir: {nameApo} {surnameApo}, teléfono: {phoneApo}</h4>
        <h4>Sus datos son:</h4>
        <table>
            <tr>
                <th>DNI</th>
                <td>{dni}</td>
            </tr>
            <tr>
                <th>Carrera</th>
                <td>{carrera}</td>
            </tr>
            <tr>
                <th>Colegio procedente</th>
                <td>{colegio}</td>
            </tr>
            <tr>
                <th>Dirección</th>
                <td>{direccion}</td>
            </tr>
            <tr>
                <th>Edad</th>
                <td>{edad}</td>
            </tr>
        </table>
        <h4>Usted escogió el siguiente horario: {tipo_horario}, especializado en {especializacion}</h4>
        <h4>El método de pago que se realizó es: {mPago} por el monto de {precio}</h4>
        {cuotas_section}
        <h4>Teniendo un descuento de tipo: {tipoD} que es de {Mdescuento}%</h4>
    </body>
    </html>
    """

    cuotas_section = ""
    if mPago == 'Crédito':
        cuotas_section += "<h4>Teniendo las siguientes cuotas:</h4>\n<ul>\n"
        for i, cuota in enumerate(cuotas, 1):
            cuota_monto = cuota['monto_cuota']

            if isinstance(cuota['fecha_vencimiento'], str):
                # Convertir la cadena de fecha y hora a objeto datetime
                cuota_fecha = datetime.strptime(cuota['fecha_vencimiento'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            else:
                cuota_fecha = cuota['fecha_vencimiento'].date()

            cuota_fecha = cuota_fecha.strftime("%Y-%m-%d")  # Formatear fecha sin horas

            cuotas_section += f"<li>Cuota {i}: {cuota_monto} que vence en {cuota_fecha}</li>\n"
        cuotas_section += "</ul>\n"

    html = template.format(
        surname=surname,
        name=name,
        email=email,
        nameApo=nameApo,
        surnameApo=surnameApo,
        phoneApo=phoneApo,
        dni=dni,
        carrera=carrera,
        colegio=colegio,
        direccion=direccion,
        edad=edad,
        tipo_horario=tipo_horario,
        especializacion=especializacion,
        mPago=mPago,
        precio=precio,
        cuotas_section=cuotas_section,
        tipoD=tipoD,
        Mdescuento=Mdescuento
    )

    config = pdfkit.configuration(wkhtmltopdf='C:\\Archivos de programa\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    pdf = pdfkit.from_string(html, False, configuration=config)

    if pdf:
        # Crear objeto de flujo de bytes
        pdf_output = io.BytesIO(pdf)

        # Crear diccionario adjunto con el nombre del archivo y contenido del PDF
        adjunto = {
            'nombre_archivo': f'{surname}.pdf',
            'contenido': pdf_output.getvalue()
        }

        # Llamar a la función enviarCorreo para enviar el correo electrónico con el adjunto del PDF
        destinatario = email
        asunto = 'FACTURA DE LA ACADEMIA NOBEL'
        cuerpo = 'Adjunto encontrarás la factura para continuar con tu registro.'

        enviarCorreo(destinatario, asunto, cuerpo, adjunto)

        # Devolver respuesta exitosa
        return 'Factura generada y enviada por correo electrónico.'
    else:
        return 'Error al generar el PDF'


# Función para enviar correo electrónico con adjunto
def enviarCorreo(destinatario, asunto, cuerpo, adjunto):
    remitente = 'ccortegana@unitru.edu.pe'
    password = Key

    # Crear objeto MIME multipart
    mensaje = MIMEMultipart('alternative')
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto

    # Agregar cuerpo del mensaje
    mensaje.attach(MIMEText(cuerpo, 'html'))

    # Agregar adjunto del PDF
    adjunto_mime = MIMEBase('application', 'octet-stream')
    adjunto_mime.set_payload(adjunto['contenido'])
    encoders.encode_base64(adjunto_mime)
    adjunto_mime.add_header('Content-Disposition', f"attachment; filename={adjunto['nombre_archivo']}")
    mensaje.attach(adjunto_mime)

    # Establecer conexión SMTP
    servidor_smtp = smtplib.SMTP('smtp.gmail.com', 587)
    servidor_smtp.starttls()
    servidor_smtp.login(remitente, password)

    # Enviar correo electrónico
    servidor_smtp.sendmail(remitente, destinatario, mensaje.as_string())
    servidor_smtp.quit()



from bson import ObjectId

@app.route('/datos-letras', methods=['GET'])
def datosLetras():
    tipo_horario = request.args.get('tipoHorario')
    
    pipeline = [
        {
            '$lookup': {
                'from': 'Descuento',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'descuentos'
            }
        },
        {
            '$lookup': {
                'from': 'Apoderados',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'apoderados'
            }
        },
        {
            '$lookup': {
                'from': 'Horario',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'horarios'
            }
        },
        {
            '$lookup': {
                'from': 'Pagos',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'pagos'
            }
        },
        {
            '$match': {
                'horarios.especializacion': 'Letras'
            }
        },
        {
            '$project': {
                'descuentos.constancia': 0
            }
        }
    ]

    if tipo_horario:
        pipeline[4]['$match']['horarios.tipo_horario'] = tipo_horario

    alumnos = dbAlum.aggregate(pipeline)

    # Convertir el resultado en una lista de diccionarios
    datos = list(alumnos)

    # Convertir ObjectId a cadena en los resultados
    for dato in datos:
        dato['_id'] = str(dato['_id'])
        for descuento in dato['descuentos']:
            descuento['_id'] = str(descuento['_id'])
        for apoderado in dato['apoderados']:
            apoderado['_id'] = str(apoderado['_id'])
        for horario in dato['horarios']:
            horario['_id'] = str(horario['_id'])
        for pago in dato['pagos']:
            pago['_id'] = str(pago['_id'])

    # Retornar los datos en formato JSON
    return jsonify(datos)




@app.route('/datos-medicina', methods=['GET'])
def datosMedicina():
    tipo_horario = request.args.get('tipoHorario')
    
    pipeline = [
        {
            '$lookup': {
                'from': 'Descuento',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'descuentos'
            }
        },
        {
            '$lookup': {
                'from': 'Apoderados',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'apoderados'
            }
        },
        {
            '$lookup': {
                'from': 'Horario',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'horarios'
            }
        },
        {
            '$lookup': {
                'from': 'Pagos',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'pagos'
            }
        },
        {
            '$match': {
                'horarios.especializacion': 'Medicina'
            }
        },
        {
            '$project': {
                'descuentos.constancia': 0
            }
        }
    ]

    if tipo_horario:
        pipeline[4]['$match']['horarios.tipo_horario'] = tipo_horario

    alumnos = dbAlum.aggregate(pipeline)

    # Convertir el resultado en una lista de diccionarios
    datos = list(alumnos)

    # Convertir ObjectId a cadena en los resultados
    for dato in datos:
        dato['_id'] = str(dato['_id'])
        for descuento in dato['descuentos']:
            descuento['_id'] = str(descuento['_id'])
        for apoderado in dato['apoderados']:
            apoderado['_id'] = str(apoderado['_id'])
        for horario in dato['horarios']:
            horario['_id'] = str(horario['_id'])
        for pago in dato['pagos']:
            pago['_id'] = str(pago['_id'])

    # Retornar los datos en formato JSON
    return jsonify(datos)


@app.route('/datos-ing', methods=['GET'])
def datosIng():
    tipo_horario = request.args.get('tipoHorario')
    
    pipeline = [
        {
            '$lookup': {
                'from': 'Descuento',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'descuentos'
            }
        },
        {
            '$lookup': {
                'from': 'Apoderados',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'apoderados'
            }
        },
        {
            '$lookup': {
                'from': 'Horario',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'horarios'
            }
        },
        {
            '$lookup': {
                'from': 'Pagos',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'pagos'
            }
        },
        {
            '$match': {
                'horarios.especializacion': 'Ingeniería'
            }
        },
        {
            '$project': {
                'descuentos.constancia': 0
            }
        }
    ]

    if tipo_horario:
        pipeline[4]['$match']['horarios.tipo_horario'] = tipo_horario

    alumnos = dbAlum.aggregate(pipeline)

    # Convertir el resultado en una lista de diccionarios
    datos = list(alumnos)

    # Convertir ObjectId a cadena en los resultados
    for dato in datos:
        dato['_id'] = str(dato['_id'])
        for descuento in dato['descuentos']:
            descuento['_id'] = str(descuento['_id'])
        for apoderado in dato['apoderados']:
            apoderado['_id'] = str(apoderado['_id'])
        for horario in dato['horarios']:
            horario['_id'] = str(horario['_id'])
        for pago in dato['pagos']:
            pago['_id'] = str(pago['_id'])

    # Retornar los datos en formato JSON
    return jsonify(datos)


@app.route('/eliminar-dato/<dni>', methods=['DELETE'])
def eliminarDato(dni):

    dni = int(dni)

    try:
        dbDesc.delete_one({'alumno_dni': dni})
        dbApo.delete_one({'alumno_dni': dni})
        dbHor.delete_one({'alumno_dni': dni})
        dbPag.delete_one({'alumno_dni': dni})
        dbAlum.delete_one({'DNI': dni})

        return jsonify({'message': 'Registros eliminados correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)})



from bson import ObjectId

@app.route('/buscar-dni/<dni>', methods=['GET'])
def buscar_dni(dni):

    dni = int(dni)
    print(dni)

    pipeline = [
        {
            '$match': {
                'DNI': dni
            }
        },
        {
            '$lookup': {
                'from': 'Descuento',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'descuentos'
            }
        },
        {
            '$lookup': {
                'from': 'Apoderados',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'apoderados'
            }
        },
        {
            '$lookup': {
                'from': 'Horario',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'horarios'
            }
        },
        {
            '$lookup': {
                'from': 'Pagos',
                'localField': 'DNI',
                'foreignField': 'alumno_dni',
                'as': 'pagos'
            }
        },
        {
            '$project': {
                'descuentos.constancia': 0
            }
        },
        {
            '$limit': 1  # Limitar los resultados a 1 documento
        }
    ]

    alumnos = list(dbAlum.aggregate(pipeline))
    if alumnos:
        alumno = alumnos[0]

        # Convertir ObjectId a cadenas de texto
        alumno['_id'] = str(alumno['_id'])
        for descuento in alumno['descuentos']:
            descuento['_id'] = str(descuento['_id'])
        for apoderado in alumno['apoderados']:
            apoderado['_id'] = str(apoderado['_id'])
        for horario in alumno['horarios']:
            horario['_id'] = str(horario['_id'])
        for pago in alumno['pagos']:
            pago['_id'] = str(pago['_id'])

        return jsonify(alumno)
    else:
        return jsonify({'message': 'No se encontró ningún alumno con el DNI proporcionado'})



#Iniciar este paquete cuando se llame a este archivo como módulo principal
if __name__ == "__main__":
    app.run(debug=True) #Cuando se haga un cambio el server se reinicia automáticamente