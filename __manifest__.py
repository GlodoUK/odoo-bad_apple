{
    "name": "Bad Odoo",
    "summary": "Pure cinema.",
    "author": "Glo Networks",
    "website": "https://www.glo.systems/",
    "category": "Uncategorized",
    "version": "19.0.1.0.0",
    "external_dependencies": {"python": ["pillow"], "bin": ["ffmpeg"]},
    "depends": ["web", "account"],
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
    "license": "LGPL-3",
}
