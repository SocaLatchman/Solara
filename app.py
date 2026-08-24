from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
@app.route('/login')
def index():
   return render_template('login.html', title='Welcome back')



if __name__ == '__main__':
   app.run(debug=True)