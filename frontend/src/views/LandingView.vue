<script setup lang="ts">
import {
  HeroSection,
  DashboardShowcaseWindow,
  PipelineTiersGrid,
  CallToActionSection,
} from "../components/landing";
</script>

<template>
  <div class="space-y-12 sm:space-y-20 py-4 sm:py-8 font-sans">
    <!-- 1. Hero Section Sesuai build_landing.py:seg_nav_hero() -->
    <HeroSection />

    <!-- 2. Laporan Diagnostik Interaktif Sesuai build_landing.py:seg_report() -->
    <DashboardShowcaseWindow />

    <!-- 3. Tiga Lapis Pemeriksaan Sesuai build_landing.py:seg_how() -->
    <PipelineTiersGrid />

    <!-- 4. Call To Action Sesuai build_landing.py:seg_cta_short() -->
    <CallToActionSection />
  </div>
</template>
