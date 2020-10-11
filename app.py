from flask import Flask, request, redirect, render_template, session
from flask import send_file, Markup
from datetime import date
import os
import shutil
import re
import magic
import detect
import integrate

IMAGES_DIR = './static/images'
IMAGES_URL = '/static/images'

app = Flask(__name__)
app.secret_key = '3Kj?2Yd['

#データサイズの制限:4MB
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/upload')
def upload_from_mobile():
    return render_template('upload_from_mobile.html')

@app.route('/upload_go', methods=['POST'])
def upload_go():
    if not ('upfile' in request.files) or not (('zoom_level' or 'x' or 'y') in request.form):
        return redirect('/')

    temp_file = request.files['upfile']
    temp_zoom = request.form['zoom_level']
    temp_x = request.form['x']
    temp_y = request.form['y']
    if temp_file.filename == '' or temp_zoom == '' or temp_x == '' or temp_y == '':
        return redirect('/')
    fp = temp_file.stream
    dt_now = str(date.today())
    mime = check_mime(fp)
    fname = temp_zoom + ',' + temp_x + ',' + temp_y + '.' + mime.split('/')[1]
    
    if check_save_file(fp, fname, dt_now) == -1:
        return '<h1>画像ファイル以外アップできません</h1>'
    return redirect('/photo/'+dt_now+'_'+fname)

@app.route('/multi_upload')
def multi():
    return render_template('multi_upload.html')

@app.route('/multi_upload_go', methods=['POST'])
def multi_go():
    flag = 0
    if not ('upload_files' in request.files):
        return redirect('/')

    upload_files = request.files.getlist('upload_files')
    
    if upload_files == []:
        return redirect('/')
    for upload_file in upload_files:
        fp = upload_file.stream
        dt_now = str(date.today())
        fname = upload_file.filename
        upflag = check_save_file(fp, fname, dt_now)
        if upflag == -1:
            session[fname] = '画像ファイル以外アップできません'
        elif upflag == -2:
            session[fname] = 'ファイル名が正しくありません'
        else:
            session[fname] = 'ok'
        flag += upflag
    session['flag'] = flag
    return redirect('/multi_finish')
    #redirect('/photo/'+dt_now+'_'+fname)
@app.route('/multi_finish')
def finish():
    allFiles = ''
    if session['flag'] == 0:
        title = 'アップロードが正常に完了しました'
    else:
        title = 'アップロードに問題がある可能性があります'
    for fname in session.keys():
        if type(session[fname]) == str:
            allFiles = allFiles + fname + ': ' + session[fname] + Markup('<br>')
    return render_template('multi_completed.html', title = title, pass_fail = allFiles)

@app.route('/photo/<dir_fname>')
def photo_page(dir_fname):
    if dir_fname is None: return redirect('/')
    dt, fname = dir_fname.split('_')
    image_path = IMAGES_DIR + '/' + dt + '/' + fname
    image_url = IMAGES_URL + '/' + dt + '/' + fname
    if not os.path.exists(image_path):
        return '<h1>画像がありません</h1>'
    return render_template('completed.html', url=image_url, path=image_path, dir_fname=dir_fname)

@app.route('/download/<dir_fname>')
def download(dir_fname):
    if dir_fname is None: return redirect('/')
    dt, fname = dir_fname.split('_')
    download_file = IMAGES_DIR + '/' + dt + '/' + fname
    return send_file(download_file, as_attachment =True, attachment_filename=fname)

@app.route('/integrate')
def request_integrate():
    return render_template('request_integrate.html')

@app.route('/integrate_download', methods=['POST'])
def integrate_download():
    shutil.rmtree('tmp')
    os.mkdir('tmp')
    area = request.form['area']
    today = date.today()
    fo, name = integrate.integrate_go(area)
    fname = '{0}_{1}.png'.format(today, name)
    dirname = './tmp/' + fname
    fo.save(dirname)
    return send_file(dirname, mimetype='image/png', as_attachment =True, attachment_filename=fname)

def check_mime(fp):
    #from_buffer()の引数はファイルオブジェクトをreadしたもの。
    #openの場合、open('*', 'rb')でバイナリとしてreadする。
    mime = magic.from_buffer(fp.read(1024), mime=True)
    fp.seek(0)
    return mime

def is_image(fp):
    mime = check_mime(fp)
    return mime == 'image/png' or mime == 'image/jpeg'

#画像ファイルかどうかチェックした上で保存する
def check_save_file(fp, fname, dt_now):
    if re.fullmatch(r'\d,\d,\d.[a-z]+', fname) == None:
        return -2
    if not is_image(fp):
        return -1
    
    save_dir = IMAGES_DIR + '/' + dt_now
    try:
        os.makedirs(save_dir, exist_ok=True)
    except FileExistsError:
        pass

    detect.detect_map(fp).save(save_dir +'/'+fname)
    return 0

if __name__ == '__main__':
    app.run()
