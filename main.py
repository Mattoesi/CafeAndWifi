import os
import requests
from flask import Flask, render_template, request, flash, redirect, url_for, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    map_url = db.Column(db.String(250), nullable=False)
    img_data = db.Column(db.LargeBinary, nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


def to_bool(raw_str):
    """Converts a string to a boolean."""
    if raw_str is None:
        return False
    if isinstance(raw_str, str):
        if raw_str.lower() in ("true", "1", "yes", "on"):
            return True
        elif raw_str.lower() in ("false", "0", "no", "off"):
            return False
    return bool(raw_str)


@app.route("/")
def home():
    cafes = Cafe.query.all()
    api_key = os.getenv("API_KEY")
    return render_template("index.html", cafes=cafes, api_key=api_key)


@app.route("/add", methods=["POST"])
def add_cafe():
    img_url = request.form.get("img_url")
    img_data = None
    if img_url:
        try:
            response = requests.get(img_url)
            if response.status_code == 200:
                img_data = response.content
                print(f"Successfully fetched image data, size: {len(img_data)} bytes")
            else:
                flash(f"Image URL returned status code: {response.status_code}", "danger")
                return redirect(url_for("show_add_cafe"))
        except Exception as e:
            flash(f"Failed to download image from URL: {e}", "danger")
            return redirect(url_for("show_add_cafe"))

    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_data=img_data,
        location=request.form.get("loc"),
        seats=request.form.get("seats"),
        has_toilet=to_bool(request.form.get("toilet")),
        has_wifi=to_bool(request.form.get("wifi")),
        has_sockets=to_bool(request.form.get("sockets")),
        can_take_calls=to_bool(request.form.get("calls")),
        coffee_price=request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    flash("Successfully added the new cafe.", "success")
    return redirect(url_for("home"))


@app.route("/image/<int:cafe_id>")
def serve_image(cafe_id):
    cafe = Cafe.query.get_or_404(cafe_id)
    print(f"Serving image for cafe ID: {cafe_id}, size: {len(cafe.img_data)} bytes")
    return Response(cafe.img_data, mimetype='image/jpeg')


@app.route("/addCafe", methods=["GET"])
def show_add_cafe():
    return render_template("addCafe.html")


@app.route("/cafes", methods=["GET"])
def get_cafes():
    cafes = Cafe.query.all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/delete/<int:cafe_id>", methods=["POST"])
def delete_cafe(cafe_id):
    api_key = request.form.get("api-key")
    if api_key == os.getenv("API_KEY"):
        cafe = Cafe.query.get_or_404(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            flash("Successfully deleted the cafe from the database.", "success")
        else:
            flash("Cafe with that id was not found in the database.", "danger")
    else:
        flash("That is not allowed. Make sure you have the correct api-key.", "danger")
    return redirect(url_for("home"))



@app.route("/modify/<int:cafe_id>", methods=["POST"])
def modify_cafe(cafe_id):
    api_key = request.form.get("api-key")
    if api_key == os.getenv("API_KEY"):
        cafe = Cafe.query.get_or_404(cafe_id)
        img_url = request.form.get("img_url")
        img_data = None
        if img_url:
            try:
                response = requests.get(img_url)
                if response.status_code == 200:
                    img_data = response.content
                    print(f"Successfully fetched image data, size: {len(img_data)} bytes")
                else:
                    flash(f"Image URL returned status code: {response.status_code}", "danger")
                    return redirect(url_for("show_modify_cafe", cafe_id=cafe_id))
            except Exception as e:
                flash(f"Failed to download image from URL: {e}", "danger")
                return redirect(url_for("show_modify_cafe", cafe_id=cafe_id))
        else:
            img_data = cafe.img_data

        # Update cafe details
        cafe.name = request.form.get("name")
        cafe.map_url = request.form.get("map_url")
        cafe.img_data = img_data
        cafe.location = request.form.get("loc")
        cafe.seats = request.form.get("seats")
        cafe.has_toilet = to_bool(request.form.get("toilet"))
        cafe.has_wifi = to_bool(request.form.get("wifi"))
        cafe.has_sockets = to_bool(request.form.get("sockets"))
        cafe.can_take_calls = to_bool(request.form.get("calls"))
        cafe.coffee_price = request.form.get("coffee_price")

        db.session.commit()
        flash("Successfully modified the cafe.", "success")
    else:
        flash("Invalid API key.", "danger")
    return redirect(url_for("home"))


@app.route("/modifyCafe/<int:cafe_id>", methods=["GET"])
def show_modify_cafe(cafe_id):
    cafe = Cafe.query.get_or_404(cafe_id)
    api_key = os.getenv("API_KEY")
    return render_template("modifyCafe.html", cafe=cafe, api_key=api_key)


if __name__ == "__main__":
    app.run(debug=True)
