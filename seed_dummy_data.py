from datetime import date, timedelta, datetime

from app import app
from models import DaftarTugas, KategoriProyek, LogbookPekerjaanHarian, db


CATEGORY_NAMES = [
    'Python Dasar',
    'Flask Web Development',
    'Database MySQL',
    'SQLAlchemy ORM',
    'Bootstrap UI',
    'JavaScript Dasar',
    'REST API',
    'Git dan GitHub',
    'Testing Aplikasi',
    'Keamanan Web',
    'Struktur Data',
    'Algoritma',
    'HTML dan CSS',
    'Deployment Lokal',
    'Dokumentasi Proyek',
    'Analisis Kebutuhan',
    'Perancangan Database',
    'Integrasi Sistem',
    'Optimasi Query',
    'Pemeliharaan Aplikasi',
]


def seed_data():
    with app.app_context():
        categories = []
        for index, name in enumerate(CATEGORY_NAMES, start=1):
            category = KategoriProyek.query.filter_by(nama_kategori=f'[DUMMY] {name}').first()
            if category is None:
                category = KategoriProyek(
                    nama_kategori=f'[DUMMY] {name}',
                    deskripsi_kategori=f'Data contoh untuk kategori {name.lower()}.',
                )
                db.session.add(category)
            categories.append(category)

        db.session.flush()

        tasks = []
        for index, category in enumerate(categories, start=1):
            task = DaftarTugas.query.filter_by(nama_tugas=f'[DUMMY] Tugas contoh {index:02d}').first()
            if task is None:
                task = DaftarTugas(
                    nama_tugas=f'[DUMMY] Tugas contoh {index:02d}',
                    deskripsi_tugas=f'Menyelesaikan latihan dan implementasi pada kategori {category.nama_kategori}.',
                    tenggat_waktu=datetime.now() + timedelta(days=index),
                    status='Selesai' if index % 3 == 0 else 'Belum Selesai',
                    prioritas=['Low', 'Medium', 'High'][index % 3],
                    kategori=category,
                )
                db.session.add(task)
            tasks.append(task)

        db.session.flush()

        LogbookPekerjaanHarian.query.filter(
            LogbookPekerjaanHarian.pekerjaan.like('[DUMMY] %')
        ).delete(synchronize_session=False)

        for index, category in enumerate(categories, start=1):
            logbook = LogbookPekerjaanHarian(
                tanggal=date.today() - timedelta(days=index - 1),
                materi_dipelajari=f'Praktik {category.nama_kategori.removeprefix("[DUMMY] ")}',
                pekerjaan=f'[DUMMY] Implementasi latihan nomor {index:02d}.',
                kendala='Menyesuaikan struktur kode dengan kebutuhan fitur.',
                solusi='Membagi pekerjaan menjadi beberapa langkah kecil dan mengujinya.',
                target_belajar_besok='Merapikan hasil implementasi dan menambah pengujian.',
                durasi_belajar=float((index % 4) + 1),
                kategori=category,
                tugas=None if index % 4 == 0 else tasks[index - 1],
            )
            db.session.add(logbook)

        db.session.commit()
        print('Seed selesai: 20 kategori, 20 tugas, dan 20 logbook dummy.')


if __name__ == '__main__':
    seed_data()