import os
from flask import Flask, request, redirect, url_for, make_response, jsonify, send_file
from werkzeug.utils import secure_filename
import logging
import subprocess
import time
import tempfile

UPLOAD_FOLDER = "/tmp"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'ppt', 'pptx' ,'xls', 'xlsx', 'doc', 'docx', 'odt', 'avi', 'ogg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True

def allowed_file(filename):
    return os.path.splitext(filename)[-1].replace('.','') in ALLOWED_EXTENSIONS
    
#######################################

import base64
import atexit
from thumbnailer import create_thumbnail


def get_thumbnail(src_path):
    return create_thumbnail(src_path, output_format='png')    

#######################################

@app.route('/', methods=['GET', 'POST'])
def upload_file():

    # POST request
    if request.method == 'POST':
        
        if request.files.get('file', None) is None:
            msg = "Bad request: 'files' was found in request"            
            resp = make_response(msg, 400)
            return resp

        ufile = request.files.get('file', None)
        
        if ufile and allowed_file(ufile.filename):
            filename = secure_filename(ufile.filename)
            dest_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            ufile.save(dest_path)

            ### Generate Thumbnail ###
            errors = {}

            if request.form.get('thumbnail',"no").lower() == "yes":
                size_str = request.form.get('thumbnail_size',"300x300")
                size = map(int, size_str.split("x"))
                try:
                    thumb_file = get_thumbnail(dest_path)
                except Exception as e:
                    errors['thumbnail'] = str(e)

            if request.form.get('save_orig',"no") == "no":
                os.unlink(dest_path)

            msg = {}
            if len(errors):
                code = 501
                msg['errors'] = errors
                resp = make_response(jsonify(msg), code)
                resp.headers['Content-type'] = "application/json"
                return resp
            else:
                return send_file(thumb_file, attachment_filename="thumbnail.png", as_attachment=True)
                #response = make_response(thumb_file)
                #response.headers['Content-Type'] = 'image/png'
                #response.headers['Content-Disposition'] = "attachment; filename=thumbnail.png"
                #return response

        else:
            msg = "Invalid file: '%s', supported types: %s" % (ufile.filename, ','.join(list(ALLOWED_EXTENSIONS)))
            resp = make_response(msg, 400)
            return resp

    # GET request
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
         <input type=hidden name="thumbnail" value="yes">
         <input type=hidden name="thumbnail_size" value="500x500"
    </form>
    '''

#######################################


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
