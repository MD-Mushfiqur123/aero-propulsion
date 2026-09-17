import http.server
import socketserver
import webbrowser
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
PORT = 8099

Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(('', PORT), Handler) as httpd:
    print(f'Serving 3D Viewer at http://localhost:{PORT}/viewer.html')
    webbrowser.open(f'http://localhost:{PORT}/viewer.html')
    httpd.serve_forever()
