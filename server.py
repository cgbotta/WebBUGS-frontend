from flask import Flask, flash, render_template, request, redirect
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
from mermaid_to_bugs import translate_v2, clear_all_data, translate_data
from os import getcwd
app = Flask(__name__)
app.secret_key = "3d6f45a5fc12445dbac2f59c3b6c7cb1"

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/markbugs_to_bugs/', methods=["POST"])
def my_link():
  clear_all_data()
  user_input = request.form["markbugs_code"]
  user_data = request.form["data_input"]

  # Handle errors version 

  # bugs_code = None
  # try:
  #   bugs_code = translate_v2(user_input)
  # except Exception as e:
  #   flash("Error: " + str(e))
  # if bugs_code is not None:
  #   return render_template("index.html", INPUT_NAME_1 = bugs_code, INPUT_NAME_2 = user_input, INPUT_NAME_3 = user_data)  
  # else:
  #   return render_template("index.html", INPUT_NAME_2 = user_input, INPUT_NAME_3 = user_data)  
  # mermaid_code = generate_mermaid()

  # Display errors version 
  bugs_code = translate_v2(user_input)
  bugs_data = translate_data(user_data)
  return render_template("index.html", INPUT_NAME_1 = bugs_code, INPUT_NAME_2 = user_input, INPUT_NAME_3 = user_data, INPUT_NAME_4 = bugs_data)  

@app.route('/aws/', methods=["POST"])
def aws():
  r = None
  try:
    r = session.get('https://flask-service.a4b97h85mfgc0.us-east-2.cs.amazonlightsail.com/')
    # dict = r.json()
  except Exception as e:
    print("error: ", e)
  return render_template("index.html", INPUT_NAME_2 = r.text)

@app.route('/clear_data/', methods=["POST"])
def clear_data():
  clear_all_data()
  return redirect('/')

@app.route('/example/<id>')
def get_example(id):
  clear_all_data()
  code_file_contents = ""
  try:
    code_file = open(f'./examples/example_{id}.txt', 'r')
    code_file_contents = code_file.read()
  except Exception as e:
    print("error: ", e)

  data_file_contents = ""
  try:
    data_file = open(f'./examples/example_{id}_data.txt', 'r')
    data_file_contents = data_file.read()
  except Exception as e:
    print("error: ", e)
  
  if data_file_contents != "":
    return render_template("index.html", INPUT_NAME_2 = code_file_contents, INPUT_NAME_3 = data_file_contents)
  return render_template("index.html", INPUT_NAME_2 = code_file_contents)


if __name__ == '__main__':
  app.run(debug=True)