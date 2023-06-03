from flask import Flask, flash, render_template, request, redirect
from mermaid_to_bugs import translate_v2, clear_all_data
from os import getcwd
app = Flask(__name__)
app.secret_key = "3d6f45a5fc12445dbac2f59c3b6c7cb1"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/markbugs_to_bugs/', methods=["POST"])
def my_link():
  clear_all_data()
  user_input = request.form["markbugs_code"]

  # Handle errors version 

  # bugs_code = None
  # try:
  #   bugs_code = translate_v2(user_input)
  # except Exception as e:
  #   flash("Error: " + str(e))
  # if bugs_code is not None:
  #   return render_template("index.html", INPUT_NAME_1 = bugs_code, INPUT_NAME_2 = user_input)  
  # else:
  #   return render_template("index.html", INPUT_NAME_2 = user_input)  
  # mermaid_code = generate_mermaid()

  # Display errors version 
  bugs_code = translate_v2(user_input)
  return render_template("index.html", INPUT_NAME_1 = bugs_code, INPUT_NAME_2 = user_input)  

@app.route('/clear_data/', methods=["POST"])
def clear():
  clear_all_data()
  return redirect('/')

@app.route('/example/<id>')
def get_example(id):
  clear_all_data()
  file_contents = ""
  try:
    print(id)
    print(getcwd())
    f = open(f'./examples/study_example_{id}.txt', 'r')
    file_contents = f.read()
  except Exception as e:
    print("error: ", e)
  return render_template("index.html", INPUT_NAME_2 = file_contents)


if __name__ == '__main__':
  app.run(debug=True)