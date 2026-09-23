import json

import frappe
from frappe.utils import flt


def get_available_stock(retail_stock_item, purity):
    """
    Current physical stock for:
    Retail Stock Item + Purity
    """

    transactions = frappe.get_all(
        "Jewellery Stock Transaction",
        filters={
            "retail_stock_item": retail_stock_item,
            "purity": purity,
        },
        fields=["movement", "weight"],
    )

    available_weight = 0.0

    for transaction in transactions:
        weight = flt(transaction.weight)

        if transaction.movement == "In":
            available_weight += weight

        elif transaction.movement == "Out":
            available_weight -= weight

    return round(available_weight, 3)


def validate_sales_stock(doc):
    """
    Ensure every Sales Item has enough physical stock.
    Stock bucket = Retail Stock Item + Purity.
    """

    for row in doc.items:

        if not row.retail_stock_item:
            frappe.throw(
                f"Retail Stock Item is required for sales item {row.idx}."
            )

        if not row.purity:
            frappe.throw(
                f"Purity is required for sales item {row.idx}."
            )

        requested_weight = flt(row.gross_weight)

        if requested_weight <= 0:
            requested_weight = flt(row.net_weight)

        if requested_weight <= 0:
            continue

        available_weight = get_available_stock(
            row.retail_stock_item,
            row.purity,
        )

        if requested_weight > available_weight:

            stock_item_name = frappe.db.get_value(
                "Retail Stock Item",
                row.retail_stock_item,
                "stock_item_name",
            ) or row.retail_stock_item

            purity_name = frappe.db.get_value(
                "Metal Purity",
                row.purity,
                "purity_name",
            ) or row.purity

            frappe.throw(
                (
                    f"<b>Insufficient Stock</b><br><br>"
                    f"<b>Retail Stock Item:</b> {stock_item_name}<br>"
                    f"<b>Purity:</b> {purity_name}<br>"
                    f"<b>Available:</b> {available_weight:.3f} g<br>"
                    f"<b>Requested:</b> {requested_weight:.3f} g"
                )
            )


def create_purchase_stock_transactions(doc, method=None):
    """
    Create Stock IN transactions from Jewellery Purchase Invoice.
    """

    existing = frappe.db.exists(
        "Jewellery Stock Transaction",
        {
            "reference_type": "Jewellery Purchase Invoice",
            "reference_no": doc.name,
            "transaction_type": "Purchase",
        },
    )

    if existing:
        return

    for row in doc.items:

        if not row.item_name:
            continue

        if not row.retail_stock_item:
            frappe.throw(
                f"Retail Stock Item is required for purchase item {row.idx}."
            )

        stock_weight = flt(row.gross_weight)

        if stock_weight <= 0:
            stock_weight = flt(row.net_weight)

        if stock_weight <= 0:
            continue

        stock_transaction = frappe.new_doc(
            "Jewellery Stock Transaction"
        )

        stock_transaction.transaction_date = doc.purchase_date
        stock_transaction.transaction_type = "Purchase"
        stock_transaction.reference_type = (
            "Jewellery Purchase Invoice"
        )
        stock_transaction.reference_no = doc.name

        stock_transaction.item = row.item_name
        stock_transaction.retail_stock_item = row.retail_stock_item
        stock_transaction.weight = stock_weight
        stock_transaction.movement = "In"

        stock_transaction.purity = row.purity
        stock_transaction.purity_percentage = (
            row.purity_percentage
        )

        stock_transaction.pure_weight_24k = (
            row.pure_weight_24k
        )
        stock_transaction.rate_24k = row.rate_24k
        stock_transaction.stock_value = row.total_amount

        stock_transaction.insert(
            ignore_permissions=True
        )


def create_sales_stock_transactions(doc, method=None):
    """
    Validate stock and create Stock OUT transactions
    from Jewellery Sales Invoice.
    """

    validate_sales_stock(doc)

    existing = frappe.db.exists(
        "Jewellery Stock Transaction",
        {
            "reference_type": "Jewellery Sales Invoice",
            "reference_no": doc.name,
            "transaction_type": "Sale",
        },
    )

    if existing:
        return

    for row in doc.items:

        if not row.item_name:
            continue

        if not row.retail_stock_item:
            frappe.throw(
                f"Retail Stock Item is required for sales item {row.idx}."
            )

        stock_weight = flt(row.gross_weight)

        if stock_weight <= 0:
            stock_weight = flt(row.net_weight)

        if stock_weight <= 0:
            continue

        stock_transaction = frappe.new_doc(
            "Jewellery Stock Transaction"
        )

        stock_transaction.transaction_date = doc.sales_date
        stock_transaction.transaction_type = "Sale"
        stock_transaction.reference_type = (
            "Jewellery Sales Invoice"
        )
        stock_transaction.reference_no = doc.name

        stock_transaction.item = row.item_name
        stock_transaction.retail_stock_item = row.retail_stock_item
        stock_transaction.weight = stock_weight
        stock_transaction.movement = "Out"

        stock_transaction.purity = row.purity
        stock_transaction.purity_percentage = (
            row.purity_percentage
        )

        stock_transaction.pure_weight_24k = (
            row.chargeable_weight
        )
        stock_transaction.rate_24k = row.rate_24k
        stock_transaction.stock_value = row.total_amount

        stock_transaction.insert(
            ignore_permissions=True
        )


