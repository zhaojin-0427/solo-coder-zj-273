from datetime import datetime
from backend.extensions import db


class CertificateAttachment(db.Model):
    __tablename__ = 'certificate_attachments'
    id = db.Column(db.Integer, primary_key=True)
    accessory_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=False)
    cert_type = db.Column(db.String(50), default='')
    file_name = db.Column(db.String(200), default='')
    file_path = db.Column(db.String(300), default='')
    cert_number = db.Column(db.String(100), default='')
    issue_date = db.Column(db.String(20), default='')
    issuer = db.Column(db.String(100), default='')
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        from backend.models.accessory import Accessory
        acc = Accessory.query.get(self.accessory_id)
        return {
            'id': self.id,
            'accessory_id': self.accessory_id,
            'accessory': acc.to_dict() if acc else None,
            'cert_type': self.cert_type,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'cert_number': self.cert_number,
            'issue_date': self.issue_date,
            'issuer': self.issuer,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }
