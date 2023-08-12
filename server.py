from flask import Flask, flash, render_template, request, redirect, send_from_directory
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
from mermaid_to_bugs import translate_v2, clear_all_data, translate_data
from os import getcwd
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import bs4
import os

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


@app.route('/graphs_page')
def graphs_page():
    return render_template('graphs_page.html')

# @app.after_request
# def add_header(response):
#     response.cache_control.max_age = 10
#     response.no_cache = True
#     return response

# @app.route('/static/<path:path>')
# def serve_static(path):
#     return send_from_directory('static', path)



@app.route('/graphs/', methods=["POST"])
def graphs():
  user_input = request.form["markbugs_code"]
  user_data = request.form["data_input"]
  inits_input = request.form["inits_input"]
  monitors_input = request.form["monitors_input"]
  feedback = request.form["feedback"]

  if os.path.isfile("./templates/graphs_page.html"):
    os.remove("./templates/graphs_page.html")
  with open("./templates/graphs_page.html", "w") as outf:
      soup = bs4.BeautifulSoup()
      dir = "static/images"
      if os.path.exists(dir):
        for f in os.listdir(dir):
          new_img = soup.new_tag("img", src="/static/images/" + f)
          soup.append(new_img)
      # print("updated_soup", soup)

      
      outf.write(bs4.BeautifulSoup.prettify(soup))

  return render_template("index.html", BUGS_CODE = user_input, DATA_INPUT = user_data,  INITS_INPUT = inits_input,  MONITORS_INPUT = monitors_input, FEEDBACK = feedback)


