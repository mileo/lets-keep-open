# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import locale
from openerp.osv import osv, fields


class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'percentual_iss': fields.float('Percentual ISS'),
        'percentual_irrf': fields.float('Percentual IRRF'),
        'percentual_pcc': fields.float('Percentual PCC'),
    }

    def get_commission(self, cr, uid, ids, start_date, end_date, context=None):
        sql = "select 'produto' as produto, rp.cnpj_cpf, rp.legal_name, \
            ai.date_due, cpcr.date, \
            cpcr.received, cpcr.perc_commission, cpcr.value_commission \
            from contract_partner_commission_report cpcr \
            inner join res_partner rp on cpcr.customer_id = rp.id \
            inner join account_invoice ai on cpcr.invoice_id = ai.id \
            where cpcr.date between '2016-09-01' and '2016-09-30' \
            and cpcr.partner_id = %s and cpcr.state = 'paid'"

        cr.execute(sql % ids[0])
        resultados = cr.fetchall()

        locale.setlocale(locale.LC_ALL, 'pt_BR')

        comissoes = [{
            'produto': x[0],
            'cnpj': x[1],
            'cliente': x[2],
            'vencimento': x[3],
            'pagamento': x[4],
            'mensalidade': locale.format_string("R$ %.2f", x[5]),
            'percentual': locale.format_string("%.0f%%", x[6]),
            'valor': locale.format_string("R$ %.2f", x[7]),
            'valor_decimal': x[7],
        } for x in resultados]
        bruto = sum(x['valor_decimal'] for x in comissoes)

        partner = self.browse(cr, uid, ids[0], context)
        impostos = {'iss': locale.format_string(
                        "%.2f", (bruto * partner.percentual_iss / 100)),
                    'perc_iss': locale.format_string(
                        "%.2f", (partner.percentual_iss)),
                    'irrf': locale.format_string(
                        "%.2f", (bruto * partner.percentual_irrf / 100)),
                    'perc_irrf': locale.format_string(
                        "%.2f", (partner.percentual_irrf)),
                    'pcc': locale.format_string(
                        "%.2f", (bruto * partner.percentual_pcc / 100)),
                    'perc_pcc': locale.format_string(
                        "%.2f", (partner.percentual_pcc))}

        liquido = bruto - round(bruto * partner.percentual_iss / 100, 2)
        liquido -= round(bruto * partner.percentual_irrf / 100, 2)
        liquido -= round(bruto * partner.percentual_pcc / 100, 2)

        impostos['total'] = bruto - liquido

        bruto = locale.format_string("%.2f", bruto)
        liquido = locale.format_string("%.2f", liquido)
        return comissoes, bruto, impostos, liquido