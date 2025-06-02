# hooks.py

def post_init_hook(env):
    cr = env.cr
    from odoo import SUPERUSER_ID, api
    env = api.Environment(cr, SUPERUSER_ID, {})

    # جلب كل التذاكر
    tickets = env['docflex.ticket'].sudo().search([])
    last_numbers = {}

    for ticket in tickets:
        if not ticket.number:
            continue

        # محاولة استخلاص الرقم من نهاية التسلسل
        try:
            base_parts = ticket.number.split('/')
            seq_num = int(base_parts[-1])
            sequence_key = '/'.join(base_parts[:-1])  # مثال: IN/FAX/2025

            if sequence_key not in last_numbers:
                last_numbers[sequence_key] = seq_num
            else:
                last_numbers[sequence_key] = max(last_numbers[sequence_key], seq_num)
        except Exception:
            continue  # تجاهل أي أرقام غير متوافقة

    # تحديث ir.sequence
    for seq_prefix, last_num in last_numbers.items():
        # بناء كود السلسلة بنفس النمط المستخدم في _get_next_number
        parts = seq_prefix.split('/')
        if len(parts) != 3:
            continue  # غير متوافق

        type_code, section_code, year = parts
        user_ids = tickets.filtered(lambda t: t.number.startswith(seq_prefix)).mapped('user_id').ids

        for user_id in set(user_ids):
            sequence_code = f"docflex.ticket.{type_code.lower()}.{section_code.lower()}.{year}.{user_id}"
            sequence = env['ir.sequence'].sudo().search([('code', '=', sequence_code)], limit=1)

            if sequence:
                sequence.sudo().write({
                    'number_next': last_num + 1
                })


def uninstall_hook(env):
    cr = env.cr

    # حذف قيد UNIQUE
    cr.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'docflex_ticket_number_unique'
                  AND table_name = 'docflex_ticket'
            ) THEN
                ALTER TABLE docflex_ticket DROP CONSTRAINT docflex_ticket_number_unique;
            END IF;
        END;
        $$;
    """)

    # حذف جميع التسلسلات المرتبطة
    cr.execute("""
        DELETE FROM ir_sequence WHERE code LIKE 'docflex.ticket.%';
    """)

    # حماية بيانات النماذج المحددة
    protected_models = [
        'docflex.ticket',
        'docflex.ticket.stage',
        'referral.type',
        'ticket.classification',
        'ticket.module',
        'ticket.priority',
        'ticket.section',
        'ticket.security',
        'ticket.status',
        'ticket.summary',
        'docflex.tag',
        'ticket.type'
    ]

    for model in protected_models:
        cr.execute("""
            UPDATE ir_model_data
            SET noupdate = TRUE
            WHERE model = %s;
        """, (model,))
