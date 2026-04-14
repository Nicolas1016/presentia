from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import get_connection

app = Flask(__name__)
app.secret_key = "clave_secreta"

app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False
)


# ------------------ LOGIN ------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE correo=%s", (correo,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id_usuario"]
            return redirect(url_for("listar_usuarios"))
        else:
            return render_template("login.html", error="Credenciales inválidas")

    return render_template("login.html")


# ------------------ LOGOUT ------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ------------------ HOME ------------------
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("listar_usuarios"))


# ------------------ LISTAR ------------------
@app.route("/usuarios")
def listar_usuarios():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id_usuario, u.nombre, u.correo, r.nombre AS rol, u.estado
        FROM usuarios u
        LEFT JOIN roles r ON u.id_rol = r.id_rol
    """)
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("usuarios/listar.html", usuarios=usuarios)


# ------------------ CREAR ------------------
@app.route("/usuarios/crear", methods=["GET", "POST"])
def crear_usuario():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"].strip()
        password = request.form["password"]
        id_rol = int(request.form["id_rol"])

        hashed_pw = generate_password_hash(password)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, password, id_rol, estado)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, correo, hashed_pw, id_rol, "activo"))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("listar_usuarios"))

    return render_template("usuarios/crear.html")

# ------------------ EDITAR ------------------
@app.route("/usuarios/editar/<int:id>", methods=["GET", "POST"])
def editar_usuario(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"].strip()
        id_rol = int(request.form["id_rol"])
        password = request.form.get("password")

        if password:
            hashed_pw = generate_password_hash(password, method="pbkdf2:sha256", salt_length=15)
            cursor.execute("""
                UPDATE usuarios 
                SET nombre=%s, correo=%s, password=%s, id_rol=%s
                WHERE id_usuario=%s
            """, (nombre, correo, hashed_pw, id_rol, id))
        else:
            cursor.execute("""
                UPDATE usuarios 
                SET nombre=%s, correo=%s, id_rol=%s
                WHERE id_usuario=%s
            """, (nombre, correo, id_rol, id))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("listar_usuarios"))

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario=%s", (id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("usuarios/editar.html", user=user)


# ------------------ ELIMINAR ------------------
@app.route("/usuarios/eliminar/<int:id>")
def eliminar_usuario(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("listar_usuarios"))


# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)