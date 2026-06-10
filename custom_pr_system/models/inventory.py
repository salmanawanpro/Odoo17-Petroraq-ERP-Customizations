from odoo import models, fields, api, _
from odoo.exceptions import UserError

class GrnSes(models.Model):
    _name = "grn.ses"
    _description = "GRN / SES"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Reference", required=True)
    partner_ref = fields.Char(string="Vendor Reference")
    date_order = fields.Date(string="Order Date")
    date_planned = fields.Date(string="Planned Date")
    project = fields.Char(string="Project")
    requested_by = fields.Char(string="Requested By")
    department = fields.Char(string="Department")
    supervisor = fields.Char(string="Supervisor")
    origin = fields.Char(string="Source Document")
    date_request = fields.Date(string="Request Date")
    subtotal = fields.Float(string="Subtotal", compute="_compute_totals", store=True)
    tax_15 = fields.Float(string="VAT 15%", compute="_compute_totals", store=True)
    grand_total = fields.Float(string="Grand Total", compute="_compute_totals", store=True)
    is_reviewed = fields.Boolean("Reviewed", default=False)
    is_approved = fields.Boolean("Approved", default=False)
    line_ids = fields.One2many("grn.ses.line", "order_id", string="GRN/SES Lines")
    stage = fields.Selection(
        [
            ("pending", "Pending"),
            ("reviewed", "Reviewed"),
            ("approved", "Approved"),
        ],
        string="Stage",
        default="pending",
        tracking=True,
    )
    
    
    @api.depends("line_ids.subtotal")
    def _compute_totals(self):
        for rec in self:
            rec.subtotal = sum(line.subtotal for line in rec.line_ids)
            rec.tax_15 = rec.subtotal * 0.15 if rec.subtotal else 0.0
            rec.grand_total = rec.subtotal + rec.tax_15
    def action_review(self):
        """Mark record as reviewed"""
        for rec in self:
            rec.is_reviewed = True
            rec.stage = "reviewed" 
        group = self.env.ref("custom_user_portal.inventory_admin", raise_if_not_found=False)
        if group and group.users:
            for user in group.users:
                rec.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=user.id,
                    summary="Record Reviewed",
                    note=f"Record {rec.display_name} has been reviewed and awaits approval."
                )
        return True

    def action_approve(self):
        """Mark record as approved and update inventory"""
        for rec in self:
            rec.is_approved = True
            rec.stage = "approved"
            
            # Update inventory for material lines
            self._update_inventory_from_grn_ses(rec)
            
            # Notify approvers group
            group = self.env.ref("custom_pr_system.inventory_approver", raise_if_not_found=False)
            if group and group.users:
                for user in group.users:
                    rec.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=user.id,
                        summary="Record Approved",
                        note=f"Record {rec.display_name} has been approved."
                    )

    def _update_inventory_from_grn_ses(self, grn_ses):
        """Update inventory when GRN/SES is approved"""
        env = self.env
        
        # Get stock location
        stock_location = env.ref("stock.stock_location_stock", raise_if_not_found=False)
        if not stock_location:
            stock_location = env["stock.location"].sudo().search([("usage", "=", "internal")], limit=1)
        if not stock_location:
            return  # No stock location found
        
        # Process only material lines
        material_lines = grn_ses.line_ids.filtered(lambda l: l.type == "material")
        
        for line in material_lines:
            if not line.name or line.quantity <= 0:
                continue
                
            # Find or create product
            product_tmpl = env["product.template"].sudo().search([("name", "=", line.name)], limit=1)
            if not product_tmpl:
                product_tmpl = env["product.template"].sudo().create({
                    "name": line.name,
                    "type": "product",
                    "categ_id": env.ref("product.product_category_all").id,
                    "list_price": line.price_unit or 0.0,
                    "standard_price": line.price_unit or 0.0,
                    "sale_ok": True,
                    "purchase_ok": True,
                    "tracking": "none",
                })
            
            product = product_tmpl.product_variant_id
            
            # Update stock
            quant = env["stock.quant"].sudo().search([
                ("product_id", "=", product.id),
                ("location_id", "=", stock_location.id),
            ], limit=1)
            
            if quant:
                quant.sudo().inventory_quantity = quant.quantity + line.quantity
                quant.sudo()._apply_inventory()
            else:
                new_quant = env["stock.quant"].sudo().create({
                    "product_id": product.id,
                    "location_id": stock_location.id,
                    "inventory_quantity": line.quantity,
                })
                new_quant.sudo()._apply_inventory()
            
            # Log in GRN/SES chatter
            grn_ses.message_post(
                body=f"Inventory updated: {line.name} (+{line.quantity} units)",
                message_type="notification",
            )

    def _get_report_base_filename(self):
        """Hide GRN/SES report until approved"""
        self.ensure_one()
        if not self.is_approved:
            return False  # prevents showing in Print dropdown
        return f"{self.name}_Report"
    
    def print_grn_ses_report(self):
        for rec in self:
            if rec.state != "approved":   # change to your real approval field
                raise UserError(_("Reports cannot be downloaded until GRN/SES is approved"))
        return self.env.ref("custom_pr_system.action_report_grn_ses").report_action(self)



