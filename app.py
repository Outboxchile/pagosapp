from flask import Flask, render_template, request, redirect, url_for
from models import db, Persona, Pago, Comision
from datetime import date

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pagos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# ---------- VISTAS PRINCIPALES ---------- #

@app.route("/")
def pendientes():
    pagos = Pago.query.filter_by(fecha_pagado=None).all()
    return render_template("pendientes.html", pagos=pagos)

@app.route("/realizados")
def realizados():
    pagos = Pago.query.filter(Pago.fecha_pagado.isnot(None)).all()
    return render_template("realizados.html", pagos=pagos)

@app.route("/nuevo", methods=["GET", "POST"])
def nuevo_pago():
    if request.method == "POST":
        cliente = request.form["cliente"].strip()
        monto = float(request.form["monto"])
        fecha = date.fromisoformat(request.form["fecha"])
        pago = Pago(cliente=cliente, monto=monto, fecha_programada=fecha)
        db.session.add(pago)
        db.session.commit()

        # crea comisiones automáticas
        for persona in Persona.query.all():
            db.session.add(
                Comision(
                    pago_id=pago.id,
                    persona_id=persona.id,
                    monto=round(monto * persona.porcentaje, 2)
                )
            )
        db.session.commit()
        return redirect(url_for("pendientes"))
    return render_template("nuevo_pago.html")

@app.route("/pagar/<int:id>")
def pagar(id):
    pago = Pago.query.get_or_404(id)
    pago.fecha_pagado = date.today()
    db.session.commit()
    return redirect(url_for("pendientes"))

# ---------- CONFIGURACIÓN DE COMISIONES ---------- #

@app.route("/comisiones", methods=["GET", "POST"])
def config_comisiones():
    if request.method == "POST":
        # Actualiza nombres y porcentajes
        for persona in Persona.query.all():
            persona.nombre = request.form.get(f"nombre_{persona.id}", "").strip() or persona.nombre
            pct_str = request.form.get(f"pct_{persona.id}", "0").replace(",", ".")
            try:
                pct_val = max(0.0, min(float(pct_str) / 100, 1.0))
                persona.porcentaje = pct_val
            except ValueError:
                pass  # ignora porcentajes no numéricos
        db.session.commit()
        return redirect(url_for("config_comisiones"))

    # Calcula totales por persona
    personas = Persona.query.all()
    data = []
    for p in personas:
        total = (
            db.session.query(db.func.sum(Comision.monto))
            .join(Pago)
            .filter(Comision.persona_id == p.id, Pago.fecha_pagado.isnot(None))
            .scalar()
            or 0
        )
        data.append((p, round(total, 2)))
    return render_template("comisiones.html", data=data)

# ---------- INICIALIZACIÓN DE LA BD ---------- #

def init_db():
    db.create_all()
    if Persona.query.count() == 0:
        seed = [("A", 0.05), ("B", 0.07), ("C", 0.03)]
        for nombre, pct in seed:
            db.session.add(Persona(nombre=nombre, porcentaje=pct))
        db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
