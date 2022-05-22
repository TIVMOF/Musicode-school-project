from flask import Flask, redirect, render_template, url_for, request, send_file, session
from werkzeug.utils import secure_filename
from glob import glob
from io import BytesIO
from zipfile import ZipFile
import os
from encryption_and_decryption import Want_to_crypt
from cryptography.fernet import Fernet

list_of_extensions = ['.mp3', '.key', '.ape', '.wv', '.m4a', '.3gp', '.aa', '.aac', '.aax', 
                                  '.act', '.aiff', '.alac', '.amr', '.au', '.awb', '.dss', '.dvf',
                                  '.flac', '.gsm', '.iklax', '.ivs', '.m4b', '.m4p', '.mmf', '.mpc',
                                  '.msv', '.nmf', '.oga', '.ogg', '.mogg', '.opus', '.ra',
                                  '.rm', '.raw', '.rf64', '.sln', '.tta', '.voc', '.vox', '.wav',
                                  '.wma', '.webm', '.8svx', '.cda']

app = Flask(__name__)

app.secret_key = Fernet.generate_key()

app.config['AUDIO_UPLOAD'] = 'C:\\Users\\PC\\Musicode\\static\\tmp'

@app.route("/", methods = ['POST', "GET"])
def code_page():    
    if request.method == "POST":
        audio = request.files['file']
        
        if audio.filename == '':
            print("File name is invalid!")
            return redirect(request.url)
        
        session['filename'] = secure_filename(audio.filename)
        
        basedir = os.path.abspath(os.path.dirname(__file__))
        
        audio.save(os.path.join(basedir, app.config['AUDIO_UPLOAD'], session['filename']))
        
        file = Want_to_crypt(session['filename'])
        
        file.encrypt(app.config['AUDIO_UPLOAD'])
        
        session['filename_new'] = file.new_name(1)
        
        session['file_key'] = 'key_' + session['filename'] + '.key'
    
    return render_template('Musicode_code_page.html')


@app.route("/decrypt", methods = ['POST', "GET"])
def decode_page():
    if request.method == "POST":
        zip = request.files['file']
        
        if zip.filename == '':
            print("File name is invalid!")
            return redirect(request.url)
        
        zip_name = secure_filename(zip.filename)
        
        basedir = os.path.abspath(os.path.dirname(__file__))
        
        zip.save(os.path.join(basedir, app.config['AUDIO_UPLOAD'], zip_name))
        
        session['filename_d'] = ''
        session['file_key_d'] = ''
        
        with ZipFile(os.path.join(app.config['AUDIO_UPLOAD'], zip_name), 'r') as zip:
            list_of_files = zip.namelist()
            to_be_extracted = []
            
            for file in list_of_files:
                for extension in list_of_extensions:
                    if extension in file:
                        to_be_extracted.append(file)
                        if extension == '.key' and session['file_key_d'] == '':
                            session['file_key_d'] = file
                        else: 
                            if session['filename_d'] == '': 
                                session['filename_d'] = file
                        
            zip.extractall(app.config['AUDIO_UPLOAD'], to_be_extracted)
        os.remove(os.path.join(app.config['AUDIO_UPLOAD'], zip_name))
        
        file = Want_to_crypt(session['filename_d'])
        
        session['filename_new_d'] = file.new_name(2)
        
        file.decrypt(app.config['AUDIO_UPLOAD'], session['file_key'])
    
    return render_template('Musicode_decode_page.html')
    
    
@app.route('/download_encrypt', methods=['GET'])
def download_encrypt():
    
    if 'filename_new' in session:  
        stream = BytesIO()
        with ZipFile(stream, 'w') as zf:
            for file in glob(app.config['AUDIO_UPLOAD'] + '\\' + session['filename_new']):
                zf.write(file, os.path.basename(file))
                
            for file in glob(app.config['AUDIO_UPLOAD'] + '\\' + session['file_key']):
                zf.write(file, os.path.basename(file))
        stream.seek(0)
        
        delete_files_encrypt()
        
        return send_file(stream, as_attachment=True, attachment_filename='Musicode.zip')
        
    else: 
        return 'No files uploaded!'
    

@app.route('/download_decrypt', methods=['GET'])
def download_decrypt():
    
    if 'filename_new_d' in session:
        return send_file(os.path.join(app.config['AUDIO_UPLOAD'], session['filename_new_d']), as_attachment=True)
        
    else: 
        return 'No files uploaded!'
    

@app.route('/delete_encrypt')
def delete_files_encrypt():
    if 'filename_new' in session:
        os.remove(app.config['AUDIO_UPLOAD'] + '\\' + session['filename'])
        os.remove(app.config['AUDIO_UPLOAD'] + '\\' + session['filename_new'])
        os.remove(app.config['AUDIO_UPLOAD'] + '\\' + session['file_key'])
        
        return redirect(request.referrer)
        
    else:
        return redirect(request.referrer)
    
@app.route('/delete_decrypt')
def delete_files_decrypt():
    if 'filename_new_d' in session:
        os.remove(app.config['AUDIO_UPLOAD'] + '\\' + session['filename_d'])
        os.remove(app.config['AUDIO_UPLOAD'] + '\\' + session['filename_new_d'])
        os.remove(app.config['AUDIO_UPLOAD'] + '\\' + session['file_key_d'])
        
        return redirect(request.referrer)
        
    else:
        return redirect(request.referrer)


if __name__ == "__main__":
    app.run(debug = True)