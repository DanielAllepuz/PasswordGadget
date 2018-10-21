from flask import Flask
from flask import render_template, request, session, url_for, jsonify

import json
import datetime
import gadgetlib

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='<%',
        block_end_string='%>',
        variable_start_string='%%',
        variable_end_string='%%',
        comment_start_string='<#',
        comment_end_string='#>',
    ))

app = CustomFlask(__name__)

with open('data.json') as f:
    pass_dict_list = json.load(f)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def hello():
    return render_template('home.html', pass_dict_list = json.dumps(pass_dict_list))

@app.route('/edit_password_page')
def edit_password_page():
    return render_template('edit_form.html')

@app.route('/new_password_page')
def new_password_page():
    return render_template('new_form.html')

@app.route('/new_password')
def new_password():
    pass_dict = dict()
    pass_dict["name"]=request.args.get("name", "NOT_FOUND")
    pass_dict["link"]=request.args.get("link", "NOT_FOUND")
    pass_dict["lastUpdate"]=datetime.datetime.today().strftime('%Y/%m/%d')
    pass_dict["password"]=request.args.get("password", "NOT_FOUND")

    pass_dict_list.append(pass_dict)
    saveToLocalFile()

    return jsonify({"result": "true"})

@app.route('/edit_password')
def edit_password():
    found = False
    oldName = request.args.get("oldName")
    for i in range(len(pass_dict_list)):
        if pass_dict_list[i]["name"] == oldName:
            pass_dict_list[i]["name"]= request.args.get("name", pass_dict_list[i]["name"])
            pass_dict_list[i]["link"]= request.args.get("link", pass_dict_list[i]["link"])
            pass_dict_list[i]["lastUpdate"]= request.args.get("lastUpdate", pass_dict_list[i]["link"])
            pass_dict_list[i]["password"]= request.args.get("password", pass_dict_list[i]["password"])
            found = True
            break
    if found:
        saveToLocalFile()
        return jsonify({"result": "true"})
    else:
        return jsonify({"result": "false"})

@app.route('/delete_password')
def delete_password():
    name = request.args.get("name")
    print(name)
    found = False
    for i in range(len(pass_dict_list)):
        if pass_dict_list[i]["name"] == name:
            pass_dict_list.pop(i)
            found = True
            break
    if found:
        saveToLocalFile()
        return jsonify({"result": "true"})
    else:
        return jsonify({"result": "false"})



@app.route('/get_password_list')
def getPasswordList():
    return jsonify(pass_dict_list)

def saveToLocalFile():
    """
    Saves passwords locally
    """
    with open('data.json', 'w') as f:
        json.dump(pass_dict_list, f)

@app.route('/save_to_arduino')
def saveToArduino():
    """
    Transfers passwords to the arduino
    """
    ardu = gadgetlib.Arduino()
    gadgetlib.fill_with_empty(ardu)
    for i, pass_dict in enumerate(pass_dict_list):
        gadgetlib.send_password(ardu, i, pass_dict["name"], pass_dict["password"])
    gadgetlib.exit_serial_mode(ardu)
    return "done"
