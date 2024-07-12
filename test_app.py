from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask is running on port 8085!"

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8085, ssl_context=('/home/admin/conf/web/web3jobs.online/ssl/web3jobs.online.pem', '/home/admin/conf/web/web3jobs.online/ssl/web3jobs.online.key'))
