import face_recognition
from flask import Flask, jsonify, request
import numpy
import firebase_admin
from firebase_admin import credentials, firestore, messaging
import requests
import json
import os
from dotenv import load_dotenv
import massage




cred = credentials.Certificate(
    {
        "type":os.environ['type'],
        "project_id": os.environ['project_id'],
        "private_key_id": os.environ['private_key_id'],
        "private_key": os.environ['private_key'],
        "client_email": os.environ['client_email'],
        "client_id": os.environ['client_id'],
        "auth_uri": os.environ['auth_uri'],
        "token_uri": os.environ['token_uri'],
        "auth_provider_x509_cert_url": os.environ['auth_provider_x509_cert_url'],
        "client_x509_cert_url": os.environ['client_x509_cert_url'],
    }
)
firebase_admin.initialize_app(
    cred,
    {
        "projectId": os.environ['project_id'],
    },
)


db = firestore.client()


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app = Flask(__name__)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route("/finderPost", methods=["POST"])
def upload_image_finder():
    if "file" not in request.files:
        return jsonify({"massage": "you did not send file"})

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"massage": "file is empty"})

    uid = request.form["uid"]

    if file and allowed_file(file.filename):
        return finder_post(file, uid)


@app.route("/seekerPost", methods=["POST"])
def upload_image_seeker():
    if "file" not in request.files:
        return jsonify({"massage": "you did not send file"})

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"massage": "file is empty"})

    uid = request.form["uid"]

    if file and allowed_file(file.filename):
        return seeker_post(file, uid)


# someone find a person and he dont know his/her  name
def finder_post(file_stream, uid):
    # this function searching in seeker posts
    # encode the image that u take from post
    unknown_image = face_recognition.load_image_file(file_stream)
    vector_unknown = face_recognition.face_encodings(unknown_image)
    if len(vector_unknown) > 0:
        vector_unknown = vector_unknown[0]
    else:
        return jsonify({"massage":"there is no faces in the image"})
    # start comparing between this vector and the known vetcors from firestore
    result = False
    vectors_known_stream = db.collection("known_vectors")
    seekeruid = ""
    seekerToken = ""
    docName=""
    # stream all the vectors in known vector
    docs = vectors_known_stream.stream()
    for doc in docs:
        vector_known = doc.to_dict()
        # convert list into np array to deal with compare function
        vector_known_list = vector_known["vector"]
        vector_known_np = numpy.array(vector_known_list)
        result = face_recognition.compare_faces([vector_unknown], vector_known_np)[0]
        if result == True:
            docName=doc
            seekeruid = vector_known["uid"]
            break
    vector_unknown_list = vector_unknown.tolist()
    if result == True:
        profiles_stream = db.collection("users")
        docs = profiles_stream.stream()
        for doc in docs:
            data = doc.to_dict()
            if data["uid"] == uid:
                finderToken = data["token"]
                break
        docs = profiles_stream.stream()
        for doc in docs:
            data = doc.to_dict()
            if data["uid"] == seekeruid:
                seekerToken = data["token"]
                break
        result_ref = db.collection("results").document()
        result_ref.set(
            {
                "uid_finder": uid,
                "uid_seeker": seekeruid,
                "result": True,
                "known_vector": vector_known_list,
                "unknown_vector": vector_unknown_list,
                "findertoken":finderToken,
                "seekertoken":seekerToken
            }
        )
        massageefinder="we happy to say that we found one you are searching for  for you 😊"
        massageeseeker="we happy to say that we know the name of person you found 😊"
        body= massage.createBody(finderToken, massageefinder,title="founded")
        response=massage.massaging(body)
        body= massage.createBody(seekerToken, massageeseeker,title="founded")
        response=massage.massaging(body)
        docName.reference.delete()
        return jsonify({"result": True,"finderID": uid,"seekerID":seekeruid})

    else:
        # if there is no known_vector that same as unknown so upload this vector so we can use it again
        # convert np array vector to list to upload to firestore
        doc_ref = db.collection("unknown_vectors").document(uid)
        doc_ref.set({"uid": uid, "vector": vector_unknown_list})
        return jsonify({"result": False})


