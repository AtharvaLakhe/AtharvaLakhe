<h1 align="center">Atharva Lakhe</h1>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=21&pause=1200&color=FFB454&center=true&vCenter=true&width=760&lines=Independent+builder;Multi-agent+systems%2C+remote-sensing+ML%2C+dev+tooling;Systems+that+make+their+own+reasoning+inspectable;A+number+you+cannot+trace+is+not+a+result" alt="Independent builder — multi-agent systems, remote-sensing ML, developer tooling" />
</p>

<p align="center">
  <a href="mailto:atharvalakhe09@gmail.com"><img src="https://img.shields.io/badge/Email-atharvalakhe09%40gmail.com-FFB454?style=for-the-badge&logo=gmail&logoColor=0D1117" alt="Email" /></a>
  <img src="https://komarev.com/ghpvc/?username=AtharvaLakhe&color=FFB454&style=for-the-badge&label=Profile+Views" alt="Profile views" />
  <a href="#open-source"><img src="https://img.shields.io/badge/Open_to-collaboration-30363D?style=for-the-badge&logo=github&logoColor=FFB454" alt="Open to collaboration" /></a>
</p>

---

## About

I build systems that make their own reasoning inspectable.

- 🛰 &nbsp;**Remote sensing** — recovering terrain from lunar craters that have been dark for two billion years
- 🤖 &nbsp;**Multi-agent systems** — agents that argue, where the disagreement itself is the auditable artifact
- 🔗 &nbsp;**Verifiable state** — hash chains written from scratch, with tampering demonstrated live
- 🧪 &nbsp;**Developer tooling** — a code reviewer graded by the repository's own future

A theme runs through all of it: **the output has to carry its own evidence.** Every project below ships the numbers that justify it — and reports the ones that don't.

---

## Featured — PSR-Net

> Near the lunar poles the Sun never rises more than a degree or two above the horizon, so any depression deep enough to hide behind its own rim has been dark for two billion years. An OHRC frame of one is twelve digital numbers of signal sitting on the noise floor.

<p align="center">
  <a href="https://psr-net.vercel.app/psr/">
    <img src="https://raw.githubusercontent.com/AtharvaLakhe/PSR-Net/main/docs/hero.png" alt="The flight from lunar orbit down to a shadowed crater floor" width="100%" />
  </a>
</p>

A single page that explains the problem, runs the recovery **in your browser**, and shows its own numbers — a scroll-driven WebGL flight, seven deterministic restoration stages on real 12-bit values, and a 714,401-parameter network exported to ONNX.

Measured on 24 held-out scenes, fixed degradation seeds, both methods scored after the same affine fit:

| Method | PSNR (dB) | SSIM |
| :--- | :--- | :--- |
| Raw frame | 17.27 ± 1.45 | 0.257 |
| Deterministic chain | 17.47 ± 1.39 | 0.272 |
| **PSR-Net** | **20.28 ± 2.65** | **0.444** |

<p align="center">
  <a href="https://psr-net.vercel.app/psr/"><img src="https://img.shields.io/badge/▶_Live_demo-psr--net.vercel.app-FFB454?style=for-the-badge" alt="Live demo" /></a>
  <a href="https://github.com/AtharvaLakhe/PSR-Net"><img src="https://img.shields.io/badge/Source-PSR--Net-30363D?style=for-the-badge&logo=github" alt="Source" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-FFB454?style=flat-square&labelColor=0D1117" alt="MIT licensed" />
  <img src="https://img.shields.io/badge/parameters-714%2C401-30363D?style=flat-square&labelColor=0D1117" alt="714,401 parameters" />
  <img src="https://img.shields.io/badge/runtime-onnxruntime--web-30363D?style=flat-square&labelColor=0D1117" alt="onnxruntime-web" />
  <img src="https://img.shields.io/github/languages/top/AtharvaLakhe/PSR-Net?style=flat-square&labelColor=0D1117&color=30363D" alt="Top language" />
  <img src="https://img.shields.io/github/languages/code-size/AtharvaLakhe/PSR-Net?style=flat-square&labelColor=0D1117&color=30363D" alt="Code size" />
  <img src="https://img.shields.io/github/last-commit/AtharvaLakhe/PSR-Net?style=flat-square&labelColor=0D1117&color=30363D" alt="Last commit" />
