import os
from wsgiref.simple_server import make_server
from app import application  # Importa la función 'application' de tu app.py

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    host = "0.0.0.0" 
    
    print(f" Servidor de desarrollo activo en: http://localhost:{port}")
    
    httpd = make_server(host, port, application)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n Servidor detenido.")