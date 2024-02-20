import os
from flask import Flask, Response, request
from dotenv import load_dotenv
from flask_cors import CORS
from chains.holdings import Holdings
from dotenv import dotenv_values


load_dotenv()

kernels = {}
app = Flask(__name__, static_folder="static")

CORS(app)
CORS(app, resources={r"/api/*": {"origins": ["*"]}})


cfg = dotenv_values()
AZURE_OPENAI_API_KEY = cfg["AZURE_OPENAI_API_KEY"]
os.environ["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY


def initialize_chat_index():

    global holdings_chain
    holdings_chain = Holdings().get_chain()

def langchain_stream(response):
    for line in response:
        yield line.content


   
@app.route("/holdings-chat", methods=["POST"])
def holdings_chat():

    global holdings_chain
    request_messages = request.json["messages"]

    question = request_messages[-1]["content"]

    response = holdings_chain.stream({"question": question,"chat_history":request_messages[-11:0]})

    if request.method == "POST":
        return Response(langchain_stream(response), mimetype='text/event-stream')
    else:
        return Response(None, mimetype='text/event-stream')
    
initialize_chat_index()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)