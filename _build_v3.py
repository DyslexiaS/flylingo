#!/usr/bin/env python3
"""V3 itinerary prototype.

Visual concept: a Taipei-to-Philippines itinerary. The page is the document.
Brand green #3A7C30 and brand yellow #FEC107 stay exactly the logo colors.
Paper, ink, coral (斯巴達) and ocean (官方考場) are the extra colors.

One motion: the route rail on the process board, tied to scroll.
"""
import _build_redesign as base

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FlyLingo 飛語｜從語言出發，飛向世界</title>
__OG__
__FAVICON__
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@vp-tw/taipei-sans-tc/dist/Regular/TaipeiSansTCBeta-Regular.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@vp-tw/taipei-sans-tc/dist/Bold/TaipeiSansTCBeta-Bold.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400&family=Share+Tech+Mono&display=swap" rel="stylesheet">
<script>if (!matchMedia("(prefers-reduced-motion: reduce)").matches && CSS.supports("animation-timeline", "view()")) document.documentElement.classList.add("motion");</script>
<style>
:root {
  --green: #3A7C30;
  --green-dark: #2C6124;
  --yellow: #FEC107;
  --yellow-ink: #7A5A00;
  --ink: #1B2119;
  --paper: #F3EEE6;
  --ticket: #FBF8F3;
  --hair: #C9C0B2;
  --muted: #5E584E;
  --coral: #A8401F;
  --ocean: #1D5A8A;
  --board: #1B2119;
  --sans: "Taipei Sans TC", "PingFang TC", sans-serif;
  --serif: "Noto Serif TC", PMingLiU, serif;
  --mono: "Share Tech Mono", ui-monospace, monospace;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; overflow-x: clip; }
body {
  margin: 0; background: var(--paper); color: var(--ink);
  font-family: var(--serif); font-size: 17.5px; font-weight: 400; line-height: 1.8;
  text-autospace: ideograph-alpha ideograph-numeric;
}
@media (max-width: 800px) {
  body.menu-pad { padding-bottom: 86px; }
}
img { max-width: 100%; }
a { color: var(--green-dark); text-decoration-thickness: 1px; text-underline-offset: 3px; }
a:hover { color: var(--green); }
button, input { font: inherit; color: inherit; }
:focus-visible { outline: 2px solid var(--green); outline-offset: 3px; }
h1, h2, h3, .ui, .btn, .gate, header, footer, .pass, .board, .leg, .row, .mark, summary {
  font-family: var(--sans);
}
h1, h2, h3, .btn, .flight, .mega { font-weight: 700; }
h1 { font-size: 39px; line-height: 1.15; letter-spacing: -0.02em; margin: 11px 0; }
h2 { font-size: 29px; line-height: 1.25; margin: 0 0 11px; }
h3 { font-size: 20px; line-height: 1.35; margin: 0; font-weight: 700; }
p { margin: 0 0 11px; }
.mono { font-family: var(--mono); font-weight: 400; letter-spacing: 0.04em; }
.muted { color: var(--muted); }
.wrap { width: min(1120px, calc(100% - 36px)); margin-inline: auto; }
.skip {
  position: absolute; left: 11px; top: -40px; background: var(--yellow); color: var(--ink);
  padding: 6px 11px; z-index: 80;
}
.skip:focus { top: 11px; }

