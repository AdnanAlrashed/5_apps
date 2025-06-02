from datetime import timedelta
from odoo import _, fields, models, api
import logging
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools.translate import _
_logger = logging.getLogger(__name__)

class HostelRoom(models.Model):
    _name = "hostel.room"
    _inherit = ['base.archive']
    _description = "Information about hostel room"
    _order = "id desc, name"
    sql_constraints = [("room_no_unique", "unique(room_no)", "Room number must be unique!")]
    name = fields.Char(string="Room Name", required=True)
    room_number = fields.Char(string="Room Number", required=True)
    floor_number = fields.Integer(string="Floor Number")
    rent_amount = fields.Monetary('Rent Amount', help="Enterrent amount per month", field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency')
    hostel_id = fields.Many2one("hostel.hostel", "hostel", help="Name of hostel")
    state = fields.Selection(
        [
            ('draft', 'Unavailable'),
            ('available', 'Available'),
            ('closed', 'Closed')], 'State', default="draft")
    
    student_per_room = fields.Integer("Student Per Room",required=True,help="Students allocated per room")
    availability = fields.Float(compute="_compute_check_availability",string="Availability", help="Room availability in hostel")
    student_ids = fields.One2many("hostel.student", "room_id", string="Students", help="Enter students")
    hostel_amenities_ids = fields.Many2many("hostel.amenities", "hostel_room_amenities_rel", "room_id", "amenitiy_id",
                                            string="Amenities", domain="[('active', '=', True)]",
                                            help="Select hostel room amenities")
    
    admission_date = fields.Date("Admission Date", help="Date of admission in hostel", default=fields.Datetime.today)
    discharge_date = fields.Date("Discharge Date", help="Date on which student discharge")
    duration = fields.Integer("Duration", compute="_compute_check_duration",
                              inverse="_inverse_duration", help="Enter duration of living")
    room_category_id = fields.Many2one('hostel.room.category', string='Room Category')
    description = fields.Html('Description')
    room_rating = fields.Float('Hostel Average Rating', digits=(14, 2))
    other_info = fields.Text("Other Information",
                             help="Enter more information")
    is_public = fields.Boolean("Public Hostel", groups="hotel.group_hostel_manager")
    notes = fields.Text("Internal Notes", groups="hotel.group_hostel_manager")
    def action_category_with_amount(self):
        self.ensure_one()

        self.env.cr.execute("""
            SELECT name, amount FROM hostel_room_category WHERE id = %s
        """, (self.room_category_id.id,))
        result = self.env.cr.fetchone()

        # التحقق مما إذا كان `result` يحتوي على بيانات
        if not result:
            _logger.warning("No category found for ID: %s", self.room_category_id.id)
            return {
                'warning': {'title': "Warning", 'message': "No category data found!"}
            }

        name, amount = result  # تفكيك النتيجة بدون أخطاء

        return {
            'name': "Room Category Details",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hostel.room.wizard',
            'target': 'new',
            'context': {
                'default_name': name,
                'default_amount': amount
            }
        }

        
    def action_remove_room_members(self):
        for student in self.student_ids:
            student.with_context(is_hostel_room=True).action_remove_room()

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

    @api.depends("student_per_room", "student_ids")
    def _compute_check_availability(self):
    #"""Method to check room availability"""

        for rec in self:
            rec.availability = rec.student_per_room - len(rec.student_ids.ids)
        
    @api.constrains("rent_amount")
    def _check_rent_amount(self):
        """Constraint on negative rent amount"""
        if self.rent_amount == 0:
            raise ValidationError(_("Rent Amount Per Month should not be a negative value!"))
        
    def filter_members(self):
        all_rooms = self.search([])
        filtered_rooms = self.rooms_with_multiple_members(all_rooms)

        print(filtered_rooms,"fjjfjfjfjfjfjfj")

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [
            ('draft', 'available'),
            ('available', 'closed'),
            ('closed', 'draft')
            ]
        return (old_state, new_state) in allowed
    
    # def change_state(self, new_state):
    #     for room in self:
    #         if room.is_allowed_transition(room.state, new_state):
    #             room.state = new_state
    #         else:
    #             continue


    def change_state(self, new_state):
        for room in self:
            if room.is_allowed_transition(room.state, new_state):
                room.state = new_state
            else:
                msg = _('Moving from %s to %s is notallowed') % (room.state, new_state)
                raise UserError(msg)


    def make_available(self):
        self.change_state('available')
    def make_closed(self):
        self.change_state('closed')