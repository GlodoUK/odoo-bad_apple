{
    "name": "Bad Odoo",
    "summary": "Pure cinema.",
    "author": "Glo Networks",
    "website": "https://www.glo.systems/",
    "category": "Uncategorized",
    "version": "18.0.1.0.0",
    "external_dependencies": {"python": ["pillow"], "bin": ["ffmpeg"]},
    "depends": ["web", "queue_job", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/screen.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "bad_odoo/static/scss/bad_odoo.scss",
            "bad_odoo/static/src/actions/*",
            "bad_odoo/static/src/views/*",
        ],
    },
    "license": "Other proprietary",
}
