from flask import Flask
from flask import request
import sqlalchemy
import json
import requests

app = Flask(__name__)

@app.route('/api/parameters/<user>/<name>/<type>', methods = ['POST'])
def set_param(user, name, type):
    value = request.form.get('value')

    try:
        value = int(value)
    except:
        pass

    engine = sqlalchemy.create_engine('sqlite:///db.db')
    con = engine.connect()
    user_ids = con.execute("SELECT id FROM user WHERE name = '{}'".format(user))
    user_id = -1

    for row in user_ids:
        user_id = row[0]

    if (user_id == -1):
        return "ERROR", 400
    elif ((isinstance(value, int) and type != 'int') or (isinstance(value, str) and type != 'str')):
        return "ERROR", 400
    else:

        try:
            con.execute("INSERT INTO param (id_user, name, type, value) VALUES ({}, '{}', '{}', '{}')".format(user_id, name, type, value))
            return "OK", 200
        except:
            con.execute("UPDATE param SET value = '{}' WHERE id_user = {} AND name = '{}' AND type = '{}'".format(value, user_id, name, type))
            return "OK", 200

@app.route('/api/parameters/<user>', methods = ['POST'])
def set_params(user):
    json_data = request.json
    result = {"Result": []}

    for i in json_data['Query']:
        url = 'http://127.0.0.1:5000/api/parameters/{}/{}/{}'.format(user, i['Name'], i['Type'])
        my_data = {'value': i['Value']}
        req = requests.post(url, data = my_data)

        if (req.status_code == 200):
            result["Result"].append({"Operation": "SetParam", "Name": i['Name'], "Type": i['Type'], "Status": "OK"})
        else:
            result["Result"].append({"Operation": "SetParam", "Name": i['Name'], "Type": i['Type'], "Status": "ERROR"})
        
    response = app.response_class(
        response = json.dumps(result),
        status = 200,
        mimetype = 'application/json'
    )

    return response

@app.route('/api/parameters/<user>/<name>/<type>', methods = ['GET'])
@app.route('/api/parameters/<user>/<name>', defaults={'type': 'all'}, methods = ['GET'])
def get_param(user, name, type):
    engine = sqlalchemy.create_engine('sqlite:///db.db')
    con = engine.connect()
    user_ids = con.execute("SELECT id FROM user WHERE name = '{}'".format(user))
    user_id = -1

    for row in user_ids:
        user_id = row[0]

    if (user_id == -1):
        return "ERROR", 400
    else:
        value = []
        types = []

        if type != 'all':
            values = con.execute("SELECT value, type FROM param WHERE id_user = {} AND name = '{}' AND type = '{}'".format(user_id, name, type))
        else:
            values = con.execute("SELECT value, type FROM param WHERE id_user = {} AND name = '{}'".format(user_id, name))

        for i in values:
            value.append(i[0])
            types.append(i[1])

        data = []
        count = 0

        if (len(value) != 0):
            for j in value:
                data.append({'name': name, 'type': types[count], 'value': str(j)})
                count += 1

        response = app.response_class(
            response = json.dumps(data),
            status = 200,
            mimetype = 'application/json'
        )

        return response

@app.route('/api/parameters/<user>', methods = ['GET'])
def get_params(user):
    engine = sqlalchemy.create_engine('sqlite:///db.db')
    con = engine.connect()
    user_ids = con.execute("SELECT id FROM user WHERE name = '{}'".format(user))
    user_id = -1

    for row in user_ids:
        user_id = row[0]

    if (user_id == -1):
        return "ERROR", 400
    else:
        values = con.execute("SELECT name, type, value FROM param WHERE id_user = {}".format(user_id))

        name = []
        types = []
        value = []

        for i in values:
            name.append(i[0])
            types.append(i[1])
            value.append(i[2])

        data = []
        count = 0

        if (len(value) != 0):
            for j in name:
                data.append({'name': j, 'type': types[count], 'value': str(value[count])})
                count += 1

        response = app.response_class(
            response = json.dumps(data),
            status = 200,
            mimetype = 'application/json'
        )

        return response