@app.route('/compile/', methods=["POST"])
def my_link():
  clear_all_data()
  user_input = request.form["markbugs_code"]
  user_data = request.form["data_input"]
  inits_input = request.form["inits_input"]
  monitors_input = request.form["monitors_input"]

  num_lines = len(user_input.splitlines())
  r = None
  feedback = ""
  try:
    r = requests.get(url='https://flask-service.a4b97h85mfgc0.us-east-2.cs.amazonlightsail.com/compile/', data ={'user_input':user_input, 'data_input':user_data, 'inits_input':inits_input, 'monitors_input':monitors_input})
    # r = requests.get(url='http://127.0.0.1:3000/compile/', data ={'user_input':user_input, 'data_input':user_data, 'inits_input':inits_input, 'monitors_input':monitors_input})
    body = r.json()
    feedback = body["logs"]
    data = body['data']
    # print(data)
    print(len(data))
    sub = 'line ' + str(num_lines + 1)
    if sub in feedback:
      feedback = feedback + 'You may need to add a closing bracket to your model\n------\nmodel{\n.\n}'

    # Need to extract individual data from response

    # Plotting

    # ax1 = plt.plot(range(10000), data[0][1], 'o')
    # ax2 = plt.plot(range(10000), data[1][1], 'o')
    # ax3 = plt.plot(range(10000), data[2][1], 'o')
    # x = range(10000)
    images = []
    for d in data:
      plt.figure()
      plt.xlabel('value')
      plt.ylabel("samples")
      plt.title(d[0])
      # plt.hist(d[1], bins=20)
      plt.plot(range(len(d[1])), d[1])
      filename = "./static/images/output_" + d[0] + ".jpg"
      plt.savefig(filename)
      plt.close()
      images.append("https://cgb45.pythonanywhere.com/static/images/output_" + d[0] + ".jpg")
      # images.append("http://127.0.0.1:8080/static/images/output_" + d[0] + ".jpg")


    # x = range(10000)
    # y = data[1][1]

    # fig = plt.figure()
    # plt.xlim(0, 10000)
    # plt.ylim(0, 10)
    # graph, = plt.plot([], [], 'o')

    # def animate(i):
    #     graph.set_data(x[:i+1], y[:i+1])
    #     return graph

    # ani = FuncAnimation(fig, animate, frames=10000, interval=20)
    # plt.show()

    

    # Saving the figure.
    # plt.savefig("./static/output.jpg")
    # ani.save("./static/TLI.gif", dpi=300, writer=PillowWriter(fps=1))


    plt.clf()

    # load the file
    # if os.path.isfile("./templates/graphs_page.html"):
    #   os.remove("./templates/graphs_page.html")
    # with open("./templates/graphs_page.html", "w") as outf:
    #   # create new images
    #   soup = bs4.BeautifulSoup()
    #   for d in data:
    #     new_img = soup.new_tag("img", src="/static/images/output_" + d[0] + ".jpg")
    #     # print("new_img", new_img)

    #     # insert it into the document
    #     soup.append(new_img)
    #   # print("updated_soup", soup)

    #   outf.write(bs4.BeautifulSoup.prettify(soup))

  except Exception as e:
    print("error: ", e)
  # return redirect("/")



  if len(images) == 0:
    return render_template("index.html", BUGS_CODE = user_input, DATA_INPUT = user_data,  INITS_INPUT = inits_input,  MONITORS_INPUT = monitors_input, FEEDBACK = feedback)
  elif len(images) == 1:
    return render_template("index.html", BUGS_CODE = user_input, DATA_INPUT = user_data,  INITS_INPUT = inits_input,  MONITORS_INPUT = monitors_input, FEEDBACK = feedback, IMAGE1 = images[0])
  elif len(images) == 2:
    return render_template("index.html", BUGS_CODE = user_input, DATA_INPUT = user_data,  INITS_INPUT = inits_input,  MONITORS_INPUT = monitors_input, FEEDBACK = feedback, IMAGE1 = images[0], IMAGE2 = images[1])
  elif len(images) == 3:
    return render_template("index.html", BUGS_CODE = user_input, DATA_INPUT = user_data,  INITS_INPUT = inits_input,  MONITORS_INPUT = monitors_input, FEEDBACK = feedback, IMAGE1 = images[0], IMAGE2 = images[1], IMAGE3 = images[2])
  elif len(images) == 4:
    return render_template("index.html", BUGS_CODE = user_input, DATA_INPUT = user_data,  INITS_INPUT = inits_input,  MONITORS_INPUT = monitors_input, FEEDBACK = feedback, IMAGE1 = images[0], IMAGE2 = images[1], IMAGE3 = images[2], IMAGE4 = images[3])
  else:
    return render_template("index.html", BUGS_CODE = user_input, DATA_INPUT = user_data,  INITS_INPUT = inits_input,  MONITORS_INPUT = monitors_input, FEEDBACK = feedback, IMAGE1 = images[0], IMAGE2 = images[1], IMAGE3 = images[2], IMAGE4 = images[3])

  # Handle errors version 

  # bugs_code = None
  # try:
  #   bugs_code = translate_v2(user_input)
  # except Exception as e:
  #   flash("Error: " + str(e))
  # if bugs_code is not None:
  #   return render_template("index.html", BUGS_CODE_TEXTBOX = bugs_code, BUGS_CODE = user_input, DATA_INPUT = user_data)  
  # else:
  #   return render_template("index.html", BUGS_CODE = user_input, DATA_INPUT = user_data)  
  # mermaid_code = generate_mermaid()

  # Display errors version 
  bugs_code = translate_v2(user_input)
  bugs_data = translate_data(user_data)
  return render_template("index.html", BUGS_CODE_TEXTBOX = bugs_code, BUGS_CODE = user_input, DATA_INPUT = user_data, BUGS_DATA_TEXTBOX = bugs_data)  

@app.route('/aws/', methods=["POST"])
def aws():
  r = None
  dict = {}
  try:
    # r = session.get('https://flask-service.a4b97h85mfgc0.us-east-2.cs.amazonlightsail.com/please')
    r = session.get('http://127.0.0.1:3000/please')

  except Exception as e:
    print("error: ", e)
  return render_template("index.html", BUGS_CODE = r.text)

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

  inits_file_contents = ""
  try:
    inits_file = open(f'./examples/example_{id}_inits.txt', 'r')
    inits_file_contents = inits_file.read()
  except Exception as e:
    print("error: ", e)

  monitors_file_contents = ""
  try:
    monitors_file = open(f'./examples/example_{id}_monitors.txt', 'r')
    monitors_file_contents = monitors_file.read()
  except Exception as e:
    print("error: ", e)
  
  return render_template("index.html", BUGS_CODE = code_file_contents, DATA_INPUT = data_file_contents, MONITORS_INPUT = monitors_file_contents, INITS_INPUT = inits_file_contents)


if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=8080)