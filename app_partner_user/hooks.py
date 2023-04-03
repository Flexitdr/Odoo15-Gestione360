# -*- coding: utf-8 -*-

# Created on 2018-10-12
# author: 广州尚鹏，https://www.sunpop.cn
# email: 300883@qq.com
# resource of Sunpop
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# Odoo在线中文用户手册（长期更新）
# https://www.sunpop.cn/documentation/user/10.0/zh_CN/index.html

# Odoo10离线中文用户手册下载
# https://www.sunpop.cn/odoo10_user_manual_document_offline/
# Odoo10离线开发手册下载-含python教程，jquery参考，Jinja2模板，PostgresSQL参考（odoo开发必备）
# https://www.sunpop.cn/odoo10_developer_document_offline/
# description:

def pre_init_hook(cr):
    pass
    # cr.execute("")

def post_init_hook(cr, registry):
    # todo: 更新当前所有 res.partner
    cr.execute("UPDATE res_partner set is_user = true, related_user_id = u.id "
               "from res_users u where res_partner.id = u.partner_id;")
    pass
