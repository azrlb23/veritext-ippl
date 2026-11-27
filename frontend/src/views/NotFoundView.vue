<template>
  <div class="mx-auto flex min-h-[70vh] max-w-[680px] items-center justify-center px-4 py-16 font-sans sm:px-6">
    <section class="w-full rounded-[32px] border border-[#E8ECEB] bg-white p-8 text-center shadow-float sm:p-12">
      <p class="text-[56px] font-semibold leading-none tracking-[-0.05em] tabular-nums text-[#0F766E] sm:text-[72px]">
        404
      </p>
      <h1 class="mt-4 text-[26px] font-semibold leading-[1.2] tracking-[-0.03em] text-[#14111C] sm:text-[30px]">
        Halaman tidak ditemukan
      </h1>
      <p class="mx-auto mt-3 max-w-[440px] text-[15px] leading-[1.65] text-[#4B4757]">
        Tautan yang Anda tuju mungkin sudah dipindahkan, dihapus, atau alamat URL keliru diketik.
      </p>

      <div class="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
        <router-link
          to="/"
          class="vt-btn-dark inline-flex min-h-[44px] w-full items-center justify-center rounded-full px-7 text-[14.5px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2 sm:w-auto"
        >
          Kembali ke Beranda
        </router-link>
        <router-link
          to="/dashboard"
          class="vt-btn-light inline-flex min-h-[44px] w-full items-center justify-center rounded-full px-7 text-[14.5px] font-semibold text-[#14111C] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2 sm:w-auto"
        >
          Buka Ringkasan
        </router-link>
      </div>
    </section>
  </div>
</template>
