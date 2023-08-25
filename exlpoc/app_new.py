from flask import Flask, request, jsonify, render_template
import os
from flask_cors import CORS
import glob
import pandas as pd
import PyPDF2, textract
import openpyxl
from docx2python import docx2python

from langchain.document_loaders import Docx2txtLoader, PyPDFLoader, CSVLoader, UnstructuredExcelLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import CharacterTextSplitter

app = Flask(__name__)
CORS(app)

os.environ["PORT"] = "5000"
landing = os.environ["landing_path"]

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    uploaded_files = request.files.getlist("file")
    print(uploaded_files)
    for file in uploaded_files:
        print("Saving File " + file.filename)
        file.save(landing + file.filename)
    processFiles(uploaded_files)
    print("Files Uploaded")
    files = glob.glob(landing + "*")
    for filename in files:
        os.unlink(filename)
    return jsonify({"result": "Files Uploaded Successfully !"})


def processFiles(uploaded_files):
    documents = ""
    for file in os.listdir(landing):
        print(file)
        extnsn = file.split(".")[1]
        print(extnsn)
        if extnsn == "pdf":
            loader = PyPDFLoader(landing+file)
            documents = loader.load()
        elif extnsn == "txt":
            loader = TextLoader(landing+file)
            documents = loader.load()
        elif extnsn in ("docx", "doc"):
            loader = Docx2txtLoader(landing+file)
            documents = loader.load()
        elif extnsn == "csv":
            loader = CSVLoader(file_path=landing+file)
            documents = loader.load()
        elif extnsn in ("xlsx", "xls"):
            loader = UnstructuredExcelLoader(landing+file, mode="elements")
            documents = loader.load()
    print("Loading files from MyDrive")
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
    print("Splitting Files into Chunks")
    docs = text_splitter.split_documents(documents)
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")  # all-MiniLM-L6-v2
    print("Storing Embeddings into Vector DB")
    global vectorDB
    vectorDB = FAISS.from_documents(docs, embedding_function)
    print("Embeddings stored in vectorDB")


@app.route("/askQuestion", methods=["POST"])
def askQuestions():
    vectordb = vectorDB
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    pdf_qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0), chain_type="stuff", retriever=vectordb.as_retriever(), memory=memory, max_tokens_limit=4000,)
    req_data = request.get_json()
    questions = req_data["questions"]
    result = pdf_qa({"question": questions})
    # res = {"Answer":result["answer"]}
    my_string = result["answer"]
    print(my_string)
    return jsonify({"answer": my_string})


if __name__ == "__main__":
    port = int(os.environ["PORT"])
    app.run(debug=True, host="0.0.0.0", port=port)