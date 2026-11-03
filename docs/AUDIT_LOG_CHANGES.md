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
  - Tombol (X) pada alert sekarang berfungsi menutup notifikasi error secara reaktif.