def create_opening_stock_transactions(doc, method=None):
    """
    Create Stock IN transactions from Jewellery Opening Stock.
    """

    existing = frappe.db.exists(
        "Jewellery Stock Transaction",
        {
            "reference_type": "Jewellery Opening Stock",
            "reference_no": doc.name,
            "transaction_type": "Opening Stock",
        },
    )

    if existing:
        return

    for row in doc.items:

        if not row.retail_stock_item:
            frappe.throw(
                f"Retail Stock Item is required for opening stock row {row.idx}."
            )

        if not row.purity:
            frappe.throw(
                f"Purity is required for opening stock row {row.idx}."
            )

        weight = flt(row.weight)

        if weight <= 0:
            continue

        stock_transaction = frappe.new_doc(
            "Jewellery Stock Transaction"
        )

        stock_transaction.transaction_date = doc.posting_date
        stock_transaction.transaction_type = "Opening Stock"
        stock_transaction.reference_type = (
            "Jewellery Opening Stock"
        )
        stock_transaction.reference_no = doc.name

        stock_transaction.item = row.item_name
        stock_transaction.retail_stock_item = row.retail_stock_item
        stock_transaction.weight = weight
        stock_transaction.movement = "In"
        stock_transaction.purity = row.purity

        if doc.warehouse:
            stock_transaction.warehouse = doc.warehouse

        stock_transaction.rate_24k = row.rate
        stock_transaction.stock_value = (
            weight * flt(row.rate)
        )

        stock_transaction.insert(
            ignore_permissions=True
        )


def get_order_stock_item_candidates(item_name, material, purity):
    """
    Find active Retail Stock Items suitable for a Jewellery Order Item.
    Matching uses:
        Article Category = item_name
        Metal            = material
        Purity           = purity
    """

    filters = {
        "article_category": item_name,
        "active": 1,
    }

    if material:
        filters["metal"] = material

    if purity:
        filters["purity"] = purity

    return frappe.get_all(
        "Retail Stock Item",
        filters=filters,
        fields=[
            "name",
            "stock_item_name",
            "metal",
            "article_category",
            "purity",
            "stock_identity_code",
        ],
        order_by="stock_item_name asc",
    )


@frappe.whitelist()
def get_order_stock_candidates(order_name: str):
    """
    Return candidate Retail Stock Items for every order item.
    """

    order = frappe.get_doc(
        "Jewellery Order",
        order_name,
    )

    if order.order_status != "Received":
        frappe.throw(
            "Items can be sent to Retail Stock only when "
            "Order Status is Received."
        )

    result = []

    for row in order.jewellery_items:

        if not row.item_name:
            continue

        net_weight = flt(
            row.delivered_net_weight
        )

        if net_weight <= 0:
            frappe.throw(
                f"Delivered Net Weight is required "
                f"for order item {row.idx}."
            )

        candidates = get_order_stock_item_candidates(
            row.item_name,
            row.material,
            row.purity,
        )

        result.append(
            {
                "row_name": row.name,
                "idx": row.idx,
                "item_name": row.item_name,
                "material": row.material,
                "purity": row.purity,
                "delivered_net_weight": net_weight,
                "already_transferred": bool(
                    row.stock_transferred
                ),
                "current_stock_item": row.retail_stock_item,
                "candidates": candidates,
            }
        )

    return result


@frappe.whitelist()
def create_retail_stock_item(
    stock_item_name: str,
    article_category: str,
    metal: str,
    purity: str,
    stock_identity_code: str,
):
    """
    Create a Retail Stock Item from the Jewellery Order workflow.
    """

    stock_item_name = (stock_item_name or "").strip()
    stock_identity_code = (stock_identity_code or "").strip()

    if not stock_item_name:
        frappe.throw("Stock Item Name is required.")

    if not article_category:
        frappe.throw("Article Category is required.")

    if not metal:
        frappe.throw("Metal is required.")

    if not stock_identity_code:
        frappe.throw("Stock Identity Code is required.")

    existing = frappe.db.exists(
        "Retail Stock Item",
        {
            "stock_identity_code": stock_identity_code,
        },
    )

    if existing:
        frappe.throw(
            f"Stock Identity Code {stock_identity_code} "
            f"already exists in Retail Stock Item {existing}."
        )

    item = frappe.new_doc(
        "Retail Stock Item"
    )

    item.stock_item_name = stock_item_name
    item.article_category = article_category
    item.metal = metal
    item.purity = purity
    item.stock_identity_code = stock_identity_code
    item.active = 1

    item.insert(
        ignore_permissions=True
    )

    frappe.db.commit()

    return {
        "name": item.name,
        "stock_item_name": item.stock_item_name,
        "article_category": item.article_category,
        "metal": item.metal,
        "purity": item.purity,
        "stock_identity_code": item.stock_identity_code,
    }


