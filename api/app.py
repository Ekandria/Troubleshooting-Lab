from flask import Flask, jsonify, request
import sqlite3
from pathlib import Path

app = Flask(__name__)

DATABASE = Path(__file__).parent.parent / "database" / "app.db"


@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Troubleshooting Lab API"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/users", methods=["GET", "POST"])
def users():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    if request.method == "GET":
        rows = connection.execute(
            "SELECT id, name, email FROM users"
        ).fetchall()

        connection.close()

        return jsonify([dict(row) for row in rows])

    if request.method == "POST":
        data = request.get_json(silent=True)

        if not data or "name" not in data or "email" not in data:
            connection.close()

            return jsonify({
                "error": "name and email are required"
            }), 400

        try:
            cursor = connection.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (data["name"], data["email"])
            )

            connection.commit()

            new_user_id = cursor.lastrowid
            connection.close()

            return jsonify({
                "id": new_user_id,
                "name": data["name"],
                "email": data["email"]
            }), 201

        except sqlite3.IntegrityError:
            connection.close()

            return jsonify({
                "error": "email already exists"
            }), 409


@app.route("/users/<int:user_id>", methods=["PUT", "PATCH", "DELETE"])
def user_by_id(user_id):
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    user = connection.execute(
        "SELECT id, name, email FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    if user is None:
        connection.close()

        return jsonify({
            "error": "user not found"
        }), 404

    # DELETE
    if request.method == "DELETE":
        connection.execute(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )

        connection.commit()
        connection.close()

        return "", 204

    data = request.get_json(silent=True)

    if not data:
        connection.close()

        return jsonify({
            "error": "JSON body required"
        }), 400

    # PUT = replace the complete editable resource
    if request.method == "PUT":
        if "name" not in data or "email" not in data:
            connection.close()

            return jsonify({
                "error": "name and email are required"
            }), 400

        name = data["name"]
        email = data["email"]

    # PATCH = change only fields supplied
    else:
        name = data.get("name", user["name"])
        email = data.get("email", user["email"])

    try:
        connection.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            (name, email, user_id)
        )

        connection.commit()
        connection.close()

        return jsonify({
            "id": user_id,
            "name": name,
            "email": email
        })

    except sqlite3.IntegrityError:
        connection.close()

        return jsonify({
            "error": "email already exists"
        }), 409


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
