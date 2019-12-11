from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning ,UserError, ValidationError
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_round, float_compare

#################################################################################################################
#################################################################################################################


class Request(models.Model):
	_name = 'fin.price'
	_description= "Price Convert Information"
	name = fields.Char(string='Name',required=True)
	date = fields.Date(string="Date",default=fields.Date.today(),required=True)
	pr_us = fields.Float(string='US')
	pr_sd = fields.Float(string='SD')

#################################################################################################################
# Create the fin.user model
#################################################################################################################

class checklabuser(models.Model):
	_name = 'fin.user'
	_description= "User Fin App"
	name = fields.Char(string="Name",required=True)
	email = fields.Char(string='E-Mail',required=True)
	passw = fields.Char(string='Password',required=True)
	user_id = fields.Many2one('res.users',string='User ID',readonly=True)
	group_id = fields.Many2one('res.groups',string='Access Group',domain="[('category_id.name','=','Fin App')]")
	created = fields.Boolean(string='Created',readonly=True)

	@api.one
	def add_user(self):
		if self.name and self.email and self.passw and self.group_id:
			list_group = []
			list_group.append(self.group_id.id)
			if not self.user_id:
				self.user_id = self.user_id.create({'name':self.name,'login':self.email,'password':self.passw,'groups_id':[(6,0,list_group)]})
				self.created = True
			else:
				self.user_id.write({'name': self.name, 'login': self.email, 'password': self.passw,'groups_id':[(6,0,list_group)]})
		return self.user_id

	@api.one
	def check_group(self):
		pass

#################################################################################################################
# inherit the sale.order.line model
#################################################################################################################

# class edit_app_sale_order_line(models.Model):
# 	_inherit = 'sale.order.line'
# 	size_package = fields.Float(string='Size Package',store=True,readonly=True,related='product_packaging.qty')
# 	num_package = fields.Float(string='Num Package')

# 	@api.one
# 	@api.constrains('price_unit')
# 	def check_qty_pro(self):
# 		if self.product_id.lst_price < self.price_unit:
# 			raise ValidationError(_("Min Price Error"))

# 	@api.one
# 	@api.depends('num_package')
# 	def update_qty_pro(self):
# 		if self.product_packaging.qty and self.num_package:
# 			self.product_uom_qty = self.product_packaging.qty * self.num_package
# 		return True

# 	#@api.one
# 	@api.onchange('num_package')
# 	def change_qty_pro(self):
# 		if self.product_id and self.product_packaging and self.product_packaging.qty and self.num_package:
# 			self.product_uom_qty = self.product_packaging.qty * self.num_package

#################################################################################################################
# inherit the product.template model
##################################################################################################################

class productTemplateInherit(models.Model):
	_inherit = 'product.template'

	is_car = fields.Boolean(string="This Product is Car")
	chassis_no = fields.Char(string="Chassis No.", copy=False)
	car_model_id = fields.Many2one("car.mod", string="Model of Car")

#################################################################################################################
# Car Model model
#################################################################################################################

class Car(models.Model):
	_name = 'car.mod'
	_rec_name = 'car_model'

	car_model = fields.Char(string="Model of Car")

#################################################################################################################
# inherit the account.payment model
#################################################################################################################

class edit_app_account_payment(models.Model):
	_inherit = 'account.payment'
	date_bank = fields.Date(string="Recive Date",default=fields.Date.today(),required=True)
	type_journal = fields.Selection([('bank','Bank'),('cash','Cash')],string='Type Journal',related='journal_id.type')

#################################################################################################################
# inherit the stock.picking model
#################################################################################################################

class stockPickingInherit(models.Model):
	_inherit = 'stock.picking'

	delay_tm = fields.Float(string="Delay", readonly=True)

	@api.depends('date_done', 'scheduled_date')
	@api.one
	def calc_delay_per_minutes(self):
		fmt = '%Y-%m-%d %H:%M:%S'
		delay_time = 0.1
		shed_date = self.scheduled_date
		done = self.date_done
		difference = 0
		if shed_date and done is True:
			schedule = datetime.strptime(str(shed_date).split(".")[0], fmt)
			done_date = datetime.strptime(str(done).split(".")[0], fmt)
			sc = schedule.day
			dd = done_date.day
			print("sssssssssssssss : ", sc)
			print("dddddddddddd : ", dd)
			if dd > sc:
				difference = dd - sc
				delay_time = (difference * 24) * 60
				self.write({'delay_tm' : delay_time})
			else:
				return delay_time

		print("differ : 7200")
		print(difference)
		print("delay time : #############")
		print(self.delay_tm)
		return self.delay_tm

#################################################################################################################
# inherit the pos.session model
#################################################################################################################

# class edit_app_pos(models.Model):
# 	_inherit = 'pos.session'
#
# 	@api.multi
# 	def action_pos_session_close(self):
# 		# Close CashBox
# 		for session in self:
# 			company_id = session.config_id.company_id.id
# 			ctx = dict(self.env.context, force_company=company_id, company_id=company_id)
# 			for st in session.statement_ids:
# 				if abs(st.difference) > st.journal_id.amount_authorized_diff:
# 					# The pos manager can close statements with maximums.
# 					if not self.user_has_groups("point_of_sale.group_pos_manager"):
# 						raise UserError(_("Your ending balance is too different from the theoretical cash closing (%.2f), the maximum allowed is: %.2f. You can contact your manager to force it.") % (st.difference, st.journal_id.amount_authorized_diff))
# 				if (st.journal_id.type not in ['bank', 'cash']):
# 					raise UserError(_("The journal type for your payment method should be bank or cash."))
# 				st.with_context(ctx).sudo().button_confirm_bank()
# 		self.with_context(ctx)._confirm_orders()
# 		self.write({'state': 'closed'})
# 		return {
# 			'type': 'ir.actions.client',
# 			'name': 'Point of Sale Menu',
# 			'tag': 'reload',
# 			'params': {'menu_id': self.env.ref('fin_app.app_pos_system_menu').id},
# 		}