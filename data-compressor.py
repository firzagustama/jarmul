from flask import Flask, render_template, request, redirect, send_from_directory, flash, url_for
from PIL import Image, ImageFilter
from pydub import AudioSegment
import ffmpy
import os

UPLOAD_FOLDER = 'uploaded_files'

app = Flask(__name__)
app.secret_key = os.urandom(16)

# other algorithm here
def convert_to_png(filename, frm):
    img = Image.open(os.path.join(UPLOAD_FOLDER, filename))
    fo_name = "convert.png"
    file_out = os.path.join(UPLOAD_FOLDER, fo_name)
    img.save(file_out)
    return fo_name

def convert_to_bmp(filename, frm):
    img = Image.open(os.path.join(UPLOAD_FOLDER, filename))
    fo_name = "convert.bmp"
    file_out = os.path.join(UPLOAD_FOLDER, fo_name)
    img.save(file_out)
    return fo_name

def convert_to_jpg(filename, frm):
    img = Image.open(os.path.join(UPLOAD_FOLDER, filename))
    img = img.convert('RGB')
    fo_name = "convert.jpg"
    file_out = os.path.join(UPLOAD_FOLDER, fo_name)
    img.save(file_out)
    return fo_name

def convert_to_tiff(filename, frm):
    img = Image.open(os.path.join(UPLOAD_FOLDER, filename))
    if(frm != 'jpg'):
        img = img.convert('RGB')
        tmp_file = os.path.join(UPLOAD_FOLDER, "tmp.jpg")
        img.save(tmp_file)
    img = Image.open(tmp_file)
    fo_name = "convert.tiff"
    file_out = os.path.join(UPLOAD_FOLDER, fo_name)
    img.save(file_out)
    os.remove(tmp_file)
    return fo_name

def image_converter(filename, frm, to):
    outname = "convert." + to

    inp_path = os.path.join(UPLOAD_FOLDER, filename)
    out_path = os.path.join(UPLOAD_FOLDER, outname)

    if to == "png":
        img = Image.open(inp_path)
    else:
        img = Image.open(inp_path).convert('RGB')

    img.save(out_path, compression='None')

    return outname

def image_conversion(filename, quality, width, height, depth, fltr):
    ext = filename.split('.')[1]
    outname = "conversion." + ext

    inp_path = os.path.join(UPLOAD_FOLDER, filename)
    out_path = os.path.join(UPLOAD_FOLDER, outname)


    if depth != "":
        img = Image.open(inp_path).convert(depth)
    else:
        img = Image.open(inp_path)

    w, h = img.size
    if width != "":
        w = int(width)
    if height != "":
        h = int(height)
    size = w, h
    img.thumbnail(size)

    if fltr != "":
        if fltr == "blur":
            im = img.filter(ImageFilter.BLUR)
        elif fltr == "contour":
            im = img.filter(ImageFilter.CONTOUR)
        elif fltr == "detail":
            im = img.filter(ImageFilter.DETAIL)

        im.save(out_path, quality=int(quality))
    else:
        img.save(out_path, quality=int(quality))

    return outname

def audio_converter(filename, frm, to):
    outname = "convert." + to

    inp_path = os.path.join(UPLOAD_FOLDER, filename)
    out_path = os.path.join(UPLOAD_FOLDER, outname)
    if frm == "wav":
        tmp_path = os.path.join(UPLOAD_FOLDER, "tmp.wav")
        os.system("ffmpeg -i " + inp_path + " -y " + tmp_path)
        inp_path = tmp_path

    sound = AudioSegment.from_file(inp_path).export(out_path, format=to)

    if frm == "wav":
        os.remove(tmp_path)

    return outname

def audio_conversion(filename, bitrate, samplerate, channel):
    ext = filename.split('.')[1]
    outname = "conversion." + ext

    inp_path = os.path.join(UPLOAD_FOLDER, filename)
    out_path = os.path.join(UPLOAD_FOLDER, outname)

    if ext == "wav":
        tmp_path = os.path.join(UPLOAD_FOLDER, "tmp.wav")
        os.system("ffmpeg -i " + inp_path + " -y " + tmp_path)
        inp_path = tmp_path

    # Algorithm
    sound = AudioSegment.from_file(inp_path).export(out_path, bitrate=bitrate, parameters=["-ac", channel, "-ar", samplerate])

    if ext == "wav":
        os.remove(tmp_path)

    return outname

def video_converter(filename, frm, to):
    outname = "convert." + to

    inp_path = os.path.join(UPLOAD_FOLDER, filename)
    out_path = os.path.join(UPLOAD_FOLDER, outname)

    video = ffmpy.FFmpeg(
            inputs = {inp_path: None},
            outputs = {out_path: None}
        )
    video.run()

    return outname

def video_conversion(filename, framesize, bitrate, framerate, channel, audiosamplerate):
    ext = filename.split('.')[1]
    outname = "conversion." + ext

    inp_path = os.path.join(UPLOAD_FOLDER, filename)
    out_path = os.path.join(UPLOAD_FOLDER, outname)

    video = ffmpy.FFmpeg(
            inputs = {inp_path: None},
            outputs = {out_path: '-y -vf "scale=' + framesize + '" -r ' + framerate + ' -b:v ' + bitrate + ' -ac ' + channel + ' -ar ' + audiosamplerate}
        )
    video.run()

    return outname


@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/download/<filename>')
def download(filename):
    return render_template('download.html', filename=filename)

@app.route('/upload', methods=['POST'])
def upload():
    # try:
    file = request.files['file']
    action = request.form['action']
    filetype = request.form['filetype']
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))

    file_ext = file.filename.split('.')[1]

    if action == 'Converter':
        convert_to = request.form['convert_to']
        if filetype == '0':
            output = image_converter(file.filename, file_ext, convert_to)
        elif filetype == '1':
            output = audio_converter(file.filename, file_ext, convert_to)
        elif filetype == '2':
            output = video_converter(file.filename, file_ext, convert_to)
    elif action == 'Conversion':
        if filetype == '0':
            quality = request.form['quality']
            width = request.form['width']
            height = request.form['height']
            depth = request.form['color_depth']
            fltr = request.form['filter']
            output = image_conversion(file.filename, quality, width, height, depth, fltr)
        elif filetype == '1':
            bitrate = request.form['bitrate']
            samplerate = request.form['samplerate']
            channel = request.form['channel']
            output = audio_conversion(file.filename, bitrate, samplerate, channel)
        elif filetype == '2':
            framesize = request.form['framesize']
            framerate = request.form['framerate']
            bitrate = request.form['bitrate']
            channel = request.form['channel']
            asr = request.form['samplerate']
            output = video_conversion(file.filename, framesize, bitrate, framerate, channel, asr)

    # except:
    #     flash('Cannot convert file', 'error')
    #     return redirect(url_for('index'))

    return redirect(url_for('download', filename=output))

@app.route('/file/<filename>')
def file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)