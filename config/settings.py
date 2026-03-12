# config/settings.py

# =========================
# CONFIGURACIÓN
# =========================

USE_LOCAL_DB = True   # True = local | False = nube (Render)

# ----- BASE DE DATOS LOCAL -----
LOCAL_DB = {
    "server": "localhost",
    "user": "sa",
    "password": "123456789",
    "database": "corporativo_db",
    "port": 1433
}


# ----- BASE DE DATOS EN LA NUBE -----
CLOUD_DB = {
    "server": "DesarrolloWeb.mssql.somee.com",
    "user": "Johann_SQLLogin_1",
    "password": "3xwx5y8jq3",
    "database": "DesarrolloWeb"
}