header.site {
  position: sticky; top: 0; z-index: 30; background: var(--paper);
  border-bottom: 1px solid var(--ink);
}
.head { display: flex; align-items: center; gap: 22px; height: 68px; }
.logo-word { width: 108px; height: 52px; display: block; }
.nav { display: flex; gap: 4px; }
.nav a {
  font-family: var(--sans); font-size: 15px; color: var(--ink); text-decoration: none;
  padding: 6px 11px; border-radius: 2px;
}
.nav a[aria-current="page"] { background: var(--green); color: #fff; }
.menu-btn {
  display: none; margin-left: auto; width: 40px; height: 40px; border: 1px solid var(--ink);
  border-radius: 2px; background: var(--ticket); place-items: center;
}
.menu-btn span, .menu-btn span::before, .menu-btn span::after {
  display: block; width: 16px; height: 1.5px; background: var(--ink); position: relative;
}
.menu-btn span::before, .menu-btn span::after { content: ""; position: absolute; left: 0; }
.menu-btn span::before { top: -5px; }
.menu-btn span::after { top: 5px; }
.head-cta { margin-left: auto; }
.socials { display: flex; gap: 6px; }
.socials a {
  width: 32px; height: 32px; display: grid; place-items: center; border-radius: 2px;
  color: #fff; text-decoration: none;
}
.social-threads { background: #000; }
.social-instagram { background: #C13584; }
.social-facebook { background: #1877F2; }
.social-line { background: #06C755; }
.head-socials { margin-left: auto; }
.head-socials + .head-cta { margin-left: 0; }
.foot-socials { display: none; }

.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  height: 46px; padding: 0 16px; border: 0; border-radius: 2px;
  background: var(--green); color: #fff; text-decoration: none; font-size: 17px; font-weight: 700;
}
.btn:hover { background: var(--green-dark); color: #fff; }
.btn svg { display: block; }
.text-link { font-family: var(--sans); font-weight: 700; color: var(--green-dark); }

.hero {
  display: grid; grid-template-columns: minmax(0, 36em) minmax(240px, 1fr);
  gap: 29px 47px; align-items: end;
  padding: 47px 0 29px max(18px, calc((100vw - 1120px) / 2));
}
.kicker { font-family: var(--mono); font-size: 13px; color: var(--yellow-ink); margin: 0 0 11px; }
.flight {
  font-family: var(--mono); font-weight: 400; font-size: clamp(104px, 12vw, 136px);
  line-height: 0.82; letter-spacing: -0.04em; margin: 0;
}
.flight i {
  display: inline-block; width: 0.42em; height: 3px; margin: 0 0.08em 0.16em;
  background: var(--green); vertical-align: middle; position: relative;
}
.flight i::after {
  content: ""; position: absolute; right: -2px; top: -5px;
  border: 6px solid transparent; border-left: 9px solid var(--green);
}
.lede { max-width: 30em; font-size: 17.5px; line-height: 1.8; margin: 18px 0; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 18px; align-items: center; }

.pass {
  background: var(--ticket); color: var(--ink);
  border: 1px solid var(--ink); border-right: 0; border-radius: 12px 0 0 12px;
  position: relative; overflow: hidden;
}
.pass-stripe { height: 11px; background: var(--yellow); }
.pass-body { padding: 18px 22px 22px; display: grid; grid-template-columns: 1fr auto; gap: 11px 18px; }
.pass dl { margin: 0; display: grid; grid-template-columns: 4.5em 1fr; gap: 6px 11px; }
.pass dt { font-family: var(--mono); font-size: 13px; color: var(--muted); }
.pass dd { margin: 0; font-family: var(--sans); font-size: 17px; }
.pass-note { grid-column: 1 / -1; margin: 8px 0 0; font-family: var(--sans); font-size: 15px; }
.pass .blank { border-bottom: 1px solid var(--ink); min-width: 8em; display: inline-block; }
.stamp {
  width: 92px; height: 92px; border: 3px solid var(--green); border-radius: 50%;
  color: var(--green); display: grid; place-items: center; align-self: center;
  transform: rotate(-14deg); text-align: center; line-height: 1.05;
  box-shadow: inset 0 0 0 1px var(--yellow);
}
.stamp b { font-family: var(--mono); font-size: 15px; font-weight: 400; letter-spacing: 0.08em; }
.stamp small { font-family: var(--mono); font-size: 13px; color: var(--yellow-ink); }
.perf {
  height: 22px; margin: 0 8px;
  background: radial-gradient(circle at 11px 11px, var(--paper) 6px, transparent 7px) left center / 22px 22px repeat-x;
}

.mega-sec { padding: 76px 0 47px; }
.mega {
  font-family: var(--mono); font-weight: 400; font-size: clamp(120px, 22vw, 168px);
  line-height: 1; letter-spacing: -0.05em; margin: 0 0 16px;
}
.mega span { display: inline-block; background: var(--yellow); line-height: 0.92; padding: 0 0.08em 0.04em; }
.mega-row { display: flex; justify-content: space-between; gap: 18px; align-items: end; flex-wrap: wrap; }
.mega-rule { height: 11px; background: var(--green); margin-top: 18px; width: calc(100% + max(18px, (100vw - 1120px) / 2)); }

.board { background: var(--board); color: var(--paper); padding: 76px 0 64px; }
.board h2, .board h3 { color: var(--paper); }
.board .kicker { color: var(--yellow); }
.board-top { display: flex; justify-content: space-between; gap: 18px; align-items: end; margin-bottom: 29px; }
.board-top p { max-width: 28em; color: rgba(243,238,230,.78); margin: 0; }
.rail-wrap { position: relative; padding-left: 28px; }
.route-rail {
  position: absolute; left: 7px; top: 8px; bottom: 8px; width: 2px; background: var(--yellow);
}
.motion .route-rail {
  transform: scaleY(0); transform-origin: top center;
  animation: rail-draw linear both;
  animation-timeline: view(block);
  animation-range: entry 5% cover 55%;
}
@keyframes rail-draw { to { transform: scaleY(1); } }
.tpe-dot {
  position: absolute; left: 2px; top: 0; width: 12px; height: 12px; border-radius: 50%;
  background: var(--green); box-shadow: 0 0 0 3px var(--board);
}
.phase { margin: 29px 0 8px; font-family: var(--mono); font-size: 13px; color: var(--yellow); }
.leg {
  display: grid; grid-template-columns: 58px minmax(0, 1.05fr) minmax(0, 1.25fr) minmax(0, 1.45fr);
  gap: 11px 18px; padding: 16px 0; border-top: 1px solid rgba(243,238,230,.28);
  position: relative;
}
.leg .no { font-family: var(--mono); font-size: 23px; color: var(--yellow); line-height: 1; }
.leg .role { font-family: var(--mono); font-size: 13px; color: var(--yellow); display: block; margin-bottom: 2px; }
.leg p { margin: 0; color: var(--paper); }
.you-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.you-tags span {
  background: var(--yellow); color: var(--ink); font-family: var(--sans); font-size: 13px;
  padding: 1px 6px; border-radius: 2px;
}

.picks { padding: 64px 0 47px; }
.pick {
  display: grid; grid-template-columns: 72px minmax(0, 1.6fr) minmax(0, 1fr) auto;
  gap: 11px 18px; align-items: baseline; padding: 14px 0;
  border-top: 1px solid var(--ink); color: inherit; text-decoration: none;
}
.pick:hover { color: var(--green-dark); }
.pick .code { font-family: var(--mono); font-size: 20px; }
.pick .meta { color: var(--muted); font-family: var(--sans); font-size: 15px; }

.page { padding: 29px 0 76px; }
.filters { display: flex; flex-direction: column; gap: 11px; margin: 18px 0 22px; }
.filter-line { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.filter-line .lab { font-family: var(--mono); font-size: 13px; color: var(--muted); width: 4.2em; }
.gate {
  border: 1px solid var(--ink); background: transparent; border-radius: 2px;
  padding: 4px 10px; font-size: 15px; cursor: pointer;
}
.gate[aria-pressed="true"] { background: var(--green); border-color: var(--green); color: #fff; }
.search {
  display: flex; border: 1px solid var(--ink); background: var(--ticket); border-radius: 0; max-width: 420px;
}
.search input { flex: 1; border: 0; background: transparent; padding: 8px 11px; border-radius: 0; }
.search button { border: 0; border-left: 1px solid var(--ink); background: transparent; padding: 0 12px; cursor: pointer; }

.school-row {
  display: grid; grid-template-columns: 64px minmax(0, 1.7fr) minmax(0, 1fr) auto;
  gap: 8px 16px; align-items: center; padding: 14px 0; border-top: 1px solid var(--hair);
}
.school-row a { color: inherit; text-decoration: none; }
.school-row a:hover h3 { color: var(--green-dark); }
.school-row .code { font-family: var(--mono); font-size: 18px; }
.cmp {
  font-family: var(--sans); font-size: 13px; display: flex; align-items: center; gap: 6px;
  border: 1px solid var(--ink); border-radius: 2px; padding: 4px 8px; background: var(--ticket); cursor: pointer;
}
.cmp input { accent-color: var(--green); }
.mark { font-family: var(--mono); font-size: 13px; }
.mark.sparta { color: var(--coral); }
.mark.semi { background: var(--yellow); color: var(--ink); padding: 0 4px; }
.mark.exam { color: var(--ocean); }
.pager { display: flex; gap: 6px; align-items: center; margin-top: 18px; }
.pager button {
  min-width: 36px; height: 36px; border: 1px solid var(--ink); background: transparent;
  border-radius: 2px; cursor: pointer; font-family: var(--mono);
}
.pager button[aria-current="page"] { background: var(--ink); color: var(--paper); }
.pager button:disabled { opacity: 0.35; }

.compare { display: grid; grid-template-columns: auto 1fr 1fr; gap: 11px; margin: 11px 0 29px; align-items: stretch; }
.weeks { display: flex; flex-direction: column; gap: 6px; }
.ticket {
  border: 1px solid var(--ink); border-radius: 12px; background: var(--ticket); overflow: hidden;
}
.ticket header { display: flex; justify-content: space-between; gap: 11px; padding: 11px 14px; background: var(--yellow); }
.ticket header a { color: var(--ink); font-family: var(--sans); font-weight: 700; text-decoration: none; }
.ticket table { width: 100%; border-collapse: collapse; }
.ticket th, .ticket td { text-align: left; padding: 8px 14px; border-top: 1px solid var(--hair); vertical-align: top; }
.ticket th { font-family: var(--mono); font-size: 13px; font-weight: 400; color: var(--muted); width: 4.5em; }
.ticket td { font-family: var(--sans); font-size: 15px; }
.empty-ticket { display: grid; place-items: center; min-height: 180px; color: var(--muted); padding: 18px; }

.crumbs { font-family: var(--sans); font-size: 15px; margin-bottom: 18px; }
.crumbs a { color: var(--muted); }
.shot {
  margin: 0 0 18px; position: relative; aspect-ratio: 3 / 2; background: #E4DCCE; overflow: hidden;
}
.shot img { width: 100%; height: 100%; object-fit: cover; filter: sepia(0.28) contrast(1.04) saturate(0.8); display: block; }
.shot::after {
  content: ""; position: absolute; inset: 0; pointer-events: none; mix-blend-mode: multiply; opacity: 0.55;
  background-image: radial-gradient(rgba(27,33,25,.35) 0.55px, transparent 0.7px);
  background-size: 3px 3px;
}
.shot figcaption, .shot-empty span {
  position: absolute; left: 14px; bottom: 12px; z-index: 1;
  font-family: var(--mono); font-size: 13px; background: var(--yellow); color: var(--ink); padding: 2px 6px;
}
.shot-empty { display: block; }
.shot-empty .big {
  position: absolute; left: 16px; top: 12px; z-index: 1;
  font-family: var(--mono); font-size: 64px; line-height: 1; color: rgba(27,33,25,.45);
}
.thumbs { display: flex; gap: 6px; margin: -8px 0 18px; }
.thumbs button { border: 1px solid var(--ink); padding: 0; width: 76px; height: 52px; border-radius: 0; background: none; cursor: pointer; }
.thumbs img { width: 100%; height: 100%; object-fit: cover; filter: sepia(0.28) saturate(0.8); display: block; }
.split { display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(220px, 0.7fr); gap: 29px; align-items: start; }
.facts { width: 100%; border-collapse: collapse; }
.facts th, .facts td { text-align: left; vertical-align: top; padding: 10px 0; border-top: 1px solid var(--hair); }
.facts th { font-family: var(--mono); font-size: 13px; font-weight: 400; color: var(--muted); width: 6.5em; padding-right: 11px; }
.aside-box { border: 1px solid var(--ink); border-radius: 12px; padding: 16px; background: var(--ticket); position: sticky; top: 84px; }
.aside-box p { font-size: 15px; }
.fac { columns: 2; gap: 22px; margin: 0; padding: 0; }
.fac li { break-inside: avoid; list-style: none; border-top: 1px solid var(--hair); padding: 6px 0; font-family: var(--sans); font-size: 15px; }

.faq-hot a, .cat-row, .post {
  display: grid; grid-template-columns: auto 1fr auto; gap: 14px; align-items: baseline;
  padding: 12px 0; border-top: 1px solid var(--ink); color: inherit; text-decoration: none;
}
.cat-row { grid-template-columns: 1fr auto; }
details.q { border-top: 1px solid var(--hair); }
details.q summary {
  display: flex; justify-content: space-between; gap: 16px; align-items: center;
  padding: 14px 0; cursor: pointer; font-weight: 700; list-style: none;
}
details.q summary::-webkit-details-marker { display: none; }
.pm { width: 14px; height: 14px; position: relative; flex: none; }
.pm::before, .pm::after { content: ""; position: absolute; background: currentColor; }
.pm::before { left: 0; right: 0; top: 6px; height: 1.5px; }
.pm::after { top: 0; bottom: 0; left: 6px; width: 1.5px; }
details[open] .pm::after { opacity: 0; }
details.q .a { padding: 0 0 14px; max-width: 38em; color: var(--muted); }
.wp h2 { font-size: 29px; margin: 29px 0 8px; }
.wp h3 { margin: 18px 0 6px; }
.wp p, .wp li { max-width: 38em; }
.wp ul, .wp ol { padding-left: 1.2em; }
.wp blockquote { margin: 18px 0; padding: 4px 0 4px 14px; border-left: 4px solid var(--yellow); max-width: 38em; }
.wp table { border-collapse: collapse; width: min(100%, 40em); margin: 11px 0 18px; }
.wp th, .wp td { border-top: 1px solid var(--ink); text-align: left; padding: 8px 11px 8px 0; vertical-align: top; }
.wp th { font-family: var(--mono); font-size: 13px; font-weight: 400; }
.wp img { aspect-ratio: 3 / 2; object-fit: cover; filter: sepia(0.28) saturate(0.8); }
.art-layout { display: grid; grid-template-columns: minmax(0, 1fr) 280px; gap: 18px; align-items: start; margin-top: 8px; }
.article-panel {
  min-width: 0; background: var(--ticket); border: 1px solid var(--hair); border-radius: 12px;
  padding: 8px 28px 28px;
}
.art-aside { position: sticky; top: 84px; }
.toc { background: var(--ticket); border: 1px solid var(--hair); border-radius: 12px; }
.toc summary {
  display: flex; justify-content: space-between; align-items: center; gap: 12px;
  padding: 16px 18px 12px; cursor: pointer; list-style: none; font-weight: 700; font-size: 18px;
}
.toc summary::-webkit-details-marker { display: none; }
.toc summary svg { color: var(--muted); flex: none; }
.toc[open] summary svg { transform: rotate(180deg); }
.toc nav { display: grid; padding: 0 14px 16px; }
.toc nav a {
  display: block; padding: 11px 12px; border-radius: 8px; color: var(--muted);
  text-decoration: none; font-family: var(--sans); font-size: 16px; line-height: 1.45;
  box-shadow: inset 2px 0 0 var(--hair);
}
.toc nav a:hover { color: var(--ink); background: var(--paper); }
.toc nav a.active { color: var(--ink); font-weight: 700; box-shadow: inset 3px 0 0 var(--green); }
.wp h2 { scroll-margin-top: 88px; }

.thumb-line {
  display: none; position: fixed; left: 11px; right: 11px; bottom: 11px; z-index: 40;
  height: 52px; border-radius: 2px;
}
footer.site { border-top: 1px solid var(--ink); padding: 29px 0 47px; }
.foot { display: flex; justify-content: space-between; gap: 22px; align-items: end; flex-wrap: wrap; }
.brandline { display: flex; align-items: center; gap: 18px; }
.brandline p { margin: 0; font-family: var(--sans); font-weight: 700; font-size: 18px; }
.brandline em { font-style: normal; background: var(--yellow); }
.foot nav { display: flex; gap: 16px; flex-wrap: wrap; }
.foot nav a { font-family: var(--sans); color: var(--ink); text-decoration: none; font-size: 15px; }

@media (max-width: 800px) {
  h1 { font-size: 32px; }
  .menu-btn { display: grid; }
  .head-cta, .head-socials { display: none; }
  .nav {
    display: none; position: absolute; top: 68px; left: 0; right: 0;
    flex-direction: column; background: var(--ticket); border-bottom: 1px solid var(--ink); padding: 8px 18px 14px;
  }
  header.site.open .nav { display: flex; }
  .hero { grid-template-columns: 1fr; padding: 22px 18px 8px; }
  .lede { margin: 12px 0; }
  .pass-body { padding: 12px 14px 8px; }
  .stamp { width: 78px; height: 78px; }
  .flight { font-size: 80px; }
  .perf { height: 12px; }
  .pass { border-right: 1px solid var(--ink); border-radius: 12px; }
  .leg { grid-template-columns: 46px 1fr; }
  .leg .fly, .leg .you { grid-column: 2; }
  .pick, .school-row { grid-template-columns: 52px 1fr; }
  .pick .meta, .school-row .stay { grid-column: 2; }
  .compare { grid-template-columns: 1fr; }
  .weeks { flex-direction: row; flex-wrap: wrap; }
  .split { grid-template-columns: 1fr; }
  .aside-box { position: static; }
  .ask { display: none; }
  .thumb-line { display: inline-flex; }
  .foot-socials { display: flex; }
  .fac { columns: 1; }
  .art-layout { grid-template-columns: 1fr; }
  .art-aside { position: static; order: -1; }
  .article-panel { padding: 4px 16px 20px; }
  .mega-rule { width: 100%; }
  footer.site { padding-bottom: 96px; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  .motion .route-rail { animation: none; transform: none; }
}
</style>
</head>
<body class="menu-pad">
<a class="skip" href="#main">跳到內容</a>
<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">
  <symbol id="mark-word" viewBox="160 116 1040 510">__WORD__</symbol>
  <symbol id="mark-star" viewBox="155 115 760 800">__STAR__</symbol>
</svg>
<header class="site">
  <div class="wrap head">
    <a href="#home" aria-label="FlyLingo 飛語首頁">
      <svg class="logo-word" viewBox="0 0 1040 510" role="img" aria-label="FlyLingo 飛語"><use href="#mark-word"/></svg>
    </a>
    <nav class="nav" id="nav" aria-label="主選單">
      <a href="#schools" data-nav="schools">學校</a>
      <a href="#process" data-nav="process">代辦流程</a>
      <a href="#faq" data-nav="faq">常見問題</a>
      <a href="#blog" data-nav="blog">部落格</a>
    </nav>
    <button class="menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="nav" aria-label="選單"><span></span></button>
    <div class="socials head-socials" aria-label="社群">__HEAD_SOCIALS__</div>
    <a class="btn head-cta" href="__LINE__" target="_blank" rel="noopener">__LINE_ICON__加 LINE 諮詢</a>
  </div>
</header>
<main id="main">
  <section data-view="home">
    <div class="hero">
      <div>
        <p class="kicker">TPE · 直飛約 2–3 小時 · 43 個校區</p>
        <p class="flight">TPE<i></i>CEB</p>
        <h1>從語言出發，<br>飛向世界</h1>
        <p class="lede">先聽你的目標、週數和預算，再幫你選校、報名，一路陪到抵達。住宿、接機、在學找誰，出發前講清楚。</p>
        <div class="hero-actions">
          <a class="text-link" href="__LINE__" target="_blank" rel="noopener">加 LINE，拿 2–4 間報價</a>
          <a class="text-link" href="#schools">看 43 個校區</a>
        </div>
      </div>
      <aside class="pass" aria-label="行程單">
        <div class="pass-stripe"></div>
        <div class="pass-body">
          <dl>
            <dt>航班</dt><dd class="mono">FL 04</dd>
            <dt>旅客</dt><dd><span class="blank">&nbsp;</span></dd>
            <dt>目的地</dt><dd>宿霧／碧瑤／克拉克</dd>
            <dt>週數</dt><dd>4–12 週</dd>
            <dt>住宿</dt><dd>校內宿舍或飯店</dd>
          </dl>
          <div class="stamp"><b>FLY<br>LINGO</b><small>蓋章處</small></div>
          <p class="pass-note">下一格把目標、週數、預算傳給飛語。章蓋在 LINE 上。</p>
        </div>
        <div class="perf"></div>
      </aside>
    </div>
    <section class="mega-sec">
      <div class="wrap">
        <p class="mega"><span>43</span></p>
        <div class="mega-row">
          <p style="max-width:22em;margin:0">個校區，在宿霧、碧瑤、克拉克、打拉、馬尼拉。先挑城市和強度，再讓飛語收到 2–4 間。</p>
          <p class="mono" style="margin:0">CEB · BAG · CRK · TAR · MNL</p>
        </div>
        <div class="mega-rule"></div>
      </div>
    </section>
    <section class="board" id="board">
      <div class="wrap">
        <div class="board-top">
          <div>
            <p class="kicker">TPE 出發</p>
            <h2>八步，誰做什麼</h2>
          </div>
          <p>每一步寫兩欄：飛語做的，和你要準備的。做完那一格，才進下一格。</p>
        </div>
        <div class="rail-wrap">
          <div class="tpe-dot" aria-hidden="true"></div>
          <div class="route-rail" aria-hidden="true"></div>
          <div id="home-legs"></div>
        </div>
      </div>
    </section>
    <section class="picks">
      <div class="wrap">
        <div class="board-top" style="margin-bottom:11px">
          <h2>先看這 6 間</h2>
          <a class="text-link" href="#schools">全部 43 個校區</a>
        </div>
        <div id="home-picks"></div>
      </div>
    </section>
  </section>

  <section data-view="schools" hidden>
    <div class="wrap page">
      <p class="kicker">43 CAMPUSES</p>
      <h1>學校清單</h1>
      <p class="lede">用城市、強度、住宿把範圍縮小。勾兩間，下面排出兩張行程票。學費這版還沒有公開數字，預算欄先留著問 LINE。</p>
      <form class="search" id="school-search">
        <input id="school-q" type="search" placeholder="校名、CIA、PINES、宿霧" aria-label="搜尋學校">
        <button type="submit" aria-label="搜尋">搜</button>
      </form>
      <div class="filters" id="filters"></div>
      <div id="compare"></div>
      <p class="mono" id="school-count"></p>
      <div id="school-list"></div>
      <nav class="pager" id="pager" aria-label="學校清單分頁"></nav>
    </div>
  </section>

  <section data-view="school" hidden>
    <div class="wrap page" id="detail"></div>
  </section>

  <section data-view="process" hidden>
    <div class="wrap page">
      <p class="kicker">TPE → 結業</p>
      <h1>代辦流程</h1>
      <p class="lede">你負責把條件說清楚，也負責最後決定。送件、對接機、列文件，是飛語的工作。</p>
    </div>
    <div class="board">
      <div class="wrap">
        <div class="rail-wrap">
          <div class="tpe-dot" aria-hidden="true"></div>
          <div class="route-rail" aria-hidden="true"></div>
          <div id="process-legs"></div>
        </div>
      </div>
    </div>
  </section>

  <section data-view="faq" hidden>
    <div class="wrap page" id="faq"></div>
  </section>

  <section data-view="blog" hidden>
    <div class="wrap page" id="blog"></div>
  </section>

  <section data-view="article" hidden>
    <div class="wrap page" id="article"></div>
  </section>
</main>
<footer class="site">
  <div class="wrap foot">
    <div class="brandline">
      <svg class="logo-word" viewBox="0 0 1040 510" role="img" aria-label="FlyLingo 飛語"><use href="#mark-word"/></svg>
      <p>從語言出發，<em>飛向世界。</em></p>
    </div>
    <nav aria-label="頁尾">
      <a href="#schools">學校</a>
      <a href="#process">代辦流程</a>
      <a href="#faq">常見問題</a>
      <a href="#blog">部落格</a>
    </nav>
    <div class="socials foot-socials" aria-label="社群">__FOOT_SOCIALS__</div>
  </div>
</footer>
<a class="btn thumb-line" href="__LINE__" target="_blank" rel="noopener">__LINE_ICON__加 LINE 諮詢</a>
<script>
const DATA = __DATA__;
const LINE = DATA.line;
const CITY_CODE = { "宿霧": "CEB", "碧瑤": "BAG", "克拉克": "CRK", "克拉克／打拉": "TAR", "馬尼拉": "MNL" };
const CITY_LABEL = { "克拉克／打拉": "打拉" };
const FLY = {
  "01": "聽你的目標、週數、預算，寫成需求摘要",
  "02": "比較城市、強度、住宿，收到 2–4 間",
  "03": "準備報價單和契約",
  "04": "送件給學校，收回入學許可和帳單",
  "05": "對接機時段，列出當地費用",
  "06": "依國籍和停留天數，列出入境文件",
  "07": "出發前 1–2 週說明一次，48 小時前再確認",
  "08": "入住後第一週和中段主動聯絡，直到結業"
};
const PHASES = [
  ["選校", ["01", "02"]],
  ["報名", ["03", "04"]],
  ["出發準備", ["05", "06", "07"]],
  ["抵達與在學", ["08"]]
];
const state = { city: "全部", course: "全部", kind: "全部", stay: "全部", q: "", page: 1, compare: [], weeks: "8" };
const PAGE = 8;

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function cityName(c) { return CITY_LABEL[c] || c; }
function schoolById(id) { return DATA.schools.find((s) => s.id === id); }
function splitList(s) { return String(s || "").split(/[；;、]/).map((x) => x.trim()).filter(Boolean); }
function stayLine(s) { return (s.accommodation || "住宿方式問 LINE").split(/[；;]/)[0]; }
function exams(s) { return (s.strengths || []).filter((x) => /考場/.test(x)); }
function kindMark(k) {
  const cls = k === "斯巴達" ? "sparta" : k === "半斯巴達" ? "semi" : "";
  return `<span class="mark ${cls}">${esc(k)}</span>`;
}
function stayMatch(s) {
  const a = s.accommodation || "";
  if (state.stay === "校內宿舍") return /宿舍|校內/.test(a);
  if (state.stay === "飯店") return /飯店|酒店/.test(a);
  return true;
}
function matchSchool(s) {
  if (state.city !== "全部" && s.city !== state.city) return false;
  if (state.course !== "全部" && !(s.filters || []).includes(state.course)) return false;
  if (state.kind !== "全部" && s.kind !== state.kind) return false;
  if (!stayMatch(s)) return false;
  if (state.q) {
    const blob = [s.name, s.brand, s.campus, s.city, s.style, s.kind, s.courses, ...(s.tags || [])].join(" ").toLowerCase();
    if (!blob.includes(state.q.toLowerCase())) return false;
  }
  return true;
}

function legsHTML() {
  const byId = Object.fromEntries(DATA.steps.map((s) => [s.id, s]));
  return PHASES.map(([title, ids]) => `
    <p class="phase">${esc(title)}</p>
    ${ids.map((id) => byId[id]).filter(Boolean).map((s) => `
      <article class="leg" id="step-${esc(s.id)}">
        <span class="no">${esc(s.id)}</span>
        <h3>${esc(s.title)}</h3>
        <p class="fly"><span class="role">飛語</span>${esc(FLY[s.id] || s.summary)}</p>
        <p class="you"><span class="role">你</span><span class="you-tags">${s.you.map((n) => `<span>${esc(n)}</span>`).join("")}</span></p>
      </article>`).join("")}
  `).join("");
}

function pickHTML(entry) {
  const s = schoolById(entry.id);
  if (!s) return "";
  return `<a class="pick" href="#school/${esc(s.id)}">
    <span class="code">${esc(CITY_CODE[s.city] || "")}</span>
    <span><strong>${esc(s.name)}</strong><br><span class="meta">${esc(cityName(s.city))} · ${esc(s.campus)}</span></span>
    <span class="meta">${kindMark(s.kind)} ${esc(entry.note || "")}</span>
    <span class="mono">→</span>
  </a>`;
}

function gate(attr, value, label, pressed) {
  return `<button class="gate" type="button" data-${attr}="${esc(value)}" aria-pressed="${pressed}">${esc(label)}</button>`;
}
function renderFilters() {
  const cities = ["全部", "宿霧", "碧瑤", "克拉克", "克拉克／打拉", "馬尼拉"];
  const courses = ["全部", "ESL", "雅思", "多益", "托福", "商務", "親子"];
  const kinds = ["全部", "半斯巴達", "斯巴達", "親子", "其他"];
  const stays = ["全部", "校內宿舍", "飯店"];
  const line = (lab, html) => `<div class="filter-line"><span class="lab">${lab}</span>${html}</div>`;
  document.getElementById("filters").innerHTML = [
    line("城市", cities.map((c) => gate("city", c, c === "全部" ? "全部" : cityName(c), state.city === c)).join("")),
    line("強度", kinds.map((k) => gate("kind", k, k, state.kind === k)).join("")),
    line("課程", courses.map((c) => gate("course", c, c, state.course === c)).join("")),
    line("住宿", stays.map((c) => gate("stay", c, c, state.stay === c)).join(""))
  ].join("");
}
function rowHTML(s) {
  const on = state.compare.includes(s.id);
  const ex = exams(s)[0];
  return `<div class="school-row">
    <span class="code">${esc(CITY_CODE[s.city] || "")}</span>
    <a href="#school/${esc(s.id)}"><h3>${esc(s.name)}</h3><span class="meta">${esc(cityName(s.city))} · ${esc(s.campus)} · ${kindMark(s.kind)}</span></a>
    <span class="stay meta">${esc(stayLine(s))}${ex ? `<br><span class="mark exam">${esc(ex)}</span>` : ""}</span>
    <label class="cmp"><input type="checkbox" data-cmp="${esc(s.id)}" ${on ? "checked" : ""}>比較</label>
  </div>`;
}
function ticketHTML(s) {
  if (!s) return `<div class="ticket empty-ticket">再勾一間，兩張票並排。</div>`;
  return `<article class="ticket">
    <header><a href="#school/${esc(s.id)}">${esc(s.name)}</a><span class="mono">${esc(CITY_CODE[s.city] || "")}</span></header>
    <table>
      <tr><th>城市</th><td>${esc(cityName(s.city))} · ${esc(s.campus)}</td></tr>
      <tr><th>週數</th><td>你填的 ${esc(state.weeks)} 週</td></tr>
      <tr><th>住宿</th><td>${esc(stayLine(s))}</td></tr>
      <tr><th>強度</th><td>${kindMark(s.kind)}　${esc(s.style || "")}</td></tr>
      <tr><th>預算</th><td><a href="${esc(LINE)}" target="_blank" rel="noopener">向 LINE 要這間的報價</a></td></tr>
    </table>
  </article>`;
}
function renderCompare() {
  const box = document.getElementById("compare");
  if (!state.compare.length) { box.innerHTML = ""; return; }
  const [a, b] = state.compare.map(schoolById);
  const weeks = ["4", "8", "12"].map((w) => gate("weeks", w, w + " 週", state.weeks === w)).join("");
  box.innerHTML = `<div class="compare">
    <div class="weeks"><span class="lab mono">你的週數</span>${weeks}</div>
    ${ticketHTML(a)}${ticketHTML(b)}
  </div>`;
}
function renderSchools() {
  const input = document.getElementById("school-q");
  if (input && document.activeElement !== input) input.value = state.q;
  renderFilters();
  renderCompare();
  const list = DATA.schools.filter(matchSchool);
  const pages = Math.max(1, Math.ceil(list.length / PAGE));
  state.page = Math.min(Math.max(1, state.page), pages);
  const shown = list.slice((state.page - 1) * PAGE, state.page * PAGE);
  document.getElementById("school-count").textContent = list.length + " 間";
  document.getElementById("school-list").innerHTML = shown.length
    ? shown.map(rowHTML).join("")
    : `<p>這個條件目前沒有學校。換個城市，或直接問 LINE。</p>`;
  const pager = document.getElementById("pager");
  if (pages <= 1) { pager.innerHTML = ""; return; }
  const nums = Array.from({ length: pages }, (_, i) => i + 1).map((n) =>
    `<button type="button" data-page="${n}" ${n === state.page ? 'aria-current="page"' : ""}>${n}</button>`).join("");
  pager.innerHTML = `<button type="button" data-page="${state.page - 1}" ${state.page === 1 ? "disabled" : ""} aria-label="上一頁">←</button>${nums}<button type="button" data-page="${state.page + 1}" ${state.page === pages ? "disabled" : ""} aria-label="下一頁">→</button>`;
}

function shotBlock(s) {
  const photos = (s.photos || []).filter((p) => p.src);
  if (!photos.length) {
    return `<figure class="shot shot-empty"><span class="big">${esc(CITY_CODE[s.city] || "PH")}</span><figcaption>照片位　3:2　${esc(cityName(s.city))}</figcaption></figure>`;
  }
  const thumbs = photos.length > 1 ? `<div class="thumbs">${photos.slice(0, 6).map((p, i) =>
    `<button type="button" data-shot="${i}" aria-label="第 ${i + 1} 張"><img src="${esc(p.src)}" alt=""></button>`).join("")}</div>` : "";
  return `<div class="gallery">
    <figure class="shot"><img alt="${esc(photos[0].caption || s.name)}" src="${esc(photos[0].src)}"><figcaption>${esc(photos[0].caption || photos[0].cat || "1 / " + photos.length)}</figcaption></figure>
    ${thumbs}
  </div>`;
}
function renderDetail(id) {
  const s = schoolById(id);
  const root = document.getElementById("detail");
  if (!s) { root.innerHTML = `<p>找不到這間學校。</p><p><a href="#schools">回學校清單</a></p>`; return; }
  const ex = exams(s);
  const courses = splitList(s.courses);
  const fac = splitList(s.facilities);
  root.innerHTML = `
    <p class="crumbs"><a href="#schools">學校</a> ／ <a href="#schools" data-city="${esc(s.city)}">${esc(cityName(s.city))}</a> ／ ${esc(s.name)}</p>
    <p class="kicker">${esc(CITY_CODE[s.city] || "")} · ${esc(s.campus)}</p>
    <h1>${esc(s.name)}</h1>
    <p>${kindMark(s.kind)}　${esc(s.style || "")}${ex.length ? `　<span class="mark exam">${ex.map(esc).join(" · ")}</span>` : ""}</p>
    ${shotBlock(s)}
    <div class="split">
      <table class="facts">
        <tr><th>成立</th><td>${esc(s.established || "資料待補")}</td></tr>
        <tr><th>人數</th><td>${esc(/未公開/.test(s.capacity || "") ? "學校未公開" : (s.capacity || "資料待補"))}</td></tr>
        <tr><th>住宿</th><td>${esc(s.accommodation || "問 LINE")}</td></tr>
        <tr><th>洗衣</th><td>${esc(s.laundry || "問 LINE")}</td></tr>
        <tr><th>課程</th><td>${courses.length ? courses.map(esc).join("、") : "資料待補"}</td></tr>
        <tr><th>適合</th><td>${esc(s.suitable || "資料待補")}</td></tr>
        <tr><th>地址</th><td>${esc(s.address || "")}<br><span class="muted">${esc(s.addressEn || "")}</span>${/^https?:/.test(s.maps || "") ? `<br><a href="${esc(s.maps)}" target="_blank" rel="noopener">在地圖上打開</a>` : ""}</td></tr>
      </table>
      <aside class="aside-box">
        <p class="mono">FL · ${esc(s.brand || "")}</p>
        <p>週數和房型決定報價。把這間的名字傳給飛語。</p>
        <a class="btn ask" href="${esc(LINE)}" target="_blank" rel="noopener">__LINE_ICON__問這間的報價</a>
      </aside>
    </div>
    ${fac.length ? `<h2 style="margin-top:29px">設施</h2><ul class="fac">${fac.map((f) => `<li>${esc(f)}</li>`).join("")}</ul>` : ""}
    ${(s.strengths || []).length ? `<h2 style="margin-top:29px">這間常被提到的</h2><ul class="fac">${s.strengths.map((f) => `<li>${esc(f)}</li>`).join("")}</ul>` : ""}`;
  const photos = (s.photos || []).filter((p) => p.src);
  root.querySelectorAll("[data-shot]").forEach((btn) => btn.addEventListener("click", () => {
    const p = photos[Number(btn.dataset.shot)];
    const img = root.querySelector(".shot img");
    const cap = root.querySelector(".shot figcaption");
    if (img && p) img.src = p.src;
    if (cap && p) cap.textContent = p.caption || p.cat || "";
  }));
  const crumb = root.querySelector("[data-city]");
  if (crumb) crumb.addEventListener("click", () => { state.city = s.city; state.page = 1; });
}

function renderProcess() { document.getElementById("process-legs").innerHTML = legsHTML(); }

function renderFaq(id) {
  const root = document.getElementById("faq");
  const vol = `<span class="muted">　範例回答，上線前替換。</span>`;
  if (id) {
    const cat = DATA.faq.find((c) => c.id === id);
    if (!cat) { root.innerHTML = `<p>找不到這個分類。</p>`; return; }
    root.innerHTML = `<p class="crumbs"><a href="#faq">常見問題</a> ／ ${esc(cat.title)}</p>
      <h1>${esc(cat.title)}</h1>
      <p class="muted">每一題目前都是範例回答。</p>
      ${cat.questions.map(([q, a], i) => `<details class="q"${i === 0 ? " open" : ""}><summary>${esc(q)}<span class="pm" aria-hidden="true"></span></summary><div class="a"><p>${esc(a)}</p>${vol}</div></details>`).join("")}
      <p style="margin-top:22px"><a class="text-link" href="${esc(LINE)}" target="_blank" rel="noopener">這題問 LINE</a></p>`;
    return;
  }
  const q = state.faqQ || "";
  const hits = q ? DATA.faq.flatMap((c) => c.questions.filter((pair) => (pair[0] + pair[1]).includes(q)).map((pair) => [c, pair])) : [];
  root.innerHTML = `<p class="kicker">FAQ</p><h1>常見問題</h1>
    <p class="lede">每一題目前都是範例回答。</p>
    <form class="search" id="faq-search"><input id="faq-q" type="search" value="${esc(q)}" placeholder="簽證、費用、住宿" aria-label="搜尋問題"><button type="submit">搜</button></form>
    ${q ? `<div style="margin-top:18px">${hits.length ? hits.map(([c, pair]) => `<a class="faq-hot" href="#faq/${esc(c.id)}"><span class="mono">${esc(c.title)}</span><span>${esc(pair[0])}</span><span>→</span></a>`).join("") : `<p>沒有對到的題目。換個詞，或直接問 LINE。</p>`}</div>` : `
    <h2 style="margin-top:29px">大家先問的</h2>
    <div>${DATA.hot.map((hid) => {
      const c = DATA.faq.find((x) => x.id === hid);
      const title = c && c.questions[0] ? c.questions[0][0] : hid;
      return `<a class="faq-hot" href="#faq/${esc(hid)}"><span class="mono">Q</span><span>${esc(title)}</span><span>→</span></a>`;
    }).join("")}</div>
    <h2 style="margin-top:36px">10 個分類</h2>
    <div>${DATA.faq.map((c) => `<a class="cat-row" href="#faq/${esc(c.id)}"><span>${esc(c.title)}</span><span class="mono">${c.questions.length} 題</span></a>`).join("")}</div>`}`;
  const form = document.getElementById("faq-search");
  if (form) form.addEventListener("submit", (e) => {
    e.preventDefault();
    state.faqQ = document.getElementById("faq-q").value.trim();
    renderFaq("");
  });
}

let articleSpy = null;
function stopArticleSpy() {
  if (articleSpy) window.removeEventListener("scroll", articleSpy);
  articleSpy = null;
}
const TOC_CHEV = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>`;

function readMin(html) {
  const text = html.replace(/<[^>]+>/g, "");
  return Math.max(1, Math.round(text.length / 300));
}
function renderBlog() {
  document.getElementById("blog").innerHTML = `<p class="kicker">NOTES</p><h1>出發前讀這幾篇</h1>
    <p class="lede">行李、城市、管理強度。文章之後會放到 WordPress，版面沿用標題、表、清單。</p>
    ${DATA.articles.map((a, i) => `<a class="post" href="#article/${esc(a.id)}">
      <span class="mono">${String(i + 1).padStart(2, "0")}</span>
      <span><span class="muted">${esc(a.kicker)}</span><br><strong>${esc(a.title)}</strong></span>
      <span class="mono">${readMin(a.html)} 分</span>
    </a>`).join("")}`;
}
function renderArticle(id, section) {
  const a = DATA.articles.find((x) => x.id === id);
  const root = document.getElementById("article");
  if (!a) { root.innerHTML = `<p>找不到這篇文章。</p>`; return; }
  const doc = new DOMParser().parseFromString(`<div>${a.html}</div>`, "text/html");
  const body = doc.body.firstElementChild;
  const heads = [...body.querySelectorAll("h2")];
  heads.forEach((h, i) => { if (!h.id) h.id = "sec-" + (i + 1); });
  document.title = a.title + "｜FlyLingo 飛語";
  const wide = matchMedia("(min-width: 801px)").matches;
  const toc = heads.length ? `<aside class="art-aside"><details class="toc"${wide ? " open" : ""}>
      <summary>本篇目錄${TOC_CHEV}</summary>
      <nav>${heads.map((h, i) => `<a href="#article/${esc(a.id)}/${esc(h.id)}" data-jump="${esc(h.id)}"${h.id === section || (!section && i === 0) ? ' class="active"' : ""}>${esc(h.textContent)}</a>`).join("")}</nav>
    </details></aside>` : "";
  root.innerHTML = `<p class="crumbs"><a href="#blog">部落格</a> ／ ${esc(a.kicker)}</p>
    <p class="kicker">${esc(a.kicker)} · ${readMin(a.html)} 分</p>
    <h1>${esc(a.title)}</h1>
    <p class="lede">${esc(a.excerpt)}</p>
    <div class="art-layout">
      <article class="article-panel"><div class="wp">${body.innerHTML}</div>
        <p style="margin-top:29px"><a class="text-link" href="${esc(LINE)}" target="_blank" rel="noopener">這篇的問題，問 LINE</a></p>
      </article>
      ${toc}
    </div>`;
  const links = [...root.querySelectorAll(".toc [data-jump]")];
  const mark = (sid) => links.forEach((x) => x.classList.toggle("active", x.dataset.jump === sid));
  const jump = (sid, smooth) => {
    const el = document.getElementById(sid);
    if (!el) return;
    mark(sid);
    history.replaceState(null, "", `#article/${a.id}/${sid}`);
    el.scrollIntoView({ behavior: smooth ? "smooth" : "auto", block: "start" });
  };
  root.onclick = (e) => {
    const link = e.target.closest(".toc [data-jump]");
    if (!link) return;
    e.preventDefault();
    jump(link.dataset.jump, true);
  };
  const liveHeads = [...root.querySelectorAll(".wp h2")];
  if (liveHeads.length) {
    articleSpy = () => {
      let cur = liveHeads[0];
      liveHeads.forEach((h) => { if (h.getBoundingClientRect().top <= 120) cur = h; });
      mark(cur.id);
    };
    window.addEventListener("scroll", articleSpy, { passive: true });
    if (section) requestAnimationFrame(() => jump(section, false));
    else articleSpy();
  }
}

function parseRoute() {
  const parts = (location.hash || "#home").replace(/^#/, "").split("?")[0].split("/").filter(Boolean);
  const known = ["home", "schools", "school", "process", "faq", "blog", "article"];
  const view = known.includes(parts[0]) ? parts[0] : "home";
  return { view, id: parts[1] || "", sub: parts[2] || "" };
}
function render() {
  stopArticleSpy();
  const route = parseRoute();
  document.querySelectorAll("[data-view]").forEach((el) => { el.hidden = el.dataset.view !== route.view; });
  const navKey = { school: "schools", article: "blog" }[route.view] || route.view;
  document.querySelectorAll("#nav a").forEach((a) => {
    if (a.dataset.nav === navKey) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  });
  document.querySelector("header.site").classList.remove("open");
  document.getElementById("menu-btn").setAttribute("aria-expanded", "false");
  if (route.view === "home") {
    document.getElementById("home-legs").innerHTML = legsHTML();
    document.getElementById("home-picks").innerHTML = DATA.featured.map(pickHTML).join("");
  }
  if (route.view === "schools") renderSchools();
  if (route.view === "school") renderDetail(route.id);
  if (route.view === "process") renderProcess();
  if (route.view === "faq") renderFaq(route.id);
  if (route.view === "blog") renderBlog();
  if (route.view === "article") renderArticle(route.id, route.sub);
  const titles = { home: "FlyLingo 飛語｜從語言出發，飛向世界", schools: "學校清單｜FlyLingo 飛語", school: "學校｜FlyLingo 飛語", process: "代辦流程｜FlyLingo 飛語", faq: "常見問題｜FlyLingo 飛語", blog: "部落格｜FlyLingo 飛語", article: "文章｜FlyLingo 飛語" };
  if (route.view !== "article") document.title = titles[route.view];
  if (!route.sub) window.scrollTo(0, 0);
}
document.getElementById("menu-btn").addEventListener("click", () => {
  const header = document.querySelector("header.site");
  const open = !header.classList.contains("open");
  header.classList.toggle("open", open);
  document.getElementById("menu-btn").setAttribute("aria-expanded", open ? "true" : "false");
});
document.getElementById("school-search").addEventListener("submit", (e) => e.preventDefault());
document.getElementById("school-q").addEventListener("input", (e) => { state.q = e.target.value.trim(); state.page = 1; renderSchools(); });
document.getElementById("filters").addEventListener("click", (e) => {
  const btn = e.target.closest(".gate");
  if (!btn) return;
  ["city", "course", "kind", "stay"].forEach((k) => { if (btn.dataset[k]) { state[k] = btn.dataset[k]; state.page = 1; } });
  renderSchools();
});
document.getElementById("compare").addEventListener("click", (e) => {
  const btn = e.target.closest("[data-weeks]");
  if (!btn) return;
  state.weeks = btn.dataset.weeks;
  renderCompare();
});
document.getElementById("school-list").addEventListener("change", (e) => {
  const box = e.target.closest("[data-cmp]");
  if (!box) return;
  const id = box.dataset.cmp;
  if (box.checked) { if (!state.compare.includes(id) && state.compare.length < 2) state.compare.push(id); else box.checked = state.compare.includes(id); }
  else state.compare = state.compare.filter((x) => x !== id);
  renderCompare();
});
document.getElementById("pager").addEventListener("click", (e) => {
  const btn = e.target.closest("[data-page]");
  if (!btn || btn.disabled || btn.getAttribute("aria-current")) return;
  state.page = Number(btn.dataset.page);
  renderSchools();
  document.getElementById("school-count").scrollIntoView({ block: "start" });
});
window.addEventListener("hashchange", render);
render();
</script>
</body>
</html>
"""


def main(data=None, word=None, star=None):
    if data is None:
        data, word, star = base.extract(base.SOURCE.read_text())
        data = base.with_process(data)
    html = TEMPLATE
    for key, value in {
        "__OG__": base.og_tags("flylingo-v3-itinerary.html"),
        "__FAVICON__": base.favicon_link(),
        "__HEAD_SOCIALS__": base.socials(skip=("line",)),
        "__FOOT_SOCIALS__": base.socials(),
        "__LINE_ICON__": base.LINE_ICON,
        "__LINE__": "https://lin.ee/oDiSotr",
        "__WORD__": word,
        "__STAR__": star,
    }.items():
        html = html.replace(key, value)
    html = html.replace("__DATA__", data)
    out = base.ROOT / "flylingo-v3-itinerary.html"
    out.write_text(html)
    print(f"wrote {out.name} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
