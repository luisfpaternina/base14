#################################################################################
#
#
#
#
#################################################################################
{
    "name": "PoS Order To Sale Order",

    "version": "14.0.0.0.0",

    "author": "Luis Felipe Paternina",

    "category": "Point Of Sale",

    "license": "AGPL-3",

    "depends": ["point_of_sale", "sale"],

    "data": ["views/view_pos_config.xml", "views/assets.xml"],

    "qweb": ["static/src/xml/pos_order_to_sale_order.xml"],

    "installable": True,
}
