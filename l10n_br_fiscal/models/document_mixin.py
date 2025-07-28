# Copyright (C) 2019  Renato Lima - Akretion <renato.lima@akretion.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from ..constants.fiscal import (
    DOCUMENT_ISSUER,
    DOCUMENT_ISSUER_COMPANY,
    FINAL_CUSTOMER,
    FINAL_CUSTOMER_YES,
    FISCAL_COMMENT_DOCUMENT,
    NFE_IND_PRES,
    NFE_IND_PRES_DEFAULT,
)


class FiscalDocumentMixin(models.AbstractModel):
    """
    Provides a collection of reusable methods for Brazilian fiscal document logic.

    This abstract model is intended to be inherited by other models or mixins
    that require fiscal document functionalities, such as preparing fiscal data,
    calculating fiscal amounts, managing document series, and handling comments.

    It is inherited by sale.order, purchase.order, account.move and even stock.picking
    in separate modules. Indeed these business documents need to take care of
    some fiscal parameters before creating Fiscal Documents. And of course,
    Fiscal Document themselves inherit from this mixin.

    Key functionalities include:
    - Computation of various fiscal amounts based on document lines.
    - Inverse methods for distributing header-level costs (freight, insurance)
      to lines.
    - Hooks for customizing data retrieval (e.g., lines, fiscal partner).
    - Onchange helpers for common fiscal fields.

    Models using this mixin are often expected to also include fields defined
    in `l10n_br_fiscal.document.mixin` for methods like
    `_prepare_br_fiscal_dict` and `_get_amount_fields` to function
    correctly. Line-based calculations typically rely on an overrideable
    `_get_amount_lines` method.
    """

    _name = "l10n_br_fiscal.document.mixin"
    _inherit = "l10n_br_fiscal.document.mixin.methods"
    _description = "Document Fiscal Mixin Fields"

    def _date_server_format(self):
        return fields.Datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @api.model
    def _default_operation(self):
        return False

    @api.model
    def _operation_domain(self):
        domain = (
            "[('state', '=', 'approved'),"
            "'|',"
            f"('company_id', '=', {self.env.company.id}),"
            "('company_id', '=', False),"
        )
        return domain

    fiscal_operation_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.operation",
        string="Operation",
        domain=lambda self: self._operation_domain(),
        default=_default_operation,
    )

    operation_name = fields.Char(
        copy=False,
        compute="_compute_operation_name",
    )

    #
    # Company and Partner are defined here to avoid warnings on runbot
    #
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        index=True,
    )

    fiscal_operation_type = fields.Selection(
        related="fiscal_operation_id.fiscal_operation_type",
        readonly=True,
    )

    ind_pres = fields.Selection(
        selection=NFE_IND_PRES,
        string="Buyer Presence",
        default=NFE_IND_PRES_DEFAULT,
    )

    comment_ids = fields.Many2many(
        comodel_name="l10n_br_fiscal.comment",
        string="Comments",
        domain=[("object", "=", FISCAL_COMMENT_DOCUMENT)],
        compute="_compute_comment_ids",
        store=True,
    )

    fiscal_additional_data = fields.Text()

    manual_fiscal_additional_data = fields.Text(
        help="Fiscal Additional data manually entered by user",
    )

    customer_additional_data = fields.Text()

    manual_customer_additional_data = fields.Text(
        help="Customer Additional data manually entered by user",
    )

    ind_final = fields.Selection(
        selection=FINAL_CUSTOMER,
        string="Final Consumption Operation",
        default=FINAL_CUSTOMER_YES,
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
    )

    amount_price_gross = fields.Monetary(
        compute="_compute_fiscal_amount",
        store=True,
        string="Amount Gross",
        help="Amount without discount.",
    )

    amount_untaxed = fields.Monetary(
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_icms_base = fields.Monetary(
        string="ICMS Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_icms_value = fields.Monetary(
        string="ICMS Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_icmsst_base = fields.Monetary(
        string="ICMS ST Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_icmsst_value = fields.Monetary(
        string="ICMS ST Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_icmssn_credit_value = fields.Monetary(
        string="ICMSSN Credit Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_icmsfcp_base = fields.Monetary(
        string="ICMS FCP Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_icmsfcp_value = fields.Monetary(
        string="ICMS FCP Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_icmsfcpst_value = fields.Monetary(
        string="ICMS FCP ST Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_icms_destination_value = fields.Monetary(
        string="ICMS Destination Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_icms_origin_value = fields.Monetary(
        string="ICMS Origin Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_ipi_base = fields.Monetary(
        string="IPI Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_ipi_value = fields.Monetary(
        string="IPI Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_ii_base = fields.Monetary(
        string="II Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_ii_value = fields.Monetary(
        string="II Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_ii_customhouse_charges = fields.Monetary(
        string="Customhouse Charges",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_pis_base = fields.Monetary(
        string="PIS Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_pis_value = fields.Monetary(
        string="PIS Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_pisst_base = fields.Monetary(
        string="PIS ST Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_pisst_value = fields.Monetary(
        string="PIS ST Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_pis_wh_base = fields.Monetary(
        string="PIS Ret Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_pis_wh_value = fields.Monetary(
        string="PIS Ret Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_cofins_base = fields.Monetary(
        string="COFINS Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_cofins_value = fields.Monetary(
        string="COFINS Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_cofinsst_base = fields.Monetary(
        string="COFINS ST Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_cofinsst_value = fields.Monetary(
        string="COFINS ST Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_cofins_wh_base = fields.Monetary(
        string="COFINS Ret Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_cofins_wh_value = fields.Monetary(
        string="COFINS Ret Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_issqn_base = fields.Monetary(
        string="ISSQN Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_issqn_value = fields.Monetary(
        string="ISSQN Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_issqn_wh_base = fields.Monetary(
        string="ISSQN Ret Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_issqn_wh_value = fields.Monetary(
        string="ISSQN Ret Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_csll_base = fields.Monetary(
        string="CSLL Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_csll_value = fields.Monetary(
        string="CSLL Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_csll_wh_base = fields.Monetary(
        string="CSLL Ret Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_csll_wh_value = fields.Monetary(
        string="CSLL Ret Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_irpj_base = fields.Monetary(
        string="IRPJ Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_irpj_value = fields.Monetary(
        string="IRPJ Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_irpj_wh_base = fields.Monetary(
        string="IRPJ Ret Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_irpj_wh_value = fields.Monetary(
        string="IRPJ Ret Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_inss_base = fields.Monetary(
        string="INSS Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_inss_value = fields.Monetary(
        string="INSS Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_inss_wh_base = fields.Monetary(
        string="INSS Ret Base",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_inss_wh_value = fields.Monetary(
        string="INSS Ret Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_estimate_tax = fields.Monetary(
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_tax = fields.Monetary(
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_total = fields.Monetary(
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_tax_withholding = fields.Monetary(
        string="Tax Withholding",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_financial_total = fields.Monetary(
        string="Amount Financial",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_discount_value = fields.Monetary(
        string="Amount Discount",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_financial_total_gross = fields.Monetary(
        string="Amount Financial Gross",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_financial_discount_value = fields.Monetary(
        string="Financial Discount Value",
        compute="_compute_fiscal_amount",
        store=True,
    )

    amount_insurance_value = fields.Monetary(
        string="Insurance Value",
        compute="_compute_fiscal_amount",
        store=True,
        inverse="_inverse_amount_insurance",
    )

    amount_other_value = fields.Monetary(
        string="Other Costs",
        compute="_compute_fiscal_amount",
        store=True,
        inverse="_inverse_amount_other",
    )

    amount_freight_value = fields.Monetary(
        string="Freight Value",
        compute="_compute_fiscal_amount",
        store=True,
        inverse="_inverse_amount_freight",
    )

    # Usado para tornar Somente Leitura os campos totais dos custos
    # de entrega quando a definição for por Linha
    delivery_costs = fields.Selection(
        related="company_id.delivery_costs",
    )

    force_compute_delivery_costs_by_total = fields.Boolean(default=False)

    issuer = fields.Selection(
        selection=DOCUMENT_ISSUER,
        default=DOCUMENT_ISSUER_COMPANY,
    )

    document_type_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.document.type",
    )

    document_serie_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.document.serie",
        domain="[('active', '=', True)," "('document_type_id', '=', document_type_id)]",
        compute="_compute_document_serie_id",
        store=True,
    )

    document_serie = fields.Char(
        string="Serie Number",
        compute="_compute_document_serie",
        store=True,
    )

    document_number = fields.Char(
        copy=False,
        index=True,
        unaccent=False,
    )

    document_key = fields.Char(
        string="Key",
        copy=False,
        index=True,
        unaccent=False,
    )

    key_random_code = fields.Char(string="Document Key Random Code")
    key_check_digit = fields.Char(string="Document Key Check Digit")
    total_weight = fields.Float()
