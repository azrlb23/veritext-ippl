<g clip-path="url(#card)">
    <!-- Photo illustration -->
    <g clip-path="url(#photo)">
      <rect x="600" y="78" width="520" height="740" fill="url(#sky)"/>
      <!-- clouds -->
      <g fill="#FFFFFF" filter="url(#cloudBlur)">
        <ellipse cx="900" cy="150" rx="110" ry="30" opacity="0.75"/>
        <ellipse cx="1020" cy="210" rx="120" ry="36" opacity="0.65"/>
        <ellipse cx="860" cy="270" rx="90" ry="26" opacity="0.6"/>
        <ellipse cx="1000" cy="330" rx="130" ry="30" opacity="0.7"/>
        <ellipse cx="900" cy="385" rx="120" ry="24" opacity="0.8"/>
      </g>

      <!-- teal rock mountains -->
      <path d="M840 442L862 418L880 430L930 456L985 428L1025 402L1048 414L1076 456L1100 432L1120 420L1120 600L840 600Z" fill="url(#rock)"/>
      <path d="M1025 402L1048 414L1076 456L1050 470L1030 440L1012 470L985 428Z" fill="url(#rockLight)" opacity="0.8"/>
      <path d="M862 418L880 430L930 456L900 480L875 455L850 470Z" fill="url(#rockLight)" opacity="0.7"/>
      <path d="M1076 456L1100 432L1120 420L1120 470L1098 490Z" fill="#6AA7AB" opacity="0.8"/>
      <path d="M1025 402L1033 414L1022 420ZM1100 432L1112 424L1106 442Z" fill="#E8F1F1" opacity="0.9"/>

      <!-- snow slope -->
      <path d="M690 604L745 540L792 497L830 472L872 502L930 546L1000 566L1040 590L1040 604Z" fill="url(#slope)"/>
      <g filter="url(#softBlur)">
        <path d="M760 545L792 505L806 525L780 560Z" fill="#9FACB0" opacity="0.4"/>
        <path d="M900 540L950 552L1000 556L1030 566L960 566Z" fill="#F2F6F6" opacity="0.8"/>
        <path d="M1050 528L1095 548L1120 556L1120 564L1070 558Z" fill="#E7EFEF" opacity="0.7"/>
      </g>

      <!-- forest -->
      <path d="M700 600L740 590L790 596L840 590L900 596L960 600L985 588L1025 568L1062 556L1095 544L1120 538L1120 616L700 616Z" fill="#1C4A42"/>
      <path d="M960 600L990 584L1030 566L1070 554L1120 540L1120 572L1040 590L980 606Z" fill="#14392F" opacity="0.7"/>

      <!-- lake -->
      <rect x="600" y="612" width="520" height="210" fill="url(#lake)"/>
      <!-- reflections -->
      <g filter="url(#lakeBlur)">
        <path d="M680 625L860 625L900 650L880 700L820 740L740 760L680 750Z" fill="url(#reflect)"/>
        <path d="M870 625L1120 625L1120 700L1040 690L960 700L900 670Z" fill="#2A7076" opacity="0.7"/>
        <path d="M950 640L1120 640L1120 662L1000 668Z" fill="#14392F" opacity="0.55"/>
        <path d="M720 700L800 690L860 720L800 790L700 800Z" fill="#B7D3D5" opacity="0.35"/>
      </g>
      <g stroke="#CFE4E5" stroke-width="1.5" stroke-linecap="round" opacity="0.35">
        <path d="M700 664H790M830 678H940M900 700H1010M760 722H870M980 740H1090M820 760H930"/>
      </g>
    </g>
  </g>

  <!-- Dashed contour -->
  <path d="M757 80C690 100 610 130 618 185C625 230 690 240 725 275C760 310 760 345 725 372C690 392 640 380 632 440C625 520 640 600 615 700C600 750 590 790 572 818"
        fill="none" stroke="#D3D8E2" stroke-width="1.2" stroke-dasharray="5 5" stroke-linecap="round" clip-path="url(#card)"/>