# someone search for person and he know his/her name
def seeker_post(file_stream, uid):
    known_image = face_recognition.load_image_file(file_stream)
    vector_known = face_recognition.face_encodings(known_image)
    if len(vector_known) > 0:
        vector_known = vector_known[0]
    else:
        return jsonify({"massage":"there is no faces in the image"})
    result = False
    finderuid = ""
    finderToken = ""
    docName=""
    vectors_unknown_stream = db.collection("unknown_vectors")
    docs = vectors_unknown_stream.stream()
    for doc in docs:
        vector_unknown = doc.to_dict()
        vector_unknown_list = vector_unknown["vector"]
        vector_unknown_np = numpy.array(vector_unknown_list)
        result = face_recognition.compare_faces([vector_known], vector_unknown_np)[0]
        if result == True:
            docName=doc
            finderuid = vector_unknown["uid"]
            break
    vector_known_list = vector_known.tolist()
    if result == True:
        profiles_stream = db.collection("users")
        docs = profiles_stream.stream()
        for doc in docs:
            data = doc.to_dict()
            if data["uid"] == uid:
                seekerToken = data["token"]
                break
        docs = profiles_stream.stream()
        for doc in docs:
            data = doc.to_dict()
            if data["uid"] == finderuid:
                finderToken = data["token"]
                break
        result_ref = db.collection("results").document()
        result_ref.set(
            {
                "uid_finder": finderuid,
                "uid_seeker": uid,
                "result": True,
                "known_vector": vector_known_list,
                "unknown_vector": vector_unknown_list,
                "findertoken":finderToken,
                "seekertoken":seekerToken
            }
        )
        massageefinder="we happy to say that we found one you are searching for  for you 😊"
        massageeseeker="we happy to say that we know the name of person you found 😊"
        body= massage.createBody(finderToken, massageefinder,title="founded")
        response=massage.massaging(body)
        body= massage.createBody(seekerToken, massageeseeker,title="founded")
        response=massage.massaging(body)
        docName.reference.delete()
        return jsonify({"result": True,"finderID":finderuid,"seekerID":uid})
    else:
        doc_ref = db.collection("known_vectors").document(uid)
        doc_ref.set({"uid": uid, "vector": vector_known_list})
        return jsonify({"massage": False})

@app.route("/likes", methods=["POST"])
def put_likes_infire():
    userName=request.form['userName']
    id=request.form['id']#id for the person who created the post
    return likes(id,userName)

def likes(ID,userName):
    profiles_stream = db.collection("users")
    docs = profiles_stream.stream()
    for doc in docs:
        data = doc.to_dict()
        if data["uid"] == ID:
            deviceToken=data['token']
            massagee=userName+" liked your post"
            body=massage.createBody(deviceToken,massagee,title="someone liked your post")
            response=massage.massaging(body)
            data={userName : massagee}
            db.collection('users').document(ID).collection('notification').document().set(data)
            break
    return jsonify({'mass':response})
@app.route("/comment", methods=["POST"])
def WrittenComment():
    userName=request.form['userName']
    comment=request.form['comment']
    id=request.form['id']#id for the person who created the post
    return write_comment(userName,comment,id)
def write_comment(userName,comment,id):
    profiles_stream = db.collection("users")
    docs = profiles_stream.stream()
    for doc in docs:
        data = doc.to_dict()
        if data["uid"] == id:
            deviceToken=data['token']
            massagee=comment
            body=massage.createBody(deviceToken,massagee,title=userName+" comment in your post")
            response=massage.massaging(body)
            data={userName : massagee}
            db.collection('users').document(id).collection('notification').document().set(data)
            break
    return jsonify({'mass':response})



if __name__ == "__main__":
    load_dotenv()
    app.run(debug=True)