</p>

---

## Projects

| Project | What it does | Stack | Live |
| :--- | :--- | :--- | :--- |
| **[PSR-Net](https://github.com/AtharvaLakhe/PSR-Net)** | Terrain recovery from permanently shadowed lunar craters imaged by Chandrayaan-2 OHRC | `PyTorch` `ONNX` `Three.js` | [▶](https://psr-net.vercel.app/psr/) |
| **[SPARC](https://github.com/AtharvaLakhe/SPARC)** | District-level environmental change from open Earth-observation data, traceable to the scene it came from | `FastAPI` `React` `MapLibre` | [▶](https://sparc-git-main-sanskars-projects-31a9e8dd.vercel.app/) |
| **[CarbonLedger](https://github.com/AtharvaLakhe/CarbonLedger)** | Carbon-credit marketplace and MRV platform for India's CCTS — SHA-256 hash chain, no crypto library | `React` `Node` `SSE` | — |
| **[FancePro](https://github.com/AtharvaLakhe/FancePro)** | Four agents argue over one household budget — and you can audit how the disagreement was settled | `Vanilla JS` `0 deps` | [▶](https://atharvalakhe.github.io/FancePro/) |
| **[LancePro](https://github.com/AtharvaLakhe/LancePro)** | Local-first scope-creep protection for freelancers — contract parsing and evidence capture | `React` `TS` `Web Crypto` | — |

<p align="center">
  <a href="https://github.com/AtharvaLakhe/SPARC"><img src="https://raw.githubusercontent.com/AtharvaLakhe/SPARC/main/docs/media/globe.png" width="49%" alt="SPARC orbital terminal" /></a>
  <a href="https://github.com/AtharvaLakhe/CarbonLedger"><img src="https://raw.githubusercontent.com/AtharvaLakhe/CarbonLedger/master/docs/screenshots/live-operations.png" width="49%" alt="CarbonLedger live operations dashboard" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/github/last-commit/AtharvaLakhe/PSR-Net?style=flat-square&label=PSR-Net&labelColor=0D1117&color=FFB454" alt="PSR-Net last commit" />
  <img src="https://img.shields.io/github/last-commit/AtharvaLakhe/SPARC?style=flat-square&label=SPARC&labelColor=0D1117&color=FFB454" alt="SPARC last commit" />
  <img src="https://img.shields.io/github/last-commit/AtharvaLakhe/CarbonLedger?style=flat-square&label=CarbonLedger&labelColor=0D1117&color=FFB454" alt="CarbonLedger last commit" />
  <img src="https://img.shields.io/github/last-commit/AtharvaLakhe/FancePro?style=flat-square&label=FancePro&labelColor=0D1117&color=FFB454" alt="FancePro last commit" />
  <img src="https://img.shields.io/github/last-commit/AtharvaLakhe/LancePro?style=flat-square&label=LancePro&labelColor=0D1117&color=FFB454" alt="LancePro last commit" />
</p>

---

## Currently building

**repo-evolve** — a code reviewer whose answer key is the repository's own future.

Every static-analysis tool is stateless: it emits findings and never learns whether they were right. repo-evolve records what it predicted, waits for the commit history to grade it, trains on the result, and ranks code and design findings in one list from one model. It is deliberately split in two — a web half that analyses but executes nothing, and a local daemon that actually applies patches and runs your build. The web app cannot verify anything, and says so on every result.

---

## Toolkit

**Languages**

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
  <img src="https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=cplusplus&logoColor=white" alt="C++" />
  <img src="https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white" alt="Java" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3" />
</p>

**AI & scientific computing**

<p>
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch" />
  <img src="https://img.shields.io/badge/ONNX-005CED?style=for-the-badge&logo=onnx&logoColor=white" alt="ONNX" />
  <img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy" />
  <img src="https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white" alt="Groq" />
</p>

**Frontend**

<p>
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/Three.js-000000?style=for-the-badge&logo=threedotjs&logoColor=white" alt="Three.js" />
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/Tailwind-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind CSS" />
  <img src="https://img.shields.io/badge/MapLibre-295DAA?style=for-the-badge&logo=maplibre&logoColor=white" alt="MapLibre GL" />
  <img src="https://img.shields.io/badge/WebGL-990000?style=for-the-badge&logo=webgl&logoColor=white" alt="WebGL" />
  <img src="https://img.shields.io/badge/Recharts-22B5BF?style=for-the-badge&logo=chartdotjs&logoColor=white" alt="Recharts" />
</p>

**Backend & tooling**

<p>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic" />
  <img src="https://img.shields.io/badge/Uvicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white" alt="Uvicorn" />
  <img src="https://img.shields.io/badge/Node.js-5FA04E?style=for-the-badge&logo=nodedotjs&logoColor=white" alt="Node.js" />
  <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git" />
  <img src="https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright" />
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="GitHub Actions" />
  <img src="https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" alt="Vercel" />
</p>

---

## Activity

<p align="center">
  <img src="https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=AtharvaLakhe&theme=github_dark" alt="Profile summary" />
</p>

<p align="center">
  <img src="https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=AtharvaLakhe&theme=github_dark" height="200" alt="Repositories per language" />
  <img src="https://github-profile-summary-cards.vercel.app/api/cards/most-commit-language?username=AtharvaLakhe&theme=github_dark" height="200" alt="Most committed language" />
</p>

<p align="center">
  <img src="https://streak-stats.demolab.com?user=AtharvaLakhe&background=0D1117&border=30363D&stroke=30363D&ring=FFB454&fire=FFB454&currStreakLabel=FFB454&sideLabels=C9D1D9&currStreakNum=C9D1D9&sideNums=C9D1D9&dates=8B949E" height="165" alt="Contribution streak" />
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/AtharvaLakhe/AtharvaLakhe/main/profile-3d-contrib/profile-night-rainbow.svg" alt="3D contribution calendar" />
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/AtharvaLakhe/AtharvaLakhe/output/github-contribution-grid-snake-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/AtharvaLakhe/AtharvaLakhe/output/github-contribution-grid-snake.svg" />
    <img alt="Contribution snake" src="https://raw.githubusercontent.com/AtharvaLakhe/AtharvaLakhe/output/github-contribution-grid-snake.svg" />
  </picture>
</p>

---

## Open source

Everything here is built to be read, and most of it ships under MIT or Apache-2.0. Issues and pull requests are welcome — **SPARC** and **PSR-Net** have the most surface area for contributors, with methodology docs, an API contract, and a reproducible evaluation script.

<p align="center">
  <img src="https://img.shields.io/github/license/AtharvaLakhe/SPARC?style=flat-square&label=SPARC&labelColor=0D1117&color=30363D" alt="SPARC license" />
  <img src="https://img.shields.io/github/license/AtharvaLakhe/CarbonLedger?style=flat-square&label=CarbonLedger&labelColor=0D1117&color=30363D" alt="CarbonLedger license" />
  <img src="https://img.shields.io/github/license/AtharvaLakhe/FancePro?style=flat-square&label=FancePro&labelColor=0D1117&color=30363D" alt="FancePro license" />
  <img src="https://img.shields.io/badge/PSR--Net-MIT-30363D?style=flat-square&labelColor=0D1117" alt="PSR-Net license" />
</p>

<p align="center">
  <a href="mailto:atharvalakhe09@gmail.com"><img src="https://img.shields.io/badge/Email-atharvalakhe09%40gmail.com-FFB454?style=for-the-badge&logo=gmail&logoColor=0D1117" alt="Email" /></a>
  <a href="https://github.com/AtharvaLakhe"><img src="https://img.shields.io/badge/GitHub-AtharvaLakhe-30363D?style=for-the-badge&logo=github" alt="GitHub" /></a>
</p>
