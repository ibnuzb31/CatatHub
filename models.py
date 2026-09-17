from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class KategoriProyek(db.Model):
    __tablename__ = 'kategori_proyek'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_kategori = db.Column(db.String(100), nullable=False, unique=True)
    deskripsi_kategori = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tugas = db.relationship(
        'DaftarTugas',
        back_populates='kategori',
        cascade='all, delete-orphan',
        lazy=True
    )
    logbooks = db.relationship(
        'LogbookPekerjaanHarian',
        back_populates='kategori',
        cascade='all, delete-orphan',
        lazy=True
    )

    def __repr__(self):
        return f'<KategoriProyek {self.nama_kategori}>'


class DaftarTugas(db.Model):
    __tablename__ = 'daftar_tugas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_tugas = db.Column(db.String(200), nullable=False)
    deskripsi_tugas = db.Column(db.Text, nullable=True)
    tenggat_waktu = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='Belum Selesai', nullable=False)
    prioritas = db.Column(db.String(20), default='Medium', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    kategori_id = db.Column(db.Integer, db.ForeignKey('kategori_proyek.id'), nullable=False)
    kategori = db.relationship('KategoriProyek', back_populates='tugas')
    logbooks = db.relationship('LogbookPekerjaanHarian', back_populates='tugas', lazy=True)

    def __repr__(self):
        return f'<DaftarTugas {self.nama_tugas}>'


class LogbookPekerjaanHarian(db.Model):
    __tablename__ = 'logbook_pekerjaan_harian'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tanggal = db.Column(db.Date, nullable=False)
    materi_dipelajari = db.Column(db.String(200), nullable=False)
    pekerjaan = db.Column(db.Text, nullable=False)
    kendala = db.Column(db.Text, nullable=False)
    solusi = db.Column(db.Text, nullable=True)
    target_belajar_besok = db.Column(db.Text, nullable=False)
    durasi_belajar = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    kategori_id = db.Column(db.Integer, db.ForeignKey('kategori_proyek.id'), nullable=False)
    tugas_id = db.Column(db.Integer, db.ForeignKey('daftar_tugas.id'), nullable=True)

    kategori = db.relationship('KategoriProyek', back_populates='logbooks')
    tugas = db.relationship('DaftarTugas', back_populates='logbooks')

    def __repr__(self):
        return f'<LogbookPekerjaanHarian {self.tanggal}>'