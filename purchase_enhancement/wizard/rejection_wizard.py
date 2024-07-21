# -*- coding: utf-8 -*-

from odoo import api, fields, models

class RejectionWizard(models.TransientModel):
    _name = "rejection.wizard"
    _description = "Wizard for rejection"

    rejection_reason = fields.Text(string="Rejection Reason", required=True)

    def confirm_btn_clicked(self):
        active_id = self.env.context.get('active_id')
        purchase_request = self.env['purchase.request'].browse(active_id)
        if purchase_request:
            purchase_request.write({
                'rejection_reason': self.rejection_reason,
                'state': 'reject'
            })
        return {'type': 'ir.actions.act_window_close'}
        # print("sdhjsfjksf")





        # hospital_patient = self.env['hospital.patient']
        # for patient in self:
        #     hospital_patient.create({
        #         "name": patient.name,
        #         "age": patient.age,
        #     })
        # print("sdhjsfjksf")
