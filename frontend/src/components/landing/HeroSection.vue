<template>
  <section class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 sm:pt-14 pb-16 sm:pb-24 overflow-hidden">
    <!-- Soft Warm Peach Radial Ambient Aura (Steep Signature Glow) -->
    <div
      class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 -z-10 w-full max-w-5xl h-[600px] bg-[radial-gradient(ellipse_60%_50%_at_70%_35%,rgba(251,225,209,0.55),rgba(255,255,255,0))] blur-3xl pointer-events-none"
      aria-hidden="true"
    ></div>
    <div
      class="absolute top-10 left-10 -z-10 w-72 h-72 bg-[radial-gradient(circle,rgba(251,225,209,0.35)_0%,rgba(255,255,255,0)_70%)] blur-2xl pointer-events-none"
      aria-hidden="true"
    ></div>

    <!-- Main Hero Canvas (Centered Headline with Floating Surrounding Artifacts on Desktop) -->
    <div class="relative min-h-[580px] lg:min-h-[660px] flex flex-col justify-center items-center text-center">

      <!-- ============================================================ -->
      <!-- FLOATING ARTIFACT 1: Top-Left (Region & Lexical Hash Match)  -->
      <!-- ============================================================ -->
      <div
        class="hidden lg:flex absolute top-2 left-0 xl:-left-2 z-10 bg-white rounded-[22px] p-4 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] hover:border-[#17191c] transition-all duration-200 ease-out text-left gap-4 w-[290px] select-none"
      >
        <!-- Left Sub-Block: 3 503 & Mini Histogram -->
        <div class="space-y-1.5 flex flex-col justify-between pr-3 border-r border-[#ededed]/80">
          <div>
            <div class="text-xl font-bold text-[#17191c] tabular-nums tracking-tight">3 503</div>
            <div class="text-[10px] text-[#777b86] font-medium leading-tight">2% vs last week</div>
          </div>
          <!-- Mini Histogram Bars -->
          <div class="flex items-end space-x-1 h-9 pt-1">
            <span class="w-1.5 bg-[#17191c]/25 rounded-t-sm h-[40%]"></span>
            <span class="w-1.5 bg-[#17191c]/40 rounded-t-sm h-[65%]"></span>
            <span class="w-1.5 bg-[#17191c]/60 rounded-t-sm h-[85%]"></span>
            <span class="w-1.5 bg-[#17191c]/45 rounded-t-sm h-[55%]"></span>
            <span class="w-1.5 bg-[#17191c] rounded-t-sm h-[100%]"></span>
          </div>
          <div class="flex items-center space-x-1 text-[9px] text-[#979799] uppercase font-mono">
            <span>F</span><span>S</span><span>S</span><span class="text-[#17191c] font-bold">M</span>
          </div>
        </div>

        <!-- Right Sub-Block: Region / Corpus Table -->
        <div class="flex-1 space-y-1 text-xs">
          <div class="text-[11px] font-semibold text-[#17191c] mb-1 tracking-tight">Region</div>
          <div class="space-y-1 text-[11px] text-[#777b86]">
            <div class="flex items-center justify-between">
              <span>Europe</span>
              <span class="text-[#17191c] font-medium tabular-nums">1 373</span>
            </div>
            <div class="flex items-center justify-between">
              <span>North America</span>
              <span class="text-[#17191c] font-medium tabular-nums">930</span>
            </div>
            <div class="flex items-center justify-between">
              <span>Africa</span>
              <span class="text-[#17191c] font-medium tabular-nums">745</span>
            </div>
            <div class="flex items-center justify-between">
              <span>Asia</span>
              <span class="text-[#17191c] font-medium tabular-nums">432</span>
            </div>
            <div class="flex items-center justify-between">
              <span>Other</span>
              <span class="text-[#17191c] font-medium tabular-nums">23</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ============================================================ -->
      <!-- FLOATING ARTIFACT 2: Middle-Right (Registrations Gauge Card) -->
      <!-- ============================================================ -->
      <div
        class="hidden lg:flex absolute top-28 right-0 xl:-right-2 z-10 bg-white rounded-[22px] p-5 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] hover:border-[#17191c] transition-all duration-200 ease-out text-left items-center justify-between gap-5 w-[270px] select-none"
      >
        <div class="space-y-1">
          <div class="text-[11px] font-semibold text-[#5d2a1a] tracking-tight">Registrations</div>
          <div class="text-2xl font-bold text-[#17191c] tabular-nums tracking-tight">2.4k</div>
          <div class="text-[10px] text-[#777b86] font-medium flex items-center">
            <span>&uarr; 5.5% vs last week</span>
          </div>
        </div>

        <!-- Circular Gauge (75% of target) in Sienna/Peach accent -->
        <div class="relative w-16 h-16 flex items-center justify-center flex-shrink-0">
          <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
            <path
              class="text-[#fbe1d1]"
              stroke-width="3.5"
              stroke="currentColor"
              fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <path
              stroke="#5d2a1a"
              stroke-dasharray="75, 100"
              stroke-linecap="round"
              stroke-width="3.5"
              fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
          </svg>
          <div class="absolute flex flex-col items-center text-center">
            <span class="text-xs font-bold text-[#17191c] tabular-nums leading-none">75%</span>
            <span class="text-[8px] text-[#777b86] font-medium leading-tight">of target</span>
          </div>
        </div>
      </div>

      <!-- ============================================================ -->
      <!-- FLOATING ARTIFACT 3: Bottom-Left (Activation Sparkline & JB) -->
      <!-- ============================================================ -->
      <div
        class="hidden lg:flex items-center absolute bottom-12 left-4 xl:left-8 z-10 select-none"
      >
        <!-- Floating JB Avatar with Hand-Drawn-Style Arrow -->
        <div class="flex items-center mr-2">
          <div class="w-8 h-8 rounded-full bg-white border border-[#ededed] shadow-sm text-[#17191c] text-xs font-semibold flex items-center justify-center">
            JB
          </div>
          <svg class="w-6 h-6 text-[#17191c]/70 -mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
            <path stroke-linecap="round" stroke-linejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </div>

        <!-- Activation Card -->
        <div class="bg-white rounded-[22px] p-4 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] hover:border-[#17191c] transition-all duration-200 ease-out text-left w-[220px]">
          <div class="text-[11px] font-medium text-[#777b86]">Activation</div>
          <div class="flex items-baseline space-x-1.5 mt-0.5">
            <span class="text-base font-bold text-[#17191c] tabular-nums">46.2%</span>
            <span class="text-[10px] text-[#979799]">103% of target</span>
          </div>

          <!-- Sparkline Curve with Month Labels -->
          <div class="mt-2 pt-1 border-t border-[#ededed]/60">
            <svg class="w-full h-8 overflow-visible" viewBox="0 0 100 30" fill="none">
              <!-- Dashed target line -->
              <line x1="0" y1="18" x2="100" y2="18" stroke="#ededed" stroke-width="1" stroke-dasharray="2,2" />
              <!-- Trendline curve -->
              <path
                d="M 5 24 Q 25 22, 45 15 T 75 14 T 95 6"
                stroke="#17191c"
                stroke-width="1.75"
                stroke-linecap="round"
                fill="none"
              />
              <!-- Active End Node -->
              <circle cx="95" cy="6" r="2.5" fill="#17191c" />
            </svg>
            <div class="flex justify-between text-[9px] text-[#979799] mt-1 font-mono">
              <span>Aug</span>
              <span>Sep</span>
              <span>Oct</span>
              <span class="px-1 bg-[#f2f2f3] rounded text-[#17191c] font-medium">Nov</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ============================================================ -->
      <!-- FLOATING ARTIFACT 4: Bottom-Right (Ask anything... Bar & AF) -->
      <!-- ============================================================ -->
      <div
        class="hidden lg:flex items-center absolute bottom-12 right-6 xl:right-12 z-10 select-none"
      >
        <div class="bg-white rounded-full pl-4 pr-1.5 py-1.5 border border-[#ededed] shadow-[0_0_0_1px_rgba(4,23,43,0.05),0_20px_35px_-10px_rgba(0,0,0,0.08)] flex items-center space-x-3 w-[290px] text-left">
          <div class="flex-1 text-xs text-[#a3a6af] font-normal truncate">
            Ask anything...
          </div>
          <!-- @ and History Icon -->
          <div class="flex items-center space-x-1.5 text-[#777b86]">
            <span class="text-xs font-semibold">@</span>
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <!-- AF Avatar Circle -->
          <div class="w-6 h-6 rounded-full bg-[#fbe1d1] text-[#5d2a1a] text-[10px] font-semibold flex items-center justify-center flex-shrink-0">
            AF
          </div>
          <!-- Black Circle Submit Button -->
          <div class="w-6 h-6 rounded-full bg-[#17191c] text-white flex items-center justify-center flex-shrink-0 cursor-pointer hover:bg-[#2e3138] transition-colors">
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
          </div>
        </div>
      </div>

      <!-- ============================================================ -->
      <!-- HERO CENTER: Iconic Serif Display Headline & Actions         -->
      <!-- ============================================================ -->
      <div class="max-w-3xl mx-auto px-4 space-y-6 z-20 py-8 lg:py-16">
        <!-- Display Headline (Signifier Serif 64px, weight 400 with italic signature) -->
        <h1 class="font-serif text-4xl sm:text-6xl lg:text-[70px] font-normal text-[#17191c] tracking-[-0.03em] leading-[1.12]">
          AI analytics for faster<br />
          insights and <span class="italic font-normal">zero chaos</span>
        </h1>

        <!-- Editorial Subtitle -->
        <p class="text-base sm:text-[18px] text-[#777b86] max-w-xl mx-auto leading-[1.6] tracking-tight font-normal">
          Steep is an AI analytics platform built on governed metrics that powers analysis, reporting and company-wide engagement.
        </p>

        <!-- Centered Pill Buttons -->
        <div class="flex flex-wrap items-center justify-center gap-3 pt-3">
          <router-link
            to="/dashboard"
            class="inline-flex items-center justify-center px-6 py-2.5 rounded-full bg-[#17191c] hover:bg-[#2e3138] text-white font-medium text-sm tracking-tight active:scale-[0.98] transition-all duration-150 ease-out shadow-sm"
          >
            Get started
          </router-link>
          <router-link
            to="/corpus"
            class="inline-flex items-center justify-center px-5 py-2.5 rounded-full bg-transparent hover:bg-[#f2f2f3] text-[#17191c] font-medium text-sm tracking-tight active:scale-[0.98] transition-all duration-150 ease-out"
          >
            Book a demo
          </router-link>
        </div>
      </div>
    </div>

    <!-- Mobile / Responsive Fallback: 4 Artifacts displayed cleanly below on smaller screens (< lg) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 lg:hidden pt-8 border-t border-[#ededed]/60 max-w-xl mx-auto">
      <!-- Card 1 Mobile -->
      <div class="bg-white rounded-[20px] p-4 border border-[#ededed] shadow-sm flex items-center justify-between text-left">
        <div>
          <div class="text-base font-bold text-[#17191c] tabular-nums">3 503</div>
          <div class="text-[11px] text-[#777b86]">Region Analytics · 2% vs last week</div>
        </div>
        <span class="px-2.5 py-0.5 rounded-full bg-[#f2f2f3] text-[10px] text-[#17191c] font-medium">Metrics</span>
      </div>

      <!-- Card 2 Mobile -->
      <div class="bg-white rounded-[20px] p-4 border border-[#ededed] shadow-sm flex items-center justify-between text-left">
        <div>
          <div class="text-base font-bold text-[#17191c] tabular-nums">2.4k (75%)</div>
          <div class="text-[11px] text-[#777b86]">Registrations of target</div>
        </div>
        <span class="px-2.5 py-0.5 rounded-full bg-[#fbe1d1] text-[10px] text-[#5d2a1a] font-medium">Target</span>
      </div>

      <!-- Card 3 Mobile -->
      <div class="bg-white rounded-[20px] p-4 border border-[#ededed] shadow-sm flex items-center justify-between text-left">
        <div>
          <div class="text-base font-bold text-[#17191c] tabular-nums">46.2%</div>
          <div class="text-[11px] text-[#777b86]">Activation curve · 103% of target</div>
        </div>
        <span class="px-2.5 py-0.5 rounded-full bg-[#ecfdf5] text-[10px] text-[#065f46] font-medium">Live</span>
      </div>

      <!-- Card 4 Mobile -->
      <div class="bg-white rounded-full px-4 py-2 border border-[#ededed] shadow-sm flex items-center justify-between text-left sm:col-span-2">
        <span class="text-xs text-[#a3a6af]">Ask anything...</span>
        <div class="w-6 h-6 rounded-full bg-[#17191c] text-white flex items-center justify-center">
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
        </div>
      </div>
    </div>
  </section>
</template>
