from datetime import datetime
from backend.extensions import db


class OutfitFavorite(db.Model):
    __tablename__ = 'outfit_favorites'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    occasion = db.Column(db.String(50), default='')
    necklace_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=True)
    earring_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=True)
    bracelet_id = db.Column(db.Integer, db.ForeignKey('accessories.id'), nullable=True)
    main_color = db.Column(db.String(50), default='')
    style = db.Column(db.String(50), default='')
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    use_count = db.Column(db.Integer, default=0)

    def to_dict(self):
        from backend.models.accessory import Accessory
        necklace = Accessory.query.get(self.necklace_id) if self.necklace_id else None
        earring = Accessory.query.get(self.earring_id) if self.earring_id else None
        bracelet = Accessory.query.get(self.bracelet_id) if self.bracelet_id else None
        return {
            'id': self.id,
            'name': self.name,
            'occasion': self.occasion,
            'necklace': necklace.to_dict() if necklace else None,
            'earring': earring.to_dict() if earring else None,
            'bracelet': bracelet.to_dict() if bracelet else None,
            'necklace_id': self.necklace_id,
            'earring_id': self.earring_id,
            'bracelet_id': self.bracelet_id,
            'main_color': self.main_color,
            'style': self.style,
            'notes': self.notes,
            'use_count': self.use_count,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else ''
        }
