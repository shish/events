import os
from flask import (
    Flask,
)

app = Flask(__name__, instance_path=os.path.abspath("./data"))
