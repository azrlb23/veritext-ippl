# Catatan Perubahan & Audit Log (Docs Audit)

Dokumen ini mencatat setiap permintaan perubahan fitur, perbaikan bug, mitigasi keamanan, atau pembaruan arsitektural yang diajukan oleh pengguna beserta status verifikasinya.

---

## Log Riwayat Audit & Perubahan

### [2026-11-03] Fix: Tombol Dismiss (X) Alert Error Login & Register Tidak Berfungsi
- **Pengaju**: User
- **Modul Terkait**:
  - `frontend/src/components/auth/LoginForm.vue`
  - `frontend/src/views/LoginView.vue`
  - `frontend/src/components/auth/RegisterForm.vue`
  - `frontend/src/views/RegisterView.vue`
- **Deskripsi Masalah**:
  Saat muncul notifikasi error login (misal *"Invalid email or password"*), tombol icon silang (X) pada komponen `Alert` tidak dapat menutup alert tersebut ketika diklik.
- **Akar Masalah (*Root Cause*)**:
  1. Komponen `LoginForm` dan `RegisterForm` menerima pesan error dari view induk via prop `:errorMessage`.
  2. Saat event `@dismiss` pada `Alert` ditembakkan, form hanya mereset state lokal `validationError = ''`, tetapi tidak mengemilikan event ke view induk (`LoginView` / `RegisterView`) untuk mereset `errorMessage.value = ''`.
  3. Akibatnya, kondisi `v-if="errorMessage || validationError"` tetap bernilai `true` dan alert error tetap terpampang di layar.
- **Solusi & Perbaikan**:
  1. Menambahkan emit `clear-error` pada `LoginForm.vue` dan `RegisterForm.vue`.
  2. Membuat method `handleDismiss()` yang mereset `validationError.value = ''` dan memanggil `emit('clear-error')`.
  3. Di `LoginView.vue` dan `RegisterView.vue`, menangani event `@clear-error="errorMessage = ''"`.
- **Hasil Verifikasi**:
  - `npm test`: 25/25 navigasi & RBAC tests **PASSED (100%)**.
  - `npm run build`: Kompilasi `vue-tsc && vite build` **SUCCEEDED (0 errors)**.

---

### [2026-11-03] Docs: Pemetaan Seluruh Halaman & State Antarmuka VeriText AI (FMS Benchmark)
- **Pengaju**: User
- **Modul Terkait**:
  - `docs/UI_UX_PAGE_STATES_ARCHITECTURE.md`
- **Deskripsi Kebutuhan**:
  Menyusun arsitektur komprehensif seluruh 9 halaman aplikasi beserta seluruh kuadran state antarmukanya (Idle, Loading, Empty, Active/Processing, Error, Modal, dan breakpoint Responsif Mobile/Tablet/Desktop) mengadopsi taksonomi desain sistematis FMS (*Fuel Management System*).
- **Hasil & Luaran**:
  - Dokumen `docs/UI_UX_PAGE_STATES_ARCHITECTURE.md` berhasil dibuat dan dipetakan untuk 9 halaman lengkap.
  - Menetapkan batas tegas untuk pembasmian klise desain tiruan (macOS window mockup, floating cards tebal) ke arah editorial workstation berdensitas tinggi (*anti-ai-slop* dan *ui-ux-pro-max*).
  - Tombol (X) pada alert sekarang berfungsi menutup notifikasi error secara reaktif.

---

### [2026-11-03] Feat: Show/Hide Password Toggle pada Formulir Login & Registrasi
- **Pengaju**: User
- **Modul Terkait**:
  - `frontend/src/components/auth/LoginForm.vue`
  - `frontend/src/components/auth/RegisterForm.vue`
- **Deskripsi Kebutuhan**:
  Menyediakan fitur toggle untuk melihat atau menyembunyikan kata sandi (show/hide password) menggunakan ikon mata (eye icon) pada formulir login dan registrasi akun.
- **Prinsip Keamanan & Desain (Zero Vulnerability / Anti-Jebolan)**:
  1. **Tipe Elemen**: Tombol toggle diatur dengan eksplisit `type="button"`. Hal ini mencegah insiden pengiriman form (*inadvertent form submission*) saat tombol mata diklik atau ditekan dengan tombol spasi/enter.
  2. **Isolasi State**: State visibilitas (`showPassword`, `showConfirmPassword`) diisolasi secara lokal menggunakan `ref(false)` di dalam *setup scope* masing-masing komponen. Password tidak pernah bocor ke storage, URL query, console log, atau state manajemen global (Pinia).
  3. **Standar Aksesibilitas (A11y)**: Ditambahkan atribut `aria-label` dinamis (*"Tampilkan kata sandi"* / *"Sembunyikan kata sandi"*) untuk kompatibilitas pembaca layar (*screen reader*).
  4. **Standar Autocomplete**: Tetap mempertahankan standar `autocomplete="current-password"` pada login dan `autocomplete="new-password"` pada registrasi untuk mendukung password manager yang aman.
  5. **Padding & Tata Letak**: Diberikan class `pr-10` pada input agar karakter password yang panjang tidak tertimpa ikon mata.
- **Solusi & Perbaikan**:
  1. Di `LoginForm.vue`: Ditambahkan `showPassword = ref(false)`, container pembungkus `.relative`, dan tombol SVG eye toggle.
  2. Di `RegisterForm.vue`: Ditambahkan kontrol terpisah `showPassword` dan `showConfirmPassword` agar pengguna dapat memeriksa kedua field kata sandi secara independen.
- **Hasil Verifikasi**:
  - `npm test`: 25/25 navigasi & RBAC tests **PASSED (100%)**.
  - `npm run build`: Kompilasi `vue-tsc && vite build` **SUCCEEDED (0 errors)**.

---

### [2026-11-03] Docs: Pemetaan Seluruh Halaman & State Antarmuka VeriText AI (FMS Benchmark)
- **Pengaju**: User
- **Modul Terkait**:
  - `docs/UI_UX_PAGE_STATES_ARCHITECTURE.md`
- **Deskripsi Kebutuhan**:
  Menyusun arsitektur komprehensif seluruh 9 halaman aplikasi beserta seluruh kuadran state antarmukanya (Idle, Loading, Empty, Active/Processing, Error, Modal, dan breakpoint Responsif Mobile/Tablet/Desktop) mengadopsi taksonomi desain sistematis FMS (*Fuel Management System*).
- **Hasil & Luaran**:
  - Dokumen `docs/UI_UX_PAGE_STATES_ARCHITECTURE.md` berhasil dibuat dan dipetakan untuk 9 halaman lengkap.
  - Menetapkan batas tegas untuk pembasmian klise desain tiruan (macOS window mockup, floating cards tebal) ke arah editorial workstation berdensitas tinggi (*anti-ai-slop* dan *ui-ux-pro-max*).