@frappe.whitelist()
def send_items_to_retail_stock(
    order_name: str,
    selections: str,
):
    """
    Transfer selected Jewellery Order Items to Retail Stock.

    selections is a list of:
        {
            "row_name": "...",
            "retail_stock_item": "RSI-..."
        }
    """

    if isinstance(selections, str):
        selections = frappe.parse_json(selections)

    if not isinstance(selections, list):
        frappe.throw(
            "Invalid Retail Stock selection."
        )

    order = frappe.get_doc(
        "Jewellery Order",
        order_name,
    )

    if order.order_status != "Received":
        frappe.throw(
            "Items can be sent to Retail Stock only when "
            "Order Status is Received."
        )

    rows_by_name = {
        row.name: row
        for row in order.jewellery_items
    }

    transferred = []

    for selection in selections:

        row_name = selection.get(
            "row_name"
        )

        retail_stock_item = selection.get(
            "retail_stock_item"
        )

        if not row_name:
            frappe.throw(
                "Order item was not specified."
            )

        row = rows_by_name.get(
            row_name
        )

        if not row:
            frappe.throw(
                f"Order item {row_name} was not found."
            )

        if row.stock_transferred:
            transferred.append(
                {
                    "row_name": row.name,
                    "stock_transaction":
                        row.stock_transaction,
                    "already_transferred": True,
                }
            )
            continue

        if not retail_stock_item:
            frappe.throw(
                f"Retail Stock Item is required "
                f"for order item {row.idx}."
            )

        valid_candidates = (
            get_order_stock_item_candidates(
                row.item_name,
                row.material,
                row.purity,
            )
        )

        valid_names = {
            item.name
            for item in valid_candidates
        }

        if retail_stock_item not in valid_names:

            frappe.throw(
                f"Invalid Retail Stock Item selected "
                f"for order item {row.idx}."
            )

        weight = flt(
            row.delivered_net_weight
        )

        if weight <= 0:
            frappe.throw(
                f"Delivered Net Weight is required "
                f"for order item {row.idx}."
            )

        existing_transaction = frappe.db.exists(
            "Jewellery Stock Transaction",
            {
                "reference_type": "Jewellery Order",
                "reference_no": order.name,
                "transaction_type": "Order Transfer",
                "item": row.item_name,
                "retail_stock_item": retail_stock_item,
                "movement": "In",
            },
        )

        if existing_transaction:
            row.stock_transferred = 1
            row.stock_transaction = (
                existing_transaction
            )
            row.retail_stock_item = (
                retail_stock_item
            )

            transferred.append(
                {
                    "row_name": row.name,
                    "stock_transaction":
                        existing_transaction,
                    "already_transferred": True,
                }
            )

            continue

        stock_transaction = frappe.new_doc(
            "Jewellery Stock Transaction"
        )

        stock_transaction.transaction_date = (
            order.order_date
        )

        stock_transaction.transaction_type = (
            "Order Transfer"
        )

        stock_transaction.reference_type = (
            "Jewellery Order"
        )

        stock_transaction.reference_no = (
            order.name
        )

        stock_transaction.item = (
            row.item_name
        )

        stock_transaction.retail_stock_item = (
            retail_stock_item
        )

        stock_transaction.weight = weight

        stock_transaction.movement = "In"

        stock_transaction.purity = (
            row.purity
        )

        stock_transaction.insert(
            ignore_permissions=True
        )

        row.retail_stock_item = (
            retail_stock_item
        )

        row.stock_transferred = 1

        row.stock_transaction = (
            stock_transaction.name
        )

        transferred.append(
            {
                "row_name": row.name,
                "stock_transaction":
                    stock_transaction.name,
                "already_transferred": False,
            }
        )

    order.save(
        ignore_permissions=True
    )

    frappe.db.commit()

    return {
        "order": order.name,
        "transferred": transferred,
    }


def remove_order_from_kanban(doc, method=None):
    """
    Remove the deleted Jewellery Order from all Kanban columns.
    """

    boards = frappe.get_all(
        "Kanban Board",
        filters={
            "reference_doctype": "Jewellery Order"
        },
        pluck="name",
    )

    for board_name in boards:

        columns = frappe.get_all(
            "Kanban Board Column",
            filters={
                "parent": board_name
            },
            fields=[
                "name",
                "order",
            ],
        )

        for column in columns:

            if not column.order:
                continue

            try:
                orders = json.loads(column.order)
            except Exception:
                continue

            if not isinstance(orders, list):
                continue

            if doc.name not in orders:
                continue

            orders = [
                order
                for order in orders
                if order != doc.name
            ]

            frappe.db.set_value(
                "Kanban Board Column",
                column.name,
                "order",
                json.dumps(orders),
                update_modified=False,
            )
