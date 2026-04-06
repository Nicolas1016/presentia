from flask import Blueprint, request, redirect, url_for, render_template
from app.utils.db import get_connection

# Crea el blueprint para las rutas de usuario
user_routes_app = Blueprint("user_routes_app", __name__)

@user_routes_app.route("/usuarios/editar/<int:id_usuario>", methods=["GET", "POST"])
def editar_usuario(id_usuario):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"].strip()
        id_rol = int(request.form["id_rol"])
        estado = request.form["estado"]

        cursor.execute("""
            UPDATE usuarios
            SET nombre=%s, correo=%s, id_rol=%s, estado=%s
            WHERE id_usuario=%s
        """, (nombre, correo, id_rol, estado, id_usuario))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("usuarios"))

    # Si es GET, carga los datos actuales
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario=%s", (id_usuario,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("usuarios/editar.html", usuario=usuario)