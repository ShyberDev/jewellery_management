app_name = "jewellery_management"
app_title = "Jewellery Management"
app_publisher = "Sri Sai Krishna Jewellery"
app_description = "Jewellery Management System for Sri Sai Krishna Jewellery"
app_email = "benwolf449@gmail.com"
app_license = "mit"

use_json_request_body = True

app_include_js = [
    "/assets/jewellery_management/js/jewellery_kanban.js"
]

doc_events = {
    "Jewellery Purchase Invoice": {
        "on_submit": "jewellery_management.jewellery_management.stock_hooks.create_purchase_stock_transactions"
    },

    "Jewellery Sales Invoice": {
        "on_submit": "jewellery_management.jewellery_management.stock_hooks.create_sales_stock_transactions"
    },

    "Jewellery Opening Stock": {
        "on_submit": "jewellery_management.jewellery_management.stock_hooks.create_opening_stock_transactions"
    },

    "Jewellery Order": {
        "before_delete": "jewellery_management.jewellery_management.stock_hooks.remove_order_from_kanban",
    },
}

export_python_type_annotations = True
require_type_annotated_api_methods = True

fixtures = [
    {
        "dt": "DocType",
        "filters": [["module", "=", "Jewellery"]],
    },
    {
        "dt": "Client Script",
        "filters": [
            [
                "dt",
                "in",
                [
                    "Jewellery Order",
                    "Jewellery Opening Stock",
                    "Jewellery Sales Invoice",
                    "Jewellery Purchase Invoice",
                    "Retail Stock Item",
                ],
            ]
        ],
    },
    {"dt": "Report", "filters": [["module", "=", "Jewellery"]]},
    {"dt": "Print Format", "filters": [["module", "=", "Jewellery"]]},
    {
        "dt": "Workflow",
        "filters": [["document_type", "like", "Jewellery%"]],
    },
    {
        "dt": "Kanban Board",
        "filters": [["reference_doctype", "like", "Jewellery%"]],
    },
    {
        "dt": "Custom Field",
        "filters": [["dt", "like", "Jewellery%"]],
    },
]
