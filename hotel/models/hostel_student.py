from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import timedelta

class HostelStudent(models.Model):
  _name = "hostel.student"
  _inherit = ['mail.thread.cc', 'mail.thread.main.attachment', 'mail.activity.mixin']
  # _inherit = ['mail.thread', 'mail.activity.mixin'] 
  name = fields.Char("Student Name")

  gender = fields.Selection(
    [
      ("male", "Male"),
      ("female", "Female"),
  ], string="Gender", help="Student gender")
  active = fields.Boolean("Active", default=True, help="Activate/Deactivate hostel record")
  room_id = fields.Many2one("hostel.room", "Room", help="Select hostel room")
  hostel_id = fields.Many2one("hostel.hostel", related='room_id.hostel_id')
  partner_id = fields.Many2one('res.partner', ondelete='cascade', delegate=True, required=True)
  status = fields.Selection(
    [
      ("draft", "Draft"),
      ("reservation", "Reservation"),
      ("pending", "Pending"),
      ("paid", "Done"),
      ("discharge", "Discharge"),
      ("cancel", "Cancel")
    ], string="Status", copy=False, default="draft", help="State of the student hostel")
  admission_date = fields.Date("Admission Date", help="Date of admission in hostel",default=fields.Datetime.today)
  discharge_date = fields.Date("Discharge Date", help="Date on which student discharge")
  duration = fields.Integer("Duration", compute="_compute_check_duration", inverse="_inverse_duration",
                            help="Enter duration of living")
  
  def action_assign_room(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Assign Room'),
            'res_model': 'assign.room.student.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
        }
  
  @api.onchange('admission_date', 'discharge_date')
  def onchange_duration(self):
      if self.discharge_date and self.admission_date:
          self.duration = (
              self.discharge_date.year - \
              self.admission_date.year) * 12 + \
              (self.discharge_date.month - \
              self.admission_date.month)

  def action_remove_room(self):
    if self.env.context.get("is_hostel_room"):
        self.room_id = False
  
  def action_draft(self):
        self.state = 'draft'

  def action_reservation(self):
      self.state = 'reservation'

  def action_pending(self):
      self.state = 'pending'

  def action_done(self):
      self.state = 'done'

  def action_discharge(self):
      self.state = 'discharge'

  def action_cancel(self):
      self.state = 'cancel'
  
  @api.depends("admission_date", "discharge_date")
  def _compute_check_duration(self):
      """Method to check duration"""
      for rec in self:
          if rec.discharge_date and rec.admission_date:rec.duration = (rec.discharge_date - rec.admission_date).days
  def _inverse_duration(self):
      for stu in self:
          if stu.discharge_date and stu.admission_date:
              duration = (stu.discharge_date - stu.admission_date).days
              if duration != stu.duration:stu.discharge_date = (stu.admission_date + timedelta(days=stu.duration)).strftime('%Y-%m-%d')
  
  # def action_assign_room(self):
  #       self.ensure_one()
  #       if self.status != "paid":
  #           raise UserError(_("You can't assign a room if it's not paid."))
  #       room_as_superuser = self.env['hostel.room'].sudo()
  #       room_rec = room_as_superuser.create({
  #           "name": "Room A-103",
  #           "room_number": "A-103",
  #           "floor_number": 1,
  #           "student_per_room": 4,
  #           "rent_amount": 500,
  #           # "category_id": self.env.ref("hotel.single_room_categ").id,
  #           "hostel_id": self.hostel_id.id,
  #       })
  #       if room_rec:
  #           self.room_id = room_rec.id