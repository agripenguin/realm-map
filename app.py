from flask import Flask, request, redirect
from datetime import datetime
import os
import magic
import detect

IMAGES_DIR = './static/images'
IMAGES_URL = '/static/images'

app = Flask(__name__)

#データサイズの制限:4MB
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 

@app.route('/')
def index_page():
    return """
        <html><body><h1>アップロード</h1>
        <form action="/upload"
            method="POST"
            enctype="multipart/form-data">
            <input type="file" name="upfile">
            <input type="submit" value="アップロード">
        </form>
        </body></html>
    """

@app.route('/upload', methods=['POST'])
def upload():
    if not ('upfile' in request.files):
        return redirect('/')
    temp_file = request.files['upfile']
    if temp_file.filename == '':
        return redirect('/')
    fp = temp_file.stream
    mime = magic.from_buffer(fp.read(1024), mime=True) 
    fp.seek(0)
    #from_buffer()の引数はファイルオブジェクトをreadしたもの。openの場合、open('*', 'rb')でバイナリとしてreadする。
    
    if mime != 'image/png' and mime != 'image/jpeg':
    #if not is_jpegfile(temp_file.stream):
        return '<h1>画像ファイル以外アップできません</h1>'
    time_s = datetime.now().strftime('%Y%m%d%H%M%S')
    fname = time_s + '.' + mime.split('/')[1]
    detect.detect_map(fp).save(IMAGES_DIR+'/'+fname)
    #temp_file.save(IMAGES_DIR+'/'+fname)
    return redirect('/photo/'+fname)

@app.route('/photo/<fname>')
def photo_page(fname):
    if fname is None: return redirect('/')
    image_path = IMAGES_DIR + '/' + fname
    image_url = IMAGES_URL + '/' + fname
    if not os. path.exists(image_path):
        return '<h1>画像がありません</h1>'
    return """
        <h1>画像がアップロードされました</h1>
        <p>URL: {0}<br>
        file: {1}</p>
        <img src="{0}" width="400">
    """.format(image_url, image_path)

def is_jpegfile(fp):
    byte = fp.read(2)
    fp.seek(0)
    return byte[:2] == b'\xFF\xD8'

if __name__ == '__main__':
    app.run()
