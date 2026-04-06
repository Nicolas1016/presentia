from werkzeug.security import generate_password_hash
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="db",
        port=3306,          
        user="root",
        password="root",        
        database="presentia"
    )

def insertar_usuarios_prueba():
    conn = get_connection()
    cursor = conn.cursor()

    usuarios = [
        ("Juan Pérez", "juan@example.com", "123456", 1, "activo"),
        ("María Gómez", "maria@example.com", "123456", 2, "activo"),
        ("Carlos Ruiz", "carlos@example.com", "123456", 1, "activo"),
        ("Laura Torres", "laura@example.com", "123456", 2, "activo"),
        ("Andrés Silva", "andres@example.com", "123456", 1, "activo"),
    ]

    for nombre, correo, password, id_rol, estado in usuarios:
        hashed_pw = generate_password_hash(password, method="pbkdf2:sha256", salt_length=15)
        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, password, id_rol, estado)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, correo, hashed_pw, id_rol, estado))

    conn.commit()
    cursor.close()
    conn.close()
    print("Usuarios de prueba insertados correctamente.")