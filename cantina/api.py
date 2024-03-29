from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
from flask import jsonify, request, send_file, session

from . import app, cache, db
from .models import Affiliation, Payment, Payroll, Product, ProductSale, Task, User
from .settings import CART_TIMEOUT


@app.route("/api/adicionar-ao-carrinho", methods=["POST"])
def add_to_cart_api():
    data = request.get_json()
    product_id = data.get("id")
    try:
        product = Product.query.filter_by(id=product_id).first()
        if product is None:
            context = {"message": f"Produto de ID {product_id} não encontrado!", "ok": False}
            return jsonify(context)
        if product.quantity < 1:
            context = {"message": f"O produto {product.name} não possui estoque!", "ok": False}
            return jsonify(context)
        product.quantity -= 1
        db.session.commit()
    except Exception as e:
        context = {"message": "Alguma coisa deu errado...", "ok": False}
        return jsonify(context)
    else:
        context = {
            "message": f"Produto {product.name} adicionado com sucesso!",
            "product": product.as_dict(),
            "ok": True,
        }
        new_task = Task(
            type="product_cleanup",
            target_id=product.id,
            user_id=session["user"].id,
            expires_at=datetime.now() + timedelta(seconds=CART_TIMEOUT),
            target_type="product",
        )
        db.session.add(new_task)
        db.session.commit()
        session["cart"].append(product)
        return jsonify(context)


@app.route("/api/remover-do-carrinho", methods=["POST"])
def remove_from_cart_api():
    data = request.get_json()
    product_id = data.get("id")
    found = False
    task = Task.query.filter_by(
        target_id=product_id, user_id=session["user"].id, is_done=False
    ).first()
    if task is not None:
        task.is_done = True
        task.finished_by_user_id = session["user"].id
        db.session.commit()
        found = True

    for product in session["cart"]:
        if product.id == product_id:
            session["cart"].remove(product)
            break

    if not found:
        context = {
            "message": f"Produto de ID {product_id} removido com sucesso!",  # neste caso, ta mais pra expirado, mas serve.
            "ok": False,
            "product": Product.query.filter_by(id=product_id).first().as_dict(),
        }
        return jsonify(context)
    product = Product.query.filter_by(id=product_id).first()
    product.quantity += 1
    db.session.commit()
    return jsonify(
        {
            "message": f"Produto {product.name} removido com sucesso!",
            "product": product.as_dict(),
            "ok": True,
        }
    )


@app.route("/api/obter-usuario", methods=["POST"])
def get_user_api():
    data = request.get_json()
    user_id = data.get("id")
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        context = {"message": f"Usuário de ID {user_id} não encontrado!", "user": False}
    else:
        context = {"message": f"Comprimente bem o usuário {user.name}! :D", "user": user.as_dict()}
    return jsonify(context)


@app.route("/api/gerar-usuario-aleatorio", methods=["POST"])
def generate_random_username_api():
    data = request.get_json()
    name = data.get("name", "aluno usuario").lower().split()
    if len(name) >= 2:
        username = f"{name[0]}.{name[-1]}"
    elif len(name) == 1:
        username = name[0]
    else:
        username = "aluno"

    existing_usernames = User.query.filter(User.username.ilike(f"{username}%")).all()
    if existing_usernames:
        username = f"{username}{len(existing_usernames)}"
    return jsonify({"username": username})


@app.route("/api/obter-pagamentos", methods=["POST"])
def get_payments_api():
    data = request.get_json()
    query = data.get("query")
    payments = (
        Payment.join(User, User.id == Payment.user_id)
        .filter(
            Payment.allowed_by.is_(None),
            Payment.id.ilike(f"%{query}%"),
            Payment.order_by(Payment.id.asc()),
        )
        .all()
    )
    result = []
    for payment in payments:
        payment = payment.as_dict()
        payment["user"] = payment["user"].as_dict()
        result.append(payment)
    return jsonify(result)


