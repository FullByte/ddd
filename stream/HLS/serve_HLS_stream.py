from flask import Flask, send_file, send_from_directory

app = Flask(__name__)

HLS_DIR = "HLS"

@app.route('/HLS/<stream>/<filename>')
def serve_hls(stream, filename):
    stream_path = os.path.join(HLS_DIR, stream)
    file_path = os.path.join(stream_path, filename)
    return send_file(file_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
