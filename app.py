from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for

from models import DaftarTugas, KategoriProyek, LogbookPekerjaanHarian, db

app = Flask(__name__)
app.secret_key = 'project_database_week2_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/db_manajemen_tugas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


def parse_datetime(value):
    if not value:
        raise ValueError('Tanggal dan waktu harus diisi.')
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M')
    except ValueError:
        raise ValueError('Format tanggal tidak valid. Gunakan format YYYY-MM-DDTHH:MM.')


def parse_date(value):
    if not value:
        raise ValueError('Tanggal harus diisi.')
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError('Format tanggal tidak valid. Gunakan format YYYY-MM-DD.')


@app.route('/')
def index():
    kategori_tersedia = KategoriProyek.query.order_by(KategoriProyek.nama_kategori.asc()).all()
    daftar_tugas = DaftarTugas.query.order_by(DaftarTugas.tenggat_waktu.asc()).all()
    return render_template('index.html', kategori=kategori_tersedia, tugas=daftar_tugas)


@app.route('/tambah', methods=['POST'])
def tambah_tugas():
    nama = (request.form.get('nama_tugas') or '').strip()
    deskripsi = (request.form.get('deskripsi_tugas') or '').strip()
    tenggat_str = request.form.get('tenggat_waktu')
    kategori_id = request.form.get('kategori_id')
    prioritas = (request.form.get('prioritas') or 'Medium').strip()

    if not nama:
        flash('Nama tugas tidak boleh kosong.', 'danger')
        return redirect(url_for('index'))

    if not kategori_id:
        flash('Pilih kategori proyek terlebih dahulu.', 'danger')
        return redirect(url_for('index'))

    try:
        tenggat_obj = parse_datetime(tenggat_str)
    except ValueError as exc:
        flash(str(exc), 'danger')
        return redirect(url_for('index'))

    tugas_baru = DaftarTugas(
        nama_tugas=nama,
        deskripsi_tugas=deskripsi,
        tenggat_waktu=tenggat_obj,
        kategori_id=int(kategori_id),
        prioritas=prioritas,
        status='Belum Selesai'
    )
    db.session.add(tugas_baru)
    db.session.commit()
    flash('Tugas berhasil ditambahkan.', 'success')
    return redirect(url_for('index'))


@app.route('/tambah_kategori', methods=['POST'])
def tambah_kategori():
    nama_kategori_baru = (request.form.get('nama_kategori') or '').strip()
    deskripsi_baru = (request.form.get('deskripsi_kategori') or '').strip()

    if not nama_kategori_baru:
        flash('Nama kategori tidak boleh kosong.', 'danger')
        return redirect(url_for('index'))

    kategori_ada = KategoriProyek.query.filter_by(nama_kategori=nama_kategori_baru).first()
    if kategori_ada:
        flash('Kategori sudah tersedia.', 'warning')
        return redirect(url_for('index'))

    kategori_baru = KategoriProyek(
        nama_kategori=nama_kategori_baru,
        deskripsi_kategori=deskripsi_baru
    )
    db.session.add(kategori_baru)
    db.session.commit()
    flash('Kategori berhasil ditambahkan.', 'success')
    return redirect(url_for('index'))


@app.route('/hapus_kategori', methods=['POST'])
@app.route('/hapus_kategori/<int:id>', methods=['POST'])
def hapus_kategori(id=None):
    kategori_id = request.form.get('kategori_id')
    if kategori_id:
        id = int(kategori_id)

    if id is None:
        flash('Pilih kategori yang ingin dihapus.', 'warning')
        return redirect(url_for('index'))

    kategori = KategoriProyek.query.get_or_404(id)

    for tugas in kategori.tugas:
        db.session.delete(tugas)

    for logbook in kategori.logbooks:
        db.session.delete(logbook)

    db.session.delete(kategori)
    db.session.commit()
    flash('Kategori berhasil dihapus.', 'success')
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_tugas(id):
    tugas_terpilih = DaftarTugas.query.get_or_404(id)

    if request.method == 'POST':
        nama = (request.form.get('nama_tugas') or '').strip()
        deskripsi = (request.form.get('deskripsi_tugas') or '').strip()
        tenggat_str = request.form.get('tenggat_waktu')
        kategori_id = request.form.get('kategori_id')
        prioritas = (request.form.get('prioritas') or 'Medium').strip()

        if not nama:
            flash('Nama tugas tidak boleh kosong.', 'danger')
            return redirect(url_for('edit_tugas', id=id))

        if not kategori_id:
            flash('Kategori tugas harus dipilih.', 'danger')
            return redirect(url_for('edit_tugas', id=id))

        try:
            tenggat_obj = parse_datetime(tenggat_str)
        except ValueError as exc:
            flash(str(exc), 'danger')
            return redirect(url_for('edit_tugas', id=id))

        tugas_terpilih.nama_tugas = nama
        tugas_terpilih.deskripsi_tugas = deskripsi
        tugas_terpilih.tenggat_waktu = tenggat_obj
        tugas_terpilih.kategori_id = int(kategori_id)
        tugas_terpilih.prioritas = prioritas

        db.session.commit()
        flash('Tugas berhasil diperbarui.', 'success')
        return redirect(url_for('index'))

    kategori_tersedia = KategoriProyek.query.order_by(KategoriProyek.nama_kategori.asc()).all()
    return render_template('edit.html', tugas=tugas_terpilih, kategori=kategori_tersedia)


