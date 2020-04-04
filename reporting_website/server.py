from flask import Flask, request
app = Flask(__name__, static_url_path='')

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/mkl')
def mkl():
    return app.send_static_file('reports/mkl.json')

@app.route('/info')
def info():
    return app.send_static_file('reports/info.json')

@app.route('/report')
def report():
    return app.send_static_file('reports/report.json')

if __name__ == '__main__':
  app.run(debug=True)