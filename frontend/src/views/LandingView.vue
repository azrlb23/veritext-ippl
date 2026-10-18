<script setup lang="ts">
import TierLegend from "../components/TierLegend.vue";
import {
  HeroSection,
  InteractiveDemoSnippet,
  PipelineTiersGrid,
  FeatureHighlights,
} from "../components/landing";
</script>

<template>
  <div class="space-y-20 sm:space-y-28 py-8 sm:py-16">
    <!-- Hero Section -->
    <HeroSection />

    <!-- Live Interactive Diagnostic Demo (Anti-Slop Utility) -->
    <InteractiveDemoSnippet />

    <!-- Visual Tier Overview -->
    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" aria-label="Legenda Ringkasan Tier">
      <TierLegend />
    </section>

    <!-- 4-Tier Detection Pipeline Grid -->
    <PipelineTiersGrid />

    <!-- Technical Architecture & Compliance Highlights -->
    <FeatureHighlights />
  </div>
</template>
