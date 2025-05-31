import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return ("My name is Rustem and I'm Python developer! \n"
            "Hello from Page Analyzer!")
