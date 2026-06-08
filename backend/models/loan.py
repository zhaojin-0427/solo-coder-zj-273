from datetime import datetime
from backend.extensions import db


class LoanRecord(db.Model):
    __tablename__ = 'loan_records'
    id = db.Column(db.Integer, primary_key=True)
    accessory_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=False)
    borrower_name = db.Column(db.String(100), nullable=False)
    borrower_phone = db.Column(db.String(50), default='')
    borrower_contact = db.Column(db.String(200), default='')
    loan_date = db.Column(db.String(20), default='')
    due_date = db.Column(db.String(20), default='')
    return_date = db.Column(db.String(20), default='')
    deposit = db.Column(db.Float, default=0.0)
    deposit_returned = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, default='')
    returned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        from backend.models.accessory import Accessory
        acc = Accessory.query.get(self.accessory_id)
        is_overdue = False
        days_overdue = 0
        if not self.returned and self.due_date:
            try:
                due = datetime.strptime(self.due_date, '%Y-%m-%d')
                today = datetime.now()
                if today > due:
                    is_overdue = True
                    days_overdue = (today - due).days
            except:
                pass
        return {
            'id': self.id,
            'accessory_id': self.accessory_id,
            'accessory': acc.to_dict() if acc else None,
            'borrower_name': self.borrower_name,
            'borrower_phone': self.borrower_phone,
            'borrower_contact': self.borrower_contact,
            'loan_date': self.loan_date,
            'due_date': self.due_date,
            'return_date': self.return_date,
            'deposit': self.deposit,
            'deposit_returned': self.deposit_returned,
            'notes': self.notes,
            'returned': self.returned,
            'is_overdue': is_overdue,
            'days_overdue': days_overdue,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }
