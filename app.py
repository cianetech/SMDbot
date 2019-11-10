from flask import Flask, render_template, request
from datetime import datetime
from database import Database
from config import CONFIDENCE
from bot import Bot
import threading

app = Flask(__name__, template_folder="docs") #static_folder="static"
db = Database()
smd_bot = Bot()


@app.route("/")
def status():
    status = "\
    <br><br> PostgreSQL Database Connection: <strong>" + db.status_connection() + "</strong>\
    <br><br> Bot Status: <strong>" + smd_bot.status + "</strong>\
    "
    return "<strong> SERVER ONLINE </strong>" + str( datetime.now().strftime("%d/%m/%Y %H:%M") ) + status  , 200

@app.route("/test")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    text = request.args.get('msg')
    response = smd_bot.current_bot.get_response(text)

    if float(response.confidence) > CONFIDENCE:
        return str(response)
    else:
        return 'Ainda não sei responder esta pergunta'



def run_bot():
    try:
        print("-- START BOT -- ")
        db.open_connection()
        data = db.get_data() #db.get_example_data()
        db.close_connection()

        if(data is None):
            print("Error: Data None")
        else:
            smd_bot.start_chatterBot(data)

    except Exception as e:
        print(' * * * * * Error: '+ str(e))


t = threading.Thread(target = run_bot)
t.start()
#run_bot()
app.run(port=5000)
