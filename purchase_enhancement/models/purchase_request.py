# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError

class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Purchase Request'

    name = fields.Char(string='Request Name', required=True)
    requested_by = fields.Many2one('res.users', string='Requested by', required=True,
                                   default=lambda self: self.env.user)
    start_date = fields.Date(string='Start Date', default=fields.Date.context_today)
    end_date = fields.Date(string='End Date')
    state = fields.Selection([('draft', 'Draft'),('submit_approve', 'Submit For Approval'),('approve', 'Approve'),('cancel','Cancel'),('reject','Reject')], default='draft')
    rejection_reason = fields.Text(string='Rejection Reason', readonly=True)
    orderlines = fields.One2many('purchase.request.line', 'purchase_request_id', string='Order Lines')
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)

    @api.depends('orderlines.total')
    def _compute_total_price(self):
        for request in self:
            request.total_price = sum(line.total for line in request.orderlines)


    def submit_for_approve(self):
        print("submit clicked")
        self.state = 'submit_approve'

    def cancel(self):
        print("cancel clicked")
        self.state = 'cancel'

    def approve(self):
        self.state = 'approve'
        # Define the email details
        subject = "Purchase Request"
        body_html = f"""<p>Hello,</p><p>Purchase Request ({self.name}) has been approved.</p>"""

        # Fetch the purchase manager group
        purchase_manager_group = self.env.ref('purchase.group_purchase_manager')
        if not purchase_manager_group:
            raise UserError("No purchase manager group found.")

        # Get the email addresses of all users in the purchase manager group
        purchase_managers = self.env['res.users'].search([('groups_id', 'in', purchase_manager_group.id)])
        email_to = ','.join(purchase_managers.mapped('email'))
        if not email_to:
            raise UserError("No purchase managers found to send email to.")

        # Create the email values dictionary
        mail_values = {
            'subject': subject,
            'body_html': body_html,
            'email_to': email_to,
            'email_from': self.env.user.email,  # Use the email of the current user
        }

        # Create and send the email
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()

    # def _send_approval_email(self):
    #     template = self.env.ref('purchase_enhancement.email_template_purchase_request_approved')
    #     if template:
    #         purchase_manager_group = self.env.ref('purchase.group_purchase_manager')
    #         purchase_managers = self.env['res.users'].search([('groups_id', 'in', purchase_manager_group.id)])
    #         email_to = ','.join(purchase_managers.mapped('email'))
    #         if not email_to:
    #             raise UserError("No purchase managers found to send email to.")
    #
    #         for manager in purchase_managers:
    #             template.with_context(email_to=manager.email).send_mail(self.id, force_send=True)

    def reject(self):
        print("reject clicked")

    def reset_to_draft(self):
        print("reset clicked")
        self.state = 'draft'



class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'Purchase Request Line'

    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Char(string='Description', related='product_id.name', readonly=True, store=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    cost_price = fields.Float(string='Cost Price', related='product_id.standard_price', readonly=True)
    total = fields.Float(string='Total', compute='_compute_total', store=True)

    @api.depends('quantity', 'cost_price')
    def _compute_total(self):
        for line in self:
            line.total = line.quantity * line.cost_price