@app.route('/selesai/<int:id>', methods=['POST'])
def selesai_tugas(id):
    tugas = DaftarTugas.query.get_or_404(id)
    tugas.status = 'Selesai'
    db.session.commit()
    flash('Status tugas berhasil diperbarui menjadi selesai.', 'success')
    return redirect(url_for('index'))


@app.route('/hapus/<int:id>', methods=['POST'])
def hapus_tugas(id):
    tugas = DaftarTugas.query.get_or_404(id)
    db.session.delete(tugas)
    db.session.commit()
    flash('Tugas berhasil dihapus.', 'success')
    return redirect(url_for('index'))


@app.route('/logbook', methods=['GET', 'POST'])
def logbook():
    kategori_tersedia = KategoriProyek.query.order_by(KategoriProyek.nama_kategori.asc()).all()
    daftar_tugas = DaftarTugas.query.order_by(DaftarTugas.tenggat_waktu.asc()).all()

    ringkasan_kategori = db.session.query(
        KategoriProyek.nama_kategori,
        db.func.count(LogbookPekerjaanHarian.id).label('jumlah_log'),
        db.func.coalesce(db.func.sum(LogbookPekerjaanHarian.durasi_belajar), 0).label('total_jam')
    ).outerjoin(LogbookPekerjaanHarian, LogbookPekerjaanHarian.kategori_id == KategoriProyek.id) \
        .group_by(KategoriProyek.id, KategoriProyek.nama_kategori) \
        .order_by(KategoriProyek.nama_kategori.asc()) \
        .all()

    if request.method == 'POST':
        tanggal = request.form.get('tanggal')
        materi = (request.form.get('materi_dipelajari') or '').strip()
        pekerjaan = (request.form.get('pekerjaan') or '').strip()
        kendala = (request.form.get('kendala') or '').strip()
        solusi = (request.form.get('solusi') or '').strip()
        target = (request.form.get('target_belajar_besok') or '').strip()
        durasi = request.form.get('durasi_belajar')
        kategori_id = request.form.get('kategori_id')
        tugas_id = request.form.get('tugas_id')

        if not tanggal or not materi or not pekerjaan or not kendala or not target or not durasi or not kategori_id:
            flash('Tanggal, materi, pekerjaan, kendala, target, durasi, dan kategori wajib diisi.', 'danger')
            return redirect(url_for('logbook'))

        try:
            tanggal_obj = parse_date(tanggal)
            durasi_value = float(durasi)
        except ValueError as exc:
            flash(str(exc), 'danger')
            return redirect(url_for('logbook'))

        catatan = LogbookPekerjaanHarian(
            tanggal=tanggal_obj,
            materi_dipelajari=materi,
            pekerjaan=pekerjaan,
            kendala=kendala,
            solusi=solusi if solusi else None,
            target_belajar_besok=target,
            durasi_belajar=durasi_value,
            kategori_id=int(kategori_id),
            tugas_id=int(tugas_id) if tugas_id else None
        )
        db.session.add(catatan)
        db.session.commit()
        flash('Logbook pekerjaan harian berhasil disimpan.', 'success')
        return redirect(url_for('logbook'))

    logbook_list = LogbookPekerjaanHarian.query.order_by(LogbookPekerjaanHarian.tanggal.desc()).all()
    return render_template(
        'logbook.html',
        logbooks=logbook_list,
        kategori=kategori_tersedia,
        tugas=daftar_tugas,
        ringkasan_kategori=ringkasan_kategori
    )


@app.route('/logbook/edit/<int:id>', methods=['GET', 'POST'])
def edit_logbook(id):
    item = LogbookPekerjaanHarian.query.get_or_404(id)
    kategori_tersedia = KategoriProyek.query.order_by(KategoriProyek.nama_kategori.asc()).all()
    daftar_tugas = DaftarTugas.query.order_by(DaftarTugas.tenggat_waktu.asc()).all()

    if request.method == 'POST':
        tanggal = request.form.get('tanggal')
        materi = (request.form.get('materi_dipelajari') or '').strip()
        pekerjaan = (request.form.get('pekerjaan') or '').strip()
        kendala = (request.form.get('kendala') or '').strip()
        solusi = (request.form.get('solusi') or '').strip()
        target = (request.form.get('target_belajar_besok') or '').strip()
        durasi = request.form.get('durasi_belajar')
        kategori_id = request.form.get('kategori_id')
        tugas_id = request.form.get('tugas_id')

        if not tanggal or not materi or not pekerjaan or not kendala or not target or not durasi or not kategori_id:
            flash('Semua field penting harus diisi.', 'danger')
            return redirect(url_for('edit_logbook', id=item.id))

        try:
            item.tanggal = parse_date(tanggal)
            item.durasi_belajar = float(durasi)
        except ValueError as exc:
            flash(str(exc), 'danger')
            return redirect(url_for('edit_logbook', id=item.id))

        item.materi_dipelajari = materi
        item.pekerjaan = pekerjaan
        item.kendala = kendala
        item.solusi = solusi if solusi else None
        item.target_belajar_besok = target
        item.kategori_id = int(kategori_id)
        item.tugas_id = int(tugas_id) if tugas_id else None

        db.session.commit()
        flash('Logbook berhasil diperbarui.', 'success')
        return redirect(url_for('logbook'))

    return render_template('logbook_edit.html', logbook=item, kategori=kategori_tersedia, tugas=daftar_tugas)


@app.route('/logbook/hapus/<int:id>', methods=['POST'])
def hapus_logbook(id):
    item = LogbookPekerjaanHarian.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Logbook berhasil dihapus.', 'success')
    return redirect(url_for('logbook'))


if __name__ == '__main__':
    app.run(debug=True)