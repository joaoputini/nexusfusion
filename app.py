from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    'host': '172.20.28.219',
    'user': 'root',
    'password': '01052003',
    'database': 'monitoramento'
}

dados_recebidos = {}

@app.route('/')
def home():
    return "Servidor Flask rodando! Use as rotas /sensores (GET, POST) e /login (POST)."

@app.route('/sensores', methods=['POST'])
def receber_dados():
    global dados_recebidos
    try:
        dados_recebidos = request.get_json()
        print("Dados recebidos:", dados_recebidos)

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = """
                INSERT INTO sensores (mq135_analog_value, mq135_analog_voltage, mq131_analog_value, mq131_analog_voltage)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (
                dados_recebidos.get('mq135_analog_value'),
                dados_recebidos.get('mq135_analog_voltage'),
                dados_recebidos.get('mq131_analog_value'),
                dados_recebidos.get('mq131_analog_voltage')
            ))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as db_err:
            print("Erro ao inserir no banco de dados:", db_err)

        return jsonify({"message": "Dados recebidos com sucesso"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/sensores', methods=['GET'])
def retornar_dados():
    if dados_recebidos:
        return jsonify(dados_recebidos), 200
    else:
        return jsonify({"message": "Nenhum dado recebido ainda"}), 404

@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    usuario = dados.get('user')
    senha = dados.get('password')

    if not usuario or not senha:
        return jsonify({"message": "Usuário ou senha não informados"}), 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM usuarios WHERE usuario = %s AND senha = %s"
        cursor.execute(query, (usuario, senha))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()

        if resultado:
            return jsonify({
                "message": "Login realizado com sucesso",
                "usuario": resultado["usuario"],  
            }), 200
        else:
            return jsonify({"message": "Usuário ou senha inválidos"}), 401
    except Exception as e:
        print("Erro no login:", e)
        return jsonify({"message": "Erro interno no servidor"}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
