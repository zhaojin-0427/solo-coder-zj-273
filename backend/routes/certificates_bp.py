from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import os
import uuid
from backend.extensions import db
from backend.models import CertificateAttachment, Accessory

bp = Blueprint('certificates', __name__, url_prefix='/api')


@bp.route('/certificates', methods=['GET'])
def get_certificates():
    accessory_id = request.args.get('accessory_id', '')
    cert_type = request.args.get('cert_type', '')
    query = CertificateAttachment.query
    if accessory_id:
        query = query.filter_by(accessory_id=int(accessory_id))
    if cert_type:
        query = query.filter_by(cert_type=cert_type)
    records = query.order_by(CertificateAttachment.created_at.desc()).all()
    return jsonify([r.to_dict() for r in records])


@bp.route('/certificates/<int:cid>', methods=['GET'])
def get_certificate(cid):
    record = CertificateAttachment.query.get_or_404(cid)
    return jsonify(record.to_dict())


@bp.route('/certificates', methods=['POST'])
def create_certificate():
    data = request.form.to_dict()
    file_path = ''
    file_name = ''
    if 'file' in request.files:
        f = request.files['file']
        if f and f.filename:
            ext = os.path.splitext(f.filename)[1]
            file_name = f.filename
            file_path = f"cert_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{uuid.uuid4().hex[:8]}{ext}"
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], file_path))

    acc = Accessory.query.get_or_404(data.get('accessory_id'))
    record = CertificateAttachment(
        accessory_id=data.get('accessory_id'),
        cert_type=data.get('cert_type', ''),
        file_name=file_name,
        file_path=file_path,
        cert_number=data.get('cert_number', ''),
        issue_date=data.get('issue_date', ''),
        issuer=data.get('issuer', ''),
        notes=data.get('notes', '')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@bp.route('/certificates/<int:cid>', methods=['PUT'])
def update_certificate(cid):
    record = CertificateAttachment.query.get_or_404(cid)
    data = request.form.to_dict()
    if 'file' in request.files:
        f = request.files['file']
        if f and f.filename:
            if record.file_path:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], record.file_path)
                if os.path.exists(old_path):
                    os.remove(old_path)
            ext = os.path.splitext(f.filename)[1]
            record.file_name = f.filename
            record.file_path = f"cert_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{uuid.uuid4().hex[:8]}{ext}"
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], record.file_path))
    fields = ['cert_type', 'cert_number', 'issue_date', 'issuer', 'notes']
    for f in fields:
        if f in data:
            setattr(record, f, data[f])
    db.session.commit()
    return jsonify(record.to_dict())


@bp.route('/certificates/<int:cid>', methods=['DELETE'])
def delete_certificate(cid):
    record = CertificateAttachment.query.get_or_404(cid)
    if record.file_path:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], record.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '已删除'})