@app.route("/api/editar-pagamento", methods=["POST"])
def verify_payment_api():
    data = request.get_json()
    payment_id = data.get("id")
    accepted = data.get("accept")
    payment = Payment.query.filter_by(id=payment_id).first()
    if payment is None:
        return jsonify({"message": f"Pagamento de ID {payment_id} não encontrado!", "error": True})

    if payment.status != "to allow":
        return jsonify(
            {
                "message": f"Muito engraçadinho, mas o pagamento de ID {payment_id} já possui status definido ({payment.status})!",
                "error": True,
            }
        )

    requester = User.query.filter_by(id=payment.user_id).first()

    if payment.is_payroll:  # forma de recarregar
        affiliation = Affiliation.query.filter_by(affiliated_id=requester.id).first()
        if affiliation is None:
            return jsonify({"message": "Matrix error, chama o felipe", "error": True})
    else:
        affiliation = None

    if accepted:
        if payment.is_payroll and payment.is_paypayroll:
            return jsonify(
                {
                    "message": "Pode rejeitar, basicamente essa pessoa tentou pagar a folha de pagamento usando a folha de pagamento :D",
                    "error": True,
                }
            )

        if payment.is_payroll:  # forma de recarregar
            affiliation = Affiliation.query.filter_by(affiliated_id=requester.id).first()
            if affiliation is None:
                return jsonify({"message": "Matrix error, chama o felipe", "error": True})
            affiliation.affiliator.balance_payroll += payment.value

            new_payroll = Payroll(
                value=payment.value,
                affiliation_id=affiliation.id,
                allowed_by=session["user"].id,
                status="accepted",
                affiliation=affiliation,
            )
            db.session.add(new_payroll)
        elif payment.is_paypayroll:  # pagamento da folha de pagamento
            financiador = User.query.filter_by(id=requester.id).first()
            financiador.balance_payroll -= payment.value

        if not payment.is_paypayroll:
            requester.balance += payment.value
        payment.allowed_by = session["user"].id
        payment.status = "accepted"

        message = f"Pagamento de ID {payment.id} liberado com sucesso! Saldo do usuário {requester.name} foi alterado para R$ {requester.balance}."
        ok = True
    else:
        # se status = 'rejected' então allowed_by é disallowed_by
        payment.status = "rejected"
        payment.allowed_by = session["user"].id
        db.session.commit()
        message = f"Pagamento de ID {payment_id} rejeitado com sucesso!"
        if payment.is_paypayroll:
            new_payroll = Payroll(
                value=payment.value,
                affiliation_id=getattr(affiliation, "id", None),
                allowed_by=session["user"].id,
                status="rejected",
                affiliation=affiliation,
            )
            db.session.add(new_payroll)
        ok = False
    db.session.commit()

    return jsonify({"message": message, "ok": ok})


@app.route("/api/exportar-para-excel", methods=["GET"])
def export_to_excel_api():
    result_id = request.args.get("result_id")

    todo = cache.get(result_id)
    if todo is None:
        return jsonify(
            {
                "message": f"Resultado de ID {result_id} não encontrado ou expirado...",
            }
        )
    if isinstance(todo, str):
        return jsonify({"message": todo})

    data = todo["data"]
    identifier = todo["identifier"]

    data = list(map(lambda x: x.as_friendly_dict(), data))

    if not data:
        return jsonify(
            {
                "message": "Nenhum dado encontrado para exportar.",
            }
        )

    df = pd.DataFrame(data)
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:  # type: ignore [output is binary]
        df.to_excel(writer, index=False, sheet_name="Sheet1")

    output.seek(0)
    return send_file(output, as_attachment=True, download_name=f"{identifier}.xlsx")


@app.route("/api/listar-usuários-para-despache", methods=["POST"])
def list_users_pending_desp_api():
    products = ProductSale.query.filter_by(status="to dispatch").all()
    users_id = set([product.sold_to for product in products])
    result = [user.as_dict() for user in User.query.filter(User.id.in_(users_id)).all()]
    return jsonify(result)


@app.route("/api/confirmar-despache", methods=["POST"])
def confirm_despache_api():
    data = request.get_json()
    venda_id = data.get("id")
    if venda_id is None:
        return jsonify({"message": f"ID da venda deve ser especificado...", "error": True})
    product_sale = ProductSale.query.filter_by(id=venda_id).first()
    if product_sale is None or product_sale.status != "to dispatch":
        return jsonify({"message": f"Venda de ID {venda_id} não encontrada!", "error": True})
    product_sale.status = "dispatched"
    db.session.commit()
    product_sale.dispatched_by = session["user"].id
    db.session.commit()
    product_sale.dispatched_at = datetime.now()
    db.session.commit()
    return jsonify(
        {"message": f"Confirmado o despacho da venda de ID {venda_id} com sucesso!", "error": False}
    )


@app.route("/api/confirmar-todos-produtos", methods=["POST"])
def confirm_all_despaches_api():
    products = ProductSale.query.filter_by(status="to dispatch").all()
    for product in products:
        product.status = "dispatched"
        product.dispatched_by = session["user"].id
        product.dispatched_at = datetime.now()
        db.session.commit()
    return jsonify({"message": "Todos os produtos foram despachados com sucesso!", "error": False})


@app.route("/api/confirmar-todos-produtos-usuario", methods=["POST"])
def confirm_all_user_despaches_api():
    data = request.get_json()
    user_id = data.get("user_id")
    if user_id is None:
        return jsonify({"message": f"ID do usuário deve ser especificado...", "error": True})
    products = ProductSale.query.filter_by(sold_to=user_id, status="to dispatch").all()
    if not products:
        return jsonify(
            {"message": f"Nenhum produto do usário {user_id} encontrado!", "error": True}
        )
    for product in products:
        product.status = "dispatched"
        product.dispatched_by = session["user"].id
        product.dispatched_at = datetime.now()
        db.session.commit()
    return jsonify(
        {
            "message": f"Todos os produtos do usário {user_id} foram despachados com sucesso!",
            "error": False,
        }
    )


@app.route("/api/produtos-para-despache-do-usuario", methods=["POST"])
def list_user_despaches_api():
    data = request.get_json()
    user_id = data.get("user_id")
    if user_id is None:
        return jsonify({"message": f"ID do usuário deve ser especificado...", "error": True})

    products = ProductSale.query.filter_by(sold_to=user_id, status="to dispatch").all()
    products_list = []
    for product in products:
        product_item = product.as_dict()
        product_item["sold_to_user"] = product.sold_to_user.as_dict()
        product_item["product"] = product.product.as_dict()
        products_list.append(product_item)
    return jsonify(products_list)
