from flask import Flask, request, redirect
from datetime import date
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
            <input type="file" name="upfile"></br>
            拡張段階：<input type="number" min="0" max="4" name="zoom_level" value="0"></br>
            x：       <input type="number" name="x"></br>
            y：       <input type="number" name="y"></br>
            <input type="submit" value="アップロード">
        </form>
        </body></html>
    """

@app.route('/upload', methods=['POST'])
def upload():
    if not ('upfile' in request.files) or not (('zoom_level' or 'x' or 'y') in request.form):
        return redirect('/')

    temp_file = request.files['upfile']
    temp_zoom = request.form['zoom_level']
    temp_x = request.form['x']
    temp_y = request.form['y']
    if temp_file.filename == '' or temp_zoom == '' or temp_x == '' or temp_y == '':
        return redirect('/')

    fp = temp_file.stream
    mime = magic.from_buffer(fp.read(1024), mime=True) 
    fp.seek(0)
    #from_buffer()の引数はファイルオブジェクトをreadしたもの。openの場合、open('*', 'rb')でバイナリとしてreadする。
    
    if mime != 'image/png' and mime != 'image/jpeg':
    #if not is_jpegfile(temp_file.stream):
        return '<h1>画像ファイル以外アップできません</h1>'
    
    dt_now = str(date.today())
    save_dir = IMAGES_DIR + '/' + dt_now
    fname = temp_zoom + ',' + temp_x + ',' + temp_y + '.' + mime.split('/')[1]

    try:
        os.makedirs(save_dir, exist_ok=True)
    except FileExistsError:
        pass

    detect.detect_map(fp).save(save_dir +'/'+fname)
    #temp_file.save(IMAGES_DIR+'/'+fname)
    return redirect('/photo/'+dt_now+'_'+fname)

@app.route('/photo/<dir_fname>')
def photo_page(dir_fname):
    if dir_fname is None: return redirect('/')
    dt, fname = dir_fname.split('_')
    image_path = IMAGES_DIR + '/' + dt + '/' + fname
    image_url = IMAGES_URL + '/' + dt + '/' + fname
    if not os.path.exists(image_path):
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
