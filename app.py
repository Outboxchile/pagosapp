from flask import Flask, render_template, request, redirect, url_for
from models import db, Persona, Pago, Comision
from datetime import date

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pagos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

@app.route("/")
def pendientes():
    pagos = Pago.query.filter_by(fecha_pagado=None).all()
    return render_template("pendientes.html", pagos=pagos)

@app.route("/realizados")
def realizados():
    pagos = Pago.query.filter(Pago.fecha_pagado.isnot(None)).all()
    return render_template("realizados.html", pagos=pagos)

@app.route("/")
def pendientes():
    return "✅ ¡Funciona la ruta raíz!"

@app.route("/pagar/<int:id>")
def pagar(id):
    pago = Pago.query.get_or_404(id)
    pago.fecha_pagado = date.today()
    db.session.commit()
    return redirect(url_for("pendientes"))

@app.route("/comisiones")
def reporte_comisiones():
    personas = Persona.query.all()
    resumen = []
    for p in personas:
        total = db.session.query(db.func.sum(Comision.monto)) \
            .join(Pago).filter(
                Comision.persona_id == p.id,
                Pago.fecha_pagado.isnot(None)
            ).scalar() or 0
        resumen.append((p.nombre, round(total, 2)))
    return render_template("comisiones.html", resumen=resumen)

def init_db():
    """Crea tablas y datos iniciales dentro del contexto de la app."""
    db.create_all()
    if Persona.query.count() == 0:
        for nombre, pct in [("A", 0.05), ("B", 0.07), ("C", 0.03)]:
            db.session.add(Persona(nombre=nombre, porcentaje=pct))
        db.session.commit()

if __name__ == "__main__":
    # Inicializa la base de datos y luego arranca el servidor
    with app.app_context():
        init_db()
    app.run(debug=True)