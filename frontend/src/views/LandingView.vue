<script setup lang="ts">
import {
  HeroSection,
  DashboardShowcaseWindow,
  InteractiveDemoSnippet,
  PipelineTiersGrid,
  InvertedDarkSection,
  FeatureHighlights,
} from "../components/landing";
</script>

<template>
  <div class="space-y-20 sm:space-y-28 py-8 sm:py-16">
    <!-- Hero Section (Steep Editorial Headline with Floating Artifacts) -->
    <HeroSection />

    <!-- Live Application Window Showcase (Steep Image 1 & 3 macOS Window Mockup) -->
    <DashboardShowcaseWindow />

    <!-- Live Interactive Diagnostic Demo (Editorial Manuscript Inspection) -->
    <InteractiveDemoSnippet />

    <!-- 4-Tier Detection Pipeline Grid (Editorial Bento Grid) -->
    <PipelineTiersGrid />

    <!-- Inverted Ink-Black High-Contrast Section (Steep Image 2 Reference) -->
    <InvertedDarkSection />

    <!-- Technical Architecture & Compliance Highlights -->
    <FeatureHighlights />
  </div>
</template>