class GrnSesLine(models.Model):
    _name = "grn.ses.line"
    _description = "GRN/SES Line"

    order_id = fields.Many2one(
        "grn.ses", string="GRN/SES", ondelete="cascade", required=True
    )
    name = fields.Char(string="Description")
    quantity = fields.Float(string="Quantity")
    unit = fields.Char(string="Unit")
    type = fields.Selection(
        [("material", "Material"), ("service", "Service")],
        string="Type",
        default="material",
        required=True,
    )
    price_unit = fields.Float(string="Unit Price")
    remarks = fields.Char(string="Remarks")
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)

    @api.depends("quantity", "price_unit")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit

class GrnSesWizard(models.TransientModel):
    _name = "grn.ses.wizard"
    _description = "Wizard for GRN/SES Creation"

    remarks = fields.Text(string="Remarks")

    def action_create_grn_ses(self):
        active_id = self.env.context.get("active_id")
        order = self.env["purchase.order"].browse(active_id)

        created_records = []

        # Separate PO lines by type
        material_lines = order.custom_line_ids.filtered(lambda l: l.type == "material")
        service_lines = order.custom_line_ids.filtered(lambda l: l.type == "service")

        # 🚀 Create GRN if material lines exist
        if material_lines:
            grn = self.env["grn.ses"].create(
                {
                    "name": f"GRN for {order.name}",
                    "partner_ref": order.partner_ref,
                    "date_order": order.date_order,
                    "date_planned": order.date_planned,
                    "project": order.project_id.name if order.project_id else False,
                    "requested_by": order.requested_by,
                    "department": order.department,
                    "supervisor": order.supervisor,
                    "origin": order.origin,
                    "date_request": order.date_request,
                }
            )
            grn.write(
                {
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": line.name,
                                "quantity": line.quantity,
                                "unit": line.unit,
                                "type": line.type,
                                "price_unit": line.price_unit,
                                "subtotal": line.subtotal,
                                "remarks": self.remarks,
                            },
                        )
                        for line in material_lines
                    ]
                }
            )
            created_records.append(grn)

        if service_lines:
            ses = self.env["grn.ses"].create(
                {
                    "name": f"SES for {order.name}",
                    "partner_ref": order.partner_ref,
                    "date_order": order.date_order,
                    "date_planned": order.date_planned,
                    "project": order.project_id.name if order.project_id else False,
                    "requested_by": order.requested_by,
                    "department": order.department,
                    "supervisor": order.supervisor,
                    "origin": order.origin,
                    "date_request": order.date_request,
                }
            )
            ses.write(
                {
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": line.name,
                                "quantity": line.quantity,
                                "unit": line.unit,
                                "type": line.type,
                                "price_unit": line.price_unit,
                                "subtotal": line.subtotal,
                                "remarks": self.remarks,
                            },
                        )
                        for line in service_lines
                    ]
                }
            )
            created_records.append(ses)
                # 🚀 Send activity to Inventory QC group after creation
        group = self.env.ref("custom_pr_system.inventory_qc", raise_if_not_found=False)
        if group and group.users:
            for rec in created_records:  # Loop over GRN/SES records
                for user in group.users:
                    rec.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=user.id,
                        summary="GRN/SES Created",
                        note=f"A {rec.name} has been created from Purchase Order {order.name} and requires your QC review."
                    )

        return {"type": "ir.actions.act_window_close"}


class GrnSesReport(models.AbstractModel):
    _name = 'report.custom_pr_system.report_petroraq_grn_ses'
    _description = 'GRN/SES QWeb Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['grn.ses'].browse(docids)
        for rec in docs:
            if not rec.is_approved:  # ✅ check approval before printing
                raise UserError("You can only print the GRN/SES Report after it is approved.")
        return {
            'doc_ids': docids,
            'doc_model': 'grn.ses',
            'docs': docs,
        }
        
        
        
