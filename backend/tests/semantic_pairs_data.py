# (a, b, label, lang, kind). label 1 = parafrase/makna sama, 0 = bukan.
ID_POS = [
 ("Penelitian ini bertujuan untuk mengetahui pengaruh media sosial terhadap prestasi belajar siswa.", "Tujuan studi ini adalah melihat dampak media sosial pada hasil belajar para siswa."),
 ("Algoritma Winnowing memilih nilai hash minimum pada setiap jendela.", "Pada tiap jendela, algoritma Winnowing mengambil hash yang paling kecil."),
 ("Kenaikan harga bahan bakar menyebabkan inflasi meningkat tajam.", "Inflasi melonjak karena harga bahan bakar naik."),
 ("Sebagian besar responden menyatakan puas dengan layanan tersebut.", "Mayoritas peserta survei mengaku puas terhadap pelayanan itu."),
 ("Model bahasa besar sering menghasilkan teks dengan pola kalimat yang seragam.", "Teks buatan model bahasa besar cenderung memiliki pola kalimat yang monoton."),
 ("Pemerintah berencana membangun jalur kereta baru di wilayah timur.", "Rencana pemerintah adalah membuat rel kereta api baru di bagian timur."),
 ("Hasil eksperimen menunjukkan bahwa akurasi sistem mencapai sembilan puluh persen.", "Percobaan memperlihatkan sistem memiliki ketepatan sebesar 90 persen."),
 ("Pengguna wajib memverifikasi alamat surel sebelum dapat masuk ke akun.", "Sebelum login, pengguna harus mengonfirmasi alamat email mereka."),
 ("Perubahan iklim mengancam produksi pangan di banyak negara berkembang.", "Produksi pangan di sejumlah negara berkembang terancam oleh perubahan iklim."),
 ("Data dikumpulkan melalui wawancara mendalam dengan sepuluh narasumber.", "Peneliti mewawancarai sepuluh narasumber secara mendalam untuk memperoleh data."),
 ("Sistem antrean memungkinkan tugas berat diproses di latar belakang.", "Dengan antrean, pekerjaan yang berat dapat dijalankan di belakang layar."),
 ("Kualitas tidur yang buruk berhubungan dengan menurunnya konsentrasi.", "Tidur yang tidak berkualitas dikaitkan dengan konsentrasi yang menurun."),
 ("Pembayaran dilakukan melalui gerbang yang mendukung berbagai metode.", "Transaksi dibayar lewat gerbang pembayaran dengan beragam metode."),
 ("Tim peneliti menggunakan metode kuantitatif dengan survei daring.", "Metode kuantitatif lewat survei online dipakai oleh tim peneliti."),
 ("Semakin tinggi suhu, semakin cepat reaksi kimia berlangsung.", "Reaksi kimia berjalan lebih cepat ketika suhu meningkat."),
 ("Naskah yang diunggah akan dihapus permanen setelah pengguna menghapusnya.", "Setelah dihapus oleh pengguna, naskah yang diunggah hilang secara permanen."),
]
ID_HARD_NEG = [  # topik sama, makna beda
 ("Penelitian ini bertujuan untuk mengetahui pengaruh media sosial terhadap prestasi belajar siswa.", "Penelitian ini bertujuan untuk mengetahui pengaruh olahraga terhadap kesehatan lansia."),
 ("Kenaikan harga bahan bakar menyebabkan inflasi meningkat tajam.", "Penurunan harga bahan bakar menyebabkan inflasi menurun tajam."),
 ("Sebagian besar responden menyatakan puas dengan layanan tersebut.", "Sebagian besar responden menyatakan kecewa dengan layanan tersebut."),
 ("Pemerintah berencana membangun jalur kereta baru di wilayah timur.", "Pemerintah membatalkan pembangunan jalur kereta di wilayah timur."),
 ("Hasil eksperimen menunjukkan bahwa akurasi sistem mencapai sembilan puluh persen.", "Hasil eksperimen menunjukkan bahwa akurasi sistem hanya mencapai empat puluh persen."),
 ("Pengguna wajib memverifikasi alamat surel sebelum dapat masuk ke akun.", "Pengguna dilarang memverifikasi alamat surel sebelum masuk ke akun."),
 ("Perubahan iklim mengancam produksi pangan di banyak negara berkembang.", "Perubahan iklim meningkatkan produksi pangan di banyak negara berkembang."),
 ("Semakin tinggi suhu, semakin cepat reaksi kimia berlangsung.", "Semakin tinggi suhu, semakin lambat reaksi kimia berlangsung."),
]
ID_EASY_NEG = [
 ("Algoritma Winnowing memilih nilai hash minimum pada setiap jendela.", "Kucing itu tidur di atas sofa sepanjang sore."),
 ("Data dikumpulkan melalui wawancara mendalam dengan sepuluh narasumber.", "Harga tiket pesawat ke Bali naik menjelang liburan."),
 ("Kualitas tidur yang buruk berhubungan dengan menurunnya konsentrasi.", "Tim sepak bola itu memenangkan pertandingan final semalam."),
 ("Sistem antrean memungkinkan tugas berat diproses di latar belakang.", "Resep rendang membutuhkan santan dan rempah pilihan."),
 ("Pembayaran dilakukan melalui gerbang yang mendukung berbagai metode.", "Gunung berapi itu meletus dan abunya menutupi desa."),
 ("Tim peneliti menggunakan metode kuantitatif dengan survei daring.", "Hujan deras mengguyur Jakarta sejak pagi hari."),
 ("Model bahasa besar sering menghasilkan teks dengan pola kalimat yang seragam.", "Anak-anak bermain layang-layang di lapangan desa."),
 ("Naskah yang diunggah akan dihapus permanen setelah pengguna menghapusnya.", "Festival musik tahun ini menghadirkan banyak penampil lokal."),
]
EN_POS = [
 ("The study aims to examine the effect of social media on student performance.", "This research seeks to investigate how social media influences students' grades."),
 ("Rising fuel prices caused inflation to climb sharply.", "Inflation jumped because the price of fuel went up."),
 ("Most respondents said they were satisfied with the service.", "The majority of survey participants reported being happy with the service."),
 ("Large language models often produce text with uniform sentence patterns.", "Text generated by big language models tends to have monotonous sentence structure."),
 ("Users must verify their email address before they can log in.", "Before logging in, users are required to confirm their email."),
 ("Climate change threatens food production in many developing countries.", "Food production in numerous developing nations is endangered by climate change."),
 ("Data were collected through in-depth interviews with ten participants.", "The researchers interviewed ten participants in depth to gather data."),
 ("A task queue lets heavy jobs run in the background.", "With a queue, heavy work can be processed behind the scenes."),
 ("The higher the temperature, the faster the chemical reaction proceeds.", "Chemical reactions speed up as the temperature rises."),
 ("Uploaded manuscripts are permanently deleted once the user removes them.", "After a user deletes an uploaded manuscript, it is gone for good."),
]
EN_HARD_NEG = [
 ("Rising fuel prices caused inflation to climb sharply.", "Falling fuel prices caused inflation to drop sharply."),
 ("Most respondents said they were satisfied with the service.", "Most respondents said they were disappointed with the service."),
 ("Users must verify their email address before they can log in.", "Users are not allowed to verify their email address before logging in."),
 ("Climate change threatens food production in many developing countries.", "Climate change boosts food production in many developing countries."),
 ("The higher the temperature, the faster the chemical reaction proceeds.", "The higher the temperature, the slower the chemical reaction proceeds."),
]
EN_EASY_NEG = [
 ("A task queue lets heavy jobs run in the background.", "The cat slept on the sofa all afternoon."),
 ("Data were collected through in-depth interviews with ten participants.", "Flight tickets to Bali get pricier before the holidays."),
 ("Large language models often produce text with uniform sentence patterns.", "Children were flying kites in the village field."),
 ("The study aims to examine the effect of social media on student performance.", "The volcano erupted and ash covered the village."),
 ("Uploaded manuscripts are permanently deleted once the user removes them.", "Heavy rain has poured over the city since morning."),
]
def build():
    out = []
    for a, b in ID_POS: out.append((a, b, 1, "id", "pos"))
    for a, b in ID_HARD_NEG: out.append((a, b, 0, "id", "hard"))
    for a, b in ID_EASY_NEG: out.append((a, b, 0, "id", "easy"))
    for a, b in EN_POS: out.append((a, b, 1, "en", "pos"))
    for a, b in EN_HARD_NEG: out.append((a, b, 0, "en", "hard"))
    for a, b in EN_EASY_NEG: out.append((a, b, 0, "en", "easy"))
    return out
