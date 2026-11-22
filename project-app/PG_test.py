"""
“桩”尽其用 · 项目初始框架
四个模块：价格地图 / 站点账单 / 治理沙盘 / 反馈中心

运行：
    streamlit run app.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="桩尽其用 · 价格与车位治理",
    page_icon=":material/ev_station:",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "stations.csv"

GLASS_CSS = """
<style>
:root {
  --glass-bg: rgba(255, 255, 255, 0.82);
  --glass-border: rgba(255, 255, 255, 0.92);
  --ink: #122a26;
}
html, body { background: #dce8e4; }
.stApp { background: transparent !important; }
[data-testid="stToolbar"], [data-testid="stDecoration"], footer { display: none !important; }
header[data-testid="stHeader"] {
  background: transparent !important;
  backdrop-filter: none !important;
}
[data-testid="stMainBlockContainer"] {
  position: fixed;
  top: 18px;
  right: 22px;
  bottom: 18px;
  left: auto;
  width: min(720px, calc(100vw - 340px));
  max-width: none;
  margin: 0;
  padding: 20px 22px 64px;
  overflow-y: auto;
  overflow-x: hidden;
  overscroll-behavior: contain;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  transition: width .55s cubic-bezier(.22, 1, .36, 1), padding .55s cubic-bezier(.22, 1, .36, 1);
  z-index: 3;
}
[data-testid="stMainBlockContainer"]::before {
  content: "";
  position: fixed;
  top: 18px;
  right: 22px;
  bottom: 18px;
  width: min(720px, calc(100vw - 340px));
  z-index: -1;
  background: linear-gradient(135deg, rgba(255,255,255,0.62), rgba(255,255,255,0.44));
  backdrop-filter: blur(46px) saturate(190%);
  -webkit-backdrop-filter: blur(46px) saturate(190%);
  border: 1px solid rgba(255,255,255,0.78);
  border-radius: 30px;
  box-shadow: 0 30px 80px rgba(12, 40, 34, 0.22), inset 0 1px 0 rgba(255,255,255,0.65);
  pointer-events: none;
  transition: opacity .4s ease, visibility .4s ease;
}
.st-key-map_bg {
  position: fixed !important;
  inset: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
  z-index: -2 !important;
}
.st-key-map_bg > div { height: 100vh !important; padding: 0 !important; }
.st-key-map_bg iframe, .st-key-map_bg canvas {
  width: 100vw !important;
  height: 100vh !important;
  z-index: -2 !important;
  border: 0 !important;
  outline: none !important;
}
section[data-testid="stSidebar"] {
  display: block !important;
  visibility: visible !important;
  transform: none !important;
  margin-left: 0 !important;
  width: 300px !important;
  min-width: 300px !important;
  z-index: 20 !important;
  background: transparent !important;
  transition: transform .55s cubic-bezier(.22, 1, .36, 1);
  will-change: transform;
  overflow: hidden !important;
  border: none !important;
  border-right: 0 !important;
  outline: 0 !important;
  box-shadow: none !important;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
section[data-testid="stSidebar"]::-webkit-scrollbar,
section[data-testid="stSidebar"] *::-webkit-scrollbar {
  width: 0 !important;
  height: 0 !important;
  display: none !important;
}
section[data-testid="stSidebar"] * {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
section[data-testid="stSidebar"] > div { background: transparent !important; border: none !important; }
section[data-testid="stSidebar"]::after {
  content: "";
  position: absolute;
  top: 0;
  right: -24px;
  width: 32px;
  height: 100%;
  background: linear-gradient(to right, #f2f6f2 0%, #f2f6f2 30%, rgba(242,246,242,0) 100%);
  pointer-events: none;
  z-index: 21;
}
section[data-testid="stSidebar"] > div:first-child {
  margin: 12px 0 12px 12px;
  width: auto !important;
  max-width: calc(100% - 12px);
  box-sizing: border-box;
  height: calc(100vh - 24px);
  padding: 10px 10px 16px;
  background: linear-gradient(135deg, rgba(255,255,255,0.66), rgba(255,255,255,0.46));
  backdrop-filter: blur(36px) saturate(190%);
  -webkit-backdrop-filter: blur(36px) saturate(190%);
  border: 0 !important;
  border-radius: 26px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
section[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar {
  width: 0;
  height: 0;
  display: none;
}
[data-testid="stMetric"] {
  background: rgba(255, 255, 255, 0.68) !important;
  backdrop-filter: blur(22px) saturate(170%);
  -webkit-backdrop-filter: blur(22px) saturate(170%);
  border: 1px solid rgba(255, 255, 255, 0.82) !important;
  border-radius: 18px !important;
  padding: 14px 16px !important;
  box-shadow: 0 12px 30px rgba(15, 40, 35, 0.10), inset 0 1px 0 rgba(255,255,255,0.7);
  transition: transform .2s ease, box-shadow .2s ease;
}
[data-testid="stMetric"]:hover {
  transform: translateY(-4px);
  box-shadow: 0 22px 46px rgba(15, 40, 35, 0.16), inset 0 1px 0 rgba(255,255,255,0.85);
}
[data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(255, 255, 255, 0.68) !important;
  backdrop-filter: blur(22px) saturate(170%);
  -webkit-backdrop-filter: blur(22px) saturate(170%);
  border: 1px solid rgba(255, 255, 255, 0.82) !important;
  border-radius: 18px !important;
  box-shadow: 0 12px 30px rgba(15, 40, 35, 0.10), inset 0 1px 0 rgba(255,255,255,0.7);
  transition: transform .2s ease, box-shadow .2s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  transform: translateY(-3px);
  box-shadow: 0 20px 42px rgba(15, 40, 35, 0.14), inset 0 1px 0 rgba(255,255,255,0.85);
}
[data-testid="stForm"] {
  background: rgba(255, 255, 255, 0.68) !important;
  backdrop-filter: blur(22px) saturate(170%);
  -webkit-backdrop-filter: blur(22px) saturate(170%);
  border: 1px solid rgba(255, 255, 255, 0.82) !important;
  border-radius: 18px !important;
  padding: 14px !important;
  box-shadow: 0 12px 30px rgba(15, 40, 35, 0.10), inset 0 1px 0 rgba(255,255,255,0.7);
}
[data-testid="stAlert"] {
  background: rgba(255, 255, 255, 0.48) !important;
  backdrop-filter: blur(18px) saturate(160%);
  -webkit-backdrop-filter: blur(18px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.70) !important;
  border-radius: 18px !important;
}
div[data-testid="stDataFrame"] {
  background: transparent !important;
  border-radius: 16px;
  overflow: hidden;
}
h1, h2, h3 { color: var(--ink) !important; letter-spacing: -0.02em; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: var(--ink) !important; }
#bill-content {
  position: absolute;
  inset: 0;
  z-index: 5;
  overflow-y: auto;
  padding: 72px 26px 40px;
  background: linear-gradient(180deg, rgba(250,253,251,0.92), rgba(247,251,249,0.86));
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}
.bill-head { display: flex; justify-content: space-between; align-items: center; }
#bill-content h2 { margin: 0; font-size: 30px; }
.bill-close {
  border: 0;
  background: rgba(255,255,255,0.72);
  border-radius: 999px;
  padding: 6px 12px;
  cursor: pointer;
}
.bill-name { font-size: 28px; font-weight: 700; margin: 14px 0 4px; }
.bill-sub { color: #556; font-size: 14px; margin-bottom: 14px; }
.bill-tags { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 6px; }
.bill-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 12px 0; }
.bill-card {
  background: rgba(255,255,255,0.68);
  border: 1px solid rgba(255,255,255,0.8);
  border-radius: 18px;
  padding: 12px 14px;
  margin: 10px 0;
  box-shadow: 0 12px 30px rgba(15,40,35,0.10), inset 0 1px 0 rgba(255,255,255,0.7);
  transition: transform .2s ease, box-shadow .2s ease;
}
.bill-grid .bill-card { margin: 0; }
.bill-cost {
  display: grid;
  grid-template-columns: 190px 34px minmax(0, 1fr);
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  width: 100%;
}
.pie-links { width: 34px; height: 128px; overflow: visible; }
.pie3d {
  width: 190px;
  height: 140px;
  perspective: 620px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.pie-side {
  position: absolute;
  top: 18px;
  width: 158px;
  height: 158px;
  border-radius: 50%;
  background: rgba(18, 44, 61, 0.35);
  transform: rotateX(58deg) rotateZ(-18deg);
  filter: blur(.4px);
}
.pie {
  width: 158px;
  height: 158px;
  border-radius: 50%;
  position: relative;
  z-index: 2;
  transform: rotateX(58deg) rotateZ(-18deg);
  transform-origin: center;
  box-shadow: 0 20px 24px rgba(15,40,35,0.2), inset 0 0 0 1px rgba(255,255,255,0.55);
  animation: pieIn .7s cubic-bezier(.22,1,.36,1) .08s both;
}
.pie::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: radial-gradient(circle at 34% 28%, rgba(255,255,255,0.4), rgba(255,255,255,0) 56%);
}
@keyframes pieIn {
  0% { opacity: 0; transform: rotateX(58deg) rotateZ(-18deg) scale(.35); }
  65% { opacity: 1; transform: rotateX(58deg) rotateZ(-18deg) scale(1.06); }
  100% { opacity: 1; transform: rotateX(58deg) rotateZ(-18deg) scale(1); }
}
.bill-legend {
  font-size: 14px;
  line-height: 1.9;
  white-space: nowrap;
  min-width: 0;
  animation: legendIn .55s ease .18s both;
}
@keyframes legendIn {
  from { opacity: 0; transform: translateX(-8px); }
  to { opacity: 1; transform: none; }
}
.bill-legend i {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 3px;
  margin-right: 6px;
}
.bill-legend b { color: #1f4e79; margin-left: 4px; }
.bill-total {
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px dashed rgba(31,78,121,0.14);
  font-size: 13px;
}
.bill-total b { font-size: 17px; }
.bill-fb-item {
  font-size: 13px;
  line-height: 1.7;
  padding: 6px 0;
  border-bottom: 1px dashed rgba(31,78,121,0.12);
}
.bill-fb-item:last-child { border-bottom: 0; }
.bill-more-btn {
  margin-top: 6px;
  border: 0;
  background: rgba(31,78,121,0.08);
  color: #1f4e79;
  border-radius: 999px;
  padding: 5px 12px;
  font-size: 12px;
  cursor: pointer;
}
.bill-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 22px 46px rgba(15,40,35,0.16), inset 0 1px 0 rgba(255,255,255,0.85);
}
.bill-card span { font-size: 12px; color: #667; }
.bill-card b { display: block; font-size: 24px; margin-top: 4px; }
.bill-row { font-size: 14px; line-height: 1.9; }
.bill-tag {
  display: inline-block;
  border-radius: 999px;
  padding: 5px 11px;
  font-size: 13px;
  font-weight: 600;
}
.bill-tag.grid { background: rgba(31,78,121,0.12); color: #1f4e79; }
.bill-tag.evidence { background: rgba(35,145,95,0.14); color: #1a6b3c; }
.cmp-chart {
  position: relative;
  height: 210px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 42px;
  padding: 30px 12px 0;
  border-bottom: 1px solid rgba(31,78,121,0.10);
}
.cmp-chart::before {
  content: "";
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: 58px;
  height: 1px;
  background: rgba(31,78,121,0.06);
}
.cmp-col {
  width: 92px;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
}
.cmp-value { font-size: 14px; font-weight: 700; color: #1f4e79; margin-bottom: 8px; }
.cmp-track {
  width: 48px;
  height: 128px;
  display: flex;
  align-items: flex-end;
  background: rgba(31,78,121,0.06);
  border-radius: 12px;
  overflow: hidden;
}
.cmp-bar {
  width: 100%;
  border-radius: 12px 12px 0 0;
  transform: scaleY(0);
  transform-origin: bottom center;
  animation: cmpRise .95s cubic-bezier(.22,1,.36,1) forwards;
  box-shadow: 0 6px 16px rgba(15,40,35,0.12);
}
.cmp-bar.base { background: linear-gradient(180deg, #a9bdcc, #7f9cb2); }
.cmp-bar.better { background: linear-gradient(180deg, #5aa0e0, #2f6fb0); }
.cmp-label { font-size: 12px; color: #667; margin-top: 10px; }
.cmp-delta {
  position: absolute;
  top: 0;
  right: 6px;
  font-size: 12px;
  font-weight: 700;
  color: #23915f;
  background: rgba(35,145,95,0.10);
  border-radius: 999px;
  padding: 4px 10px;
}
@keyframes cmpRise { to { transform: scaleY(1); } }
@media (max-width: 900px) {
  .cmp-chart { gap: 24px; height: 190px; }
}
.rank-chart { padding: 4px 2px 2px; }
.rank-row {
  display: grid;
  grid-template-columns: 22px 132px minmax(0, 1fr) 56px;
  align-items: center;
  gap: 10px;
  padding: 7px 0;
  animation: rankIn .5s cubic-bezier(.22,1,.36,1) both;
}
.rank-no {
  width: 20px;
  height: 20px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #5b6b66;
  background: rgba(31,78,121,0.08);
}
.rank-row:nth-child(1) .rank-no { background: #1f4e79; color: #fff; }
.rank-row:nth-child(2) .rank-no { background: #3d6f9c; color: #fff; }
.rank-row:nth-child(3) .rank-no { background: #6b93b5; color: #fff; }
.rank-name {
  font-size: 12px;
  color: #34443f;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rank-track {
  height: 14px;
  border-radius: 999px;
  background: rgba(31,78,121,0.08);
  overflow: hidden;
}
.rank-bar {
  height: 100%;
  border-radius: 999px;
  transform: scaleX(0);
  transform-origin: left center;
  animation: rankGrow .85s cubic-bezier(.22,1,.36,1) forwards;
  box-shadow: 0 2px 8px rgba(15,40,35,0.12);
}
.rank-val {
  text-align: right;
  font-size: 12px;
  font-weight: 700;
  color: #1f4e79;
}
@keyframes rankGrow { to { transform: scaleX(1); } }
@keyframes rankIn {
  from { opacity: 0; transform: translateX(-8px); }
  to { opacity: 1; transform: none; }
}
@media (max-width: 900px) {
  .rank-row { grid-template-columns: 20px 100px minmax(0, 1fr) 50px; gap: 7px; }
}
body.hide-left section[data-testid="stSidebar"] {
  transform: translateX(-105%) !important;
  pointer-events: none !important;
}
body.hide-right [data-testid="stMainBlockContainer"] {
  width: 0 !important;
  min-width: 0 !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
  overflow: hidden !important;
}
body.hide-right [data-testid="stMainBlockContainer"]::before {
  opacity: 0 !important;
  visibility: hidden !important;
}
.bill-metric {
  background: rgba(255, 255, 255, 0.68);
  border: 1px solid rgba(255, 255, 255, 0.82);
  border-radius: 18px;
  padding: 14px 16px;
  box-shadow: 0 12px 30px rgba(15, 40, 35, 0.10), inset 0 1px 0 rgba(255,255,255,0.7);
  transition: transform .2s ease, box-shadow .2s ease;
}
.bill-metric:hover {
  transform: translateY(-4px);
  box-shadow: 0 22px 46px rgba(15, 40, 35, 0.16), inset 0 1px 0 rgba(255,255,255,0.85);
}
.bill-metric span { font-size: 14px; color: #58665f; }
.bill-metric b {
  display: block;
  font-size: 2rem;
  font-weight: 600;
  color: #122a26;
  margin: 4px 0;
}
.bill-metric small { font-size: 11px; line-height: 1.35; color: #7e8b85; }
.bill-echarts { width: 100%; height: 330px; }
[data-testid="stElementContainer"]:has(canvas) {
  transform-origin: center;
  animation: chartIn 1.5s cubic-bezier(.22,1,.36,1) both;
}
@keyframes chartIn {
  0% { opacity: 0; transform: scale(.72) rotate(-4deg); }
  65% { opacity: 1; transform: scale(1.03) rotate(1deg); }
  100% { opacity: 1; transform: scale(1) rotate(0); }
}
.bill-preset {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 10px;
}
.bill-preset div {
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(255,255,255,0.7);
  border-radius: 14px;
  padding: 8px 10px;
}
.bill-preset small { display: block; font-size: 11px; color: #7e8b85; }
.bill-preset b { font-size: 15px; color: #1f4e79; }
.cost-pie-wrap {
  max-width: 560px;
  width: 100%;
  margin: 0 auto;
}
.cost-pie-svg {
  width: 100%;
  height: auto;
  aspect-ratio: 560 / 340;
  display: block;
}
.cost-pie-img {
  width: 100%;
  height: auto;
  display: block;
  transform-origin: center;
  animation: piePop .72s cubic-bezier(.22,1,.36,1) both;
}
.cost-pie-svg {
  transform-origin: center;
  animation: piePop .72s cubic-bezier(.22,1,.36,1) both;
}
@keyframes piePop {
  0% { opacity: 0; transform: scale(.55) rotate(-7deg); }
  68% { opacity: 1; transform: scale(1.045) rotate(1.5deg); }
  100% { opacity: 1; transform: scale(1) rotate(0); }
}
.cost-pie-total {
  text-align: center;
  font-size: 13px;
  color: #667;
  margin-top: 2px;
}
.cost-pie-total b { font-size: 20px; color: #1f4e79; }
.sb-controls {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 18px;
  margin-top: 10px;
}
.sb-controls label { font-size: 12px; color: #58665f; }
.sb-controls label b { float: right; color: #1f4e79; }
.sb-controls input[type="range"] {
  width: 100%;
  margin-top: 6px;
  accent-color: #1f4e79;
}
.sb-controls .sb-switch {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #34443f;
}
.fb-inline-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin: 10px 0;
}
.fb-inline-form label { font-size: 12px; color: #58665f; }
.fb-inline-form select,
.fb-inline-form textarea {
  width: 100%;
  margin-top: 4px;
  border: 1px solid rgba(31,78,121,0.14);
  border-radius: 10px;
  padding: 7px 8px;
  font-family: inherit;
  font-size: 12px;
  background: rgba(255,255,255,0.72);
}
.fb-inline-form textarea { grid-column: 1 / -1; height: 66px; resize: vertical; }
.fb-inline-form button {
  grid-column: 1 / -1;
  border: 0;
  border-radius: 999px;
  padding: 8px;
  background: #1f4e79;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.bill-fb-text { font-size: 13px; color: #34443f; line-height: 1.65; }
.bill-fb-time { font-size: 11px; color: #8a9892; margin-top: 2px; }
#panel-controls {
  position: fixed;
  top: 64px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 99999;
  display: flex;
  gap: 8px;
}
#panel-controls button {
  border: 1px solid rgba(255,255,255,0.8);
  background: rgba(255,255,255,0.72);
  backdrop-filter: blur(18px) saturate(170%);
  -webkit-backdrop-filter: blur(18px) saturate(170%);
  color: #12302b;
  border-radius: 999px;
  padding: 7px 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 8px 22px rgba(12,40,34,0.14);
  transition: background .2s ease, color .2s ease, transform .15s ease;
}
#panel-controls button:hover { transform: translateY(-1px); }
#panel-controls button:active { transform: scale(.96); }
#panel-controls button.active {
  background: rgba(31,78,121,0.92);
  color: #fff;
  border-color: rgba(31,78,121,0.92);
}
body.panels-collapsed section[data-testid="stSidebar"] {
  transform: translateX(-105%) !important;
  pointer-events: none !important;
}
body.panels-collapsed.show-left section[data-testid="stSidebar"] {
  transform: none !important;
  pointer-events: auto !important;
}
body.panels-collapsed [data-testid="stMainBlockContainer"] {
  width: 0 !important;
  min-width: 0 !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
  overflow: hidden !important;
}
body.panels-collapsed [data-testid="stMainBlockContainer"]::before {
  opacity: 0 !important;
  visibility: hidden !important;
}
body.panels-collapsed.show-right [data-testid="stMainBlockContainer"] {
  width: min(720px, calc(100vw - 340px)) !important;
  padding: 20px 22px 64px !important;
  overflow-y: auto !important;
}
body.panels-collapsed.show-right [data-testid="stMainBlockContainer"]::before {
  opacity: 1 !important;
  visibility: visible !important;
}
@media (max-width: 900px) {
  [data-testid="stMainBlockContainer"] {
    top: 12px;
    right: 12px;
    bottom: 12px;
    left: 12px;
    width: auto;
    padding: 16px 16px 48px;
    border-radius: 24px;
  }
  [data-testid="stMainBlockContainer"]::before {
    top: 12px;
    right: 12px;
    bottom: 12px;
    left: 12px;
    width: auto;
    border-radius: 24px;
  }
  .st-key-map_bg iframe, .st-key-map_bg canvas {
    width: 100vw !important;
    min-width: 0 !important;
  }
  body.panels-collapsed.show-right [data-testid="stMainBlockContainer"] {
    width: auto !important;
    padding: 16px 16px 48px !important;
  }
}
</style>
"""
REQUIRED = {
    "station_id",
    "station_name",
    "district",
    "grid_company",
    "operator",
    "lng",
    "lat",
    "piles",
    "price_elec",
    "price_service",
    "price_parking",
    "platform_price",
    "field_price",
    "occupancy",
    "queue",
    "fake_idle",
    "feedback_count",
    "evidence",
}


@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    return prepare_data(pd.read_csv(path))


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """统一计算派生指标，上传自己的 CSV 也会走这里。"""
    out = df.copy()
    out["price_deviation"] = (
        (out["field_price"] - out["platform_price"]) / out["platform_price"] * 100
    ).round(1)
    # 按“充 60 度 + 停车 1 小时”估算一次全成本，便于横向比较
    out["full_cost_60"] = (out["field_price"] * 60 + out["price_parking"]).round(1)
    out["effective_supply"] = (out["piles"] * (1 - out["fake_idle"])).round(1)
    return out


def _out_of_china(lng: float, lat: float) -> bool:
    return not (72.004 <= lng <= 137.8347 and 0.8293 <= lat <= 55.8271)


def _transform_lat(x: float, y: float) -> float:
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
    return ret


def _transform_lng(x: float, y: float) -> float:
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
    return ret


def wgs84_to_gcj02(lng: float, lat: float) -> tuple[float, float]:
    """高德/腾讯底图使用 GCJ-02；站点坐标是 WGS84，先转换再画。"""
    if _out_of_china(lng, lat):
        return lng, lat
    a = 6378245.0
    ee = 0.00669342162296594323
    dlat = _transform_lat(lng - 105.0, lat - 35.0)
    dlng = _transform_lng(lng - 105.0, lat - 35.0)
    rad_lat = lat / 180.0 * math.pi
    magic = math.sin(rad_lat)
    magic = 1 - ee * magic * magic
    sqrt_magic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrt_magic) * math.pi)
    dlng = (dlng * 180.0) / (a / sqrt_magic * math.cos(rad_lat) * math.pi)
    return lng + dlng, lat + dlat


def price_color(value: float) -> list[int]:
    if value >= 20:
        return [200, 45, 60, 210]
    if value >= 10:
        return [240, 165, 40, 210]
    return [35, 145, 95, 210]


def comparison_chart(
    current: float,
    proposed: float,
    current_text: str,
    proposed_text: str,
    delta_text: str,
    proposed_color: str = "#2f6fb0",
) -> str:
    max_value = max(abs(current), abs(proposed), 1e-9)
    h1 = max(8.0, abs(current) / max_value * 100)
    h2 = max(8.0, abs(proposed) / max_value * 100)
    return f"""
<div class="cmp-chart">
  <div class="cmp-delta">{delta_text}</div>
  <div class="cmp-col">
    <div class="cmp-value">{current_text}</div>
    <div class="cmp-track"><div class="cmp-bar base" style="height:{h1:.1f}%;animation-delay:.05s"></div></div>
    <div class="cmp-label">现状</div>
  </div>
  <div class="cmp-col">
    <div class="cmp-value">{proposed_text}</div>
    <div class="cmp-track"><div class="cmp-bar better" style="height:{h2:.1f}%;background:linear-gradient(180deg,{proposed_color}bb,{proposed_color});animation-delay:.15s"></div></div>
    <div class="cmp-label">方案</div>
  </div>
</div>
"""


def echarts_pie_option(elec: float, service: float, parking: float) -> dict:
    data = [
        {"value": round(elec), "name": "电费"},
        {"value": round(service), "name": "服务费"},
        {"value": round(parking), "name": "停车费"},
    ]
    return {
        "animation": True,
        "animationDuration": 1600,
        "animationEasing": "cubicOut",
        "animationType": "expansion",
        "title": {
            "text": "花费明细",
            "subtext": "按充 60 度、停车 1 小时估算",
            "left": "center",
        },
        "tooltip": {"trigger": "item"},
        "legend": {"orient": "vertical", "left": "left"},
        "series": [
            {
                "name": "费用构成",
                "type": "pie",
                "radius": "50%",
                "data": data,
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",
                    }
                },
            }
        ],
    }


def echarts_pie_html(elec: float, service: float, parking: float) -> str:
    option = json.dumps(echarts_pie_option(elec, service, parking), ensure_ascii=False)
    return (
        '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"/>'
        '<style>html,body{height:100%;margin:0;background:transparent;}'
        '#pie{width:100%;height:330px;}</style>'
        '<script src="https://cdn.jsdelivr.net/npm/echarts@5.6.0/dist/echarts.min.js"></script>'
        '</head><body><div id="pie"></div><script>'
        'var chart=echarts.init(document.getElementById("pie"),null,{renderer:"canvas"});'
        'chart.setOption(' + option + ');'
        'window.addEventListener("resize",function(){chart.resize();});'
        '</script></body></html>'
    )


def make_map(data: pd.DataFrame) -> str:
    coords = [wgs84_to_gcj02(float(lng), float(lat)) for lng, lat in zip(data["lng"], data["lat"])]
    stations = []
    for i, row in data.reset_index(drop=True).iterrows():
        lng, lat = coords[i]
        stations.append(
            {
                "name": row["station_name"],
                "district": row["district"],
                "grid": row["grid_company"],
                "operator": row["operator"],
                "lat": lat,
                "lng": lng,
                "piles": int(row["piles"]),
                "queue": float(row["queue"]),
                "fake_idle": float(row["fake_idle"]),
                "occupancy": float(row["occupancy"]),
                "deviation": float(row["price_deviation"]),
                "platform": float(row["platform_price"]),
                "field": float(row["field_price"]),
                "full_cost": float(row["full_cost_60"]),
                "evidence": row["evidence"],
                "feedback": int(row["feedback_count"]),
                "elec": float(row["price_elec"]),
                "service": float(row["price_service"]),
                "parking": float(row["price_parking"]),
                "feedback_items": [
                    {
                        "text": f"价格不符：平台 ¥{row['platform_price']:.2f}，现场 ¥{row['field_price']:.2f}",
                        "time": "2026-11-18 09:42",
                    },
                    {
                        "text": f"占位：晚高峰排队约 {int(row['queue'])} 分钟",
                        "time": "2026-11-17 18:20",
                    },
                    {
                        "text": "坏桩：现场部分充电枪无法启动",
                        "time": "2026-11-16 12:05",
                    },
                    {
                        "text": "环境/服务：现场无人值守",
                        "time": "2026-11-15 20:31",
                    },
                ],
            }
        )
    center_lat = sum(s["lat"] for s in stations) / len(stations)
    center_lng = sum(s["lng"] for s in stations) / len(stations)
    payload = json.dumps(stations, ensure_ascii=False)

    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<style>
  html, body, #map {{ height: 100%; margin: 0; background: #e7efe9; }}
  #map {{ position: relative; }}
  .leaflet-container {{ background: #e7efe9; font-family: "Microsoft YaHei", sans-serif; }}
  .leaflet-tile-pane {{ opacity: 0.78; filter: grayscale(0.25) saturate(0.60) brightness(1.05) contrast(0.94); }}
  .map-veil {{ position: absolute; inset: 0; z-index: 350; pointer-events: none; background: rgba(248, 251, 248, 0.18); }}
  .leaflet-control-attribution {{ display: none; }}
  .leaflet-popup-content {{ font-family: "Microsoft YaHei", sans-serif; font-size: 13px; line-height: 1.6; }}
  .leaflet-popup-content b {{ color: #12302b; }}
</style>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css"/>
</head>
<body>
<div id="map"></div>
<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const stations = {payload};
const map = L.map('map', {{ zoomControl: true, attributionControl: false }}).setView([{center_lat}, {center_lng}], 11);
L.tileLayer(
  'https://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={{x}}&y={{y}}&z={{z}}',
  {{ minZoom: 3, maxZoom: 18 }}
).addTo(map);
L.DomUtil.create('div', 'map-veil', map.getContainer());

function ensurePanelControls() {{
  try {{
    const p = window.parent;
    const doc = p.document;
    p.__dshTogglePanel = function(side) {{
      const body = doc.body;
      body.classList.remove('panels-collapsed', 'show-left', 'show-right');
      if (side === 'left') {{
        body.classList.toggle('hide-left');
      }} else {{
        body.classList.toggle('hide-right');
      }}
      doc.querySelectorAll('#panel-controls button').forEach((b) => {{
        const hidden = body.classList.contains(
          b.dataset.side === 'left' ? 'hide-left' : 'hide-right'
        );
        b.classList.toggle('active', !hidden);
      }});
    }};
    let wrap = doc.getElementById('panel-controls');
    if (!wrap) {{
      wrap = doc.createElement('div');
      wrap.id = 'panel-controls';
      wrap.innerHTML = '<button type="button" data-side="left">左栏</button><button type="button" data-side="right">右栏</button>';
      doc.body.appendChild(wrap);
    }}
    doc.body.classList.remove('panels-collapsed', 'show-left', 'show-right');
    wrap.querySelectorAll('button').forEach((btn) => {{
      btn.setAttribute('onclick', "window.__dshTogglePanel('" + btn.dataset.side + "')");
      const hidden = doc.body.classList.contains(
        btn.dataset.side === 'left' ? 'hide-left' : 'hide-right'
      );
      btn.classList.toggle('active', !hidden);
    }});
  }} catch (e) {{}}
}}
function collapsePanels() {{
  try {{
    const doc = window.parent.document;
    doc.body.classList.remove('panels-collapsed', 'show-left', 'show-right');
    doc.body.classList.add('hide-left', 'hide-right');
    doc.querySelectorAll('#panel-controls button').forEach(b => b.classList.remove('active'));
  }} catch (e) {{}}
}}
ensurePanelControls();

function ensureStationBridge() {{
  try {{
    const p = window.parent;
    if (!p || p.__dshStationBridge) return;
    p.__dshStationBridge = true;
    p.addEventListener('message', (e) => {{
      if (!e.data || e.data.type !== 'dsh-station') return;
      if (!p.location.pathname.includes('page_station_bill')) return;
      const url = p.location.pathname + '?station=' + encodeURIComponent(e.data.name);
      p.location.href = url;
    }});
  }} catch (e) {{}}
}}
ensureStationBridge();

function closeBillContent(doc) {{
  doc.querySelectorAll('#bill-content').forEach((c) => {{
    (c.__dshHidden || []).forEach((ch) => {{
      ch.style.display = ch.__dshOldDisplay || '';
      ch.__dshHiddenFlag = false;
    }});
    c.remove();
  }});
}}

function renderInlinePie(s) {{
  const p = window.parent;
  const doc = p.document;
  const el = doc.getElementById('bill-echarts-pie');
  if (!el) return;
  const option = {{
    animation: true,
    animationDuration: 1600,
    animationEasing: 'cubicOut',
    animationType: 'expansion',
    title: {{
      text: '花费明细',
      subtext: '按充 60 度、停车 1 小时估算',
      left: 'center',
    }},
    tooltip: {{ trigger: 'item' }},
    legend: {{ orient: 'vertical', left: 'left' }},
    series: [{{
      name: '费用构成',
      type: 'pie',
      radius: '50%',
      data: [
        {{ value: Math.round(s.elec * 60), name: '电费' }},
        {{ value: Math.round(s.service * 60), name: '服务费' }},
        {{ value: Math.round(s.parking), name: '停车费' }},
      ],
      emphasis: {{
        itemStyle: {{
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)',
        }},
      }},
    }}],
  }};
  const draw = () => {{
    if (!p.echarts || !el.isConnected) return;
    if (!el.clientWidth) {{
      setTimeout(draw, 80);
      return;
    }}
    if (el.__chart) el.__chart.dispose();
    const chart = p.echarts.init(el, null, {{ renderer: 'canvas' }});
    chart.setOption(option);
    el.__chart = chart;
    setTimeout(() => {{
      if (el.__chart) el.__chart.resize();
    }}, 420);
    if (p.ResizeObserver && !el.__ro) {{
      el.__ro = new p.ResizeObserver(() => {{
        if (el.__chart) el.__chart.resize();
      }});
      el.__ro.observe(el);
    }}
  }};
  if (p.echarts) {{
    draw();
  }} else {{
    let script = doc.getElementById('echarts-cdn');
    if (!script) {{
      script = doc.createElement('script');
      script.id = 'echarts-cdn';
      script.src = 'https://cdn.jsdelivr.net/npm/echarts@5.6.0/dist/echarts.min.js';
      doc.head.appendChild(script);
    }}
    script.addEventListener('load', draw, {{ once: true }});
  }}
}}

function showBillInline(s) {{
  try {{
    const p = window.parent;
    const doc = p.document;
    const main = doc.querySelector('[data-testid="stMainBlockContainer"]');
    if (!main) return;

    doc.body.classList.remove('hide-right', 'panels-collapsed', 'show-left', 'show-right');
    const rightBtn = doc.querySelector('#panel-controls button[data-side="right"]');
    if (rightBtn) rightBtn.classList.add('active');

    closeBillContent(doc);
    let content = null;
    content = doc.createElement('div');
    content.id = 'bill-content';
    main.appendChild(content);
    content.__dshHidden = [];
    const mapEl = main.querySelector('.st-key-map_bg');
    if (mapEl) {{
      let node = mapEl;
      while (node && node !== main) {{
        const parent = node.parentElement;
        [...parent.children].forEach((ch) => {{
          if (ch === node || ch === content || ch.contains(mapEl) || ch.__dshHiddenFlag) return;
          ch.__dshOldDisplay = ch.style.display;
          ch.style.display = 'none';
          ch.__dshHiddenFlag = true;
          content.__dshHidden.push(ch);
        }});
        node = parent;
      }}
    }}
    [...main.children].forEach((ch) => {{
      if (ch === content || ch === mapEl || ch.contains(mapEl) || ch.__dshHiddenFlag) return;
      ch.__dshOldDisplay = ch.style.display;
      ch.style.display = 'none';
      ch.__dshHiddenFlag = true;
      content.__dshHidden.push(ch);
    }});
    content.addEventListener('click', (e) => {{
      if (e.target.closest('[data-close]')) {{
        closeBillContent(doc);
      }} else if (e.target.closest('[data-more]')) {{
        const more = content.querySelector('.bill-more');
        if (more) {{
          more.hidden = !more.hidden;
          e.target.textContent = more.hidden ? '显示更多' : '收起';
        }}
      }}
    }});
    content.dataset.page = p.location.pathname;

    if (!p.__dshBillWatch) {{
      p.__dshBillWatch = setInterval(() => {{
        const layers = p.document.querySelectorAll('#bill-content');
        for (const layer of layers) {{
          if (layer.dataset.page && layer.dataset.page !== p.location.pathname) {{
            closeBillContent(p.document);
            break;
          }}
        }}
      }}, 300);
    }}
    if (!p.__dshHistoryHooked) {{
      p.__dshHistoryHooked = true;
      const originalPush = p.history.pushState;
      p.history.pushState = function (...args) {{
        const before = p.location.pathname;
        const result = originalPush.apply(this, args);
        if (p.location.pathname !== before) {{
          closeBillContent(p.document);
        }}
        return result;
      }};
      p.addEventListener('popstate', () => closeBillContent(p.document));
    }}

    const card = (label, value) =>
      '<div class="bill-card"><span>' + label + '</span><b>' + value + '</b></div>';
    const elec = s.elec * 60;
    const service = s.service * 60;
    const parking = s.parking;
    const total = Math.max(1, elec + service + parking);
    const p1 = (elec / total) * 100;
    const p2 = ((elec + service) / total) * 100;
    const p3 = 100 - p2;
    const pieBg = 'conic-gradient(#2f6fb0 0 ' + p1.toFixed(1) + '%, #48a37b ' +
      p1.toFixed(1) + '% ' + p2.toFixed(1) + '%, #e0a33a ' + p2.toFixed(1) + '% 100%)';
    const feedback = (s.feedback_items || []).map((f) =>
      typeof f === 'string' ? {{ text: f, time: '' }} : f
    );
    const fbItem = (f) =>
      '<div class="bill-fb-item"><div class="bill-fb-text">' + f.text + '</div>' +
      '<div class="bill-fb-time">' + (f.time || '') + '</div></div>';
    const firstFb = feedback.slice(0, 2).map(fbItem).join('');
    const restFb = feedback.slice(2).map(fbItem).join('');
    const moreBtn = restFb ? '<button class="bill-more-btn" data-more>显示更多</button>' : '';

    content.innerHTML =
      '<div class="bill-head"><h2>站点账单</h2><button class="bill-close" data-close>关闭</button></div>' +
      '<div class="bill-name">' + s.name + '</div>' +
      '<div class="bill-sub">' + s.district + ' · ' + s.operator + ' · ' + s.piles + ' 桩</div>' +
      '<div class="bill-tags">' +
        '<span class="bill-tag grid">电网：' + s.grid + '</span>' +
        '<span class="bill-tag evidence">证据等级：' + s.evidence + '</span>' +
      '</div>' +
      '<div class="bill-grid">' +
        card('平台价', '¥' + s.platform.toFixed(2) + '/度') +
        card('实地实付', '¥' + s.field.toFixed(2) + '/度') +
        card('价格偏差', (s.deviation > 0 ? '+' : '') + s.deviation.toFixed(1) + '%') +
        card('全成本', '¥' + s.full_cost.toFixed(0)) +
      '</div>' +
      '<div class="bill-card"><div id="bill-echarts-pie" class="bill-echarts"></div></div>' +
      '<div class="bill-card"><span>用户反馈</span>' +
        '<div class="bill-fb">' + firstFb + '<div class="bill-more" hidden>' + restFb + '</div></div>' +
        moreBtn +
      '</div>';
    renderInlinePie(s);
  }} catch (e) {{}}
}}

function showSandboxInline(s) {{
  showBillInline(s);
  const doc = window.parent.document;
  const c = doc.getElementById('bill-content');
  if (!c) return;
  const baseWait = s.queue;
  const baseFake = s.fake_idle;
  const piles = s.piles;

  c.innerHTML =
    '<div class="bill-head"><h2>治理沙盘</h2><button class="bill-close" data-close>关闭</button></div>' +
    '<div class="bill-name">' + s.name + '</div>' +
    '<div class="bill-sub">' + s.district + ' · ' + s.operator + ' · ' + s.piles + ' 桩</div>' +
    '<div class="bill-grid">' +
      '<div class="bill-metric"><span>平均等待（现状）</span><b id="sb-wait-base">' + baseWait.toFixed(1) + ' 分钟</b></div>' +
      '<div class="bill-metric"><span>平均等待（方案）</span><b id="sb-wait-new">—</b></div>' +
      '<div class="bill-metric"><span>空闲误判率</span><b id="sb-fake-new">—</b></div>' +
      '<div class="bill-metric"><span>有效桩数</span><b id="sb-eff">—</b></div>' +
    '</div>' +
    '<div class="bill-card"><span>方案控制台</span><div class="sb-controls">' +
      '<label>免费宽限 <b id="sb-grace-v">30 分钟</b><input id="sb-grace" type="range" min="0" max="60" step="5" value="30"></label>' +
      '<label>超时占用费 <b id="sb-fee-v">0.3 元/分钟</b><input id="sb-fee" type="range" min="0.1" max="2" step="0.1" value="0.3"></label>' +
      '<label>单次封顶 <b id="sb-cap-v">50 元</b><input id="sb-cap" type="range" min="10" max="100" step="10" value="50"></label>' +
      '<label class="sb-switch"><input id="sb-res" type="checkbox" checked> 启用预约锁位</label>' +
    '</div></div>' +
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">' +
      '<div class="bill-card"><span>等待时间对比</span><div class="cmp-chart">' +
        '<div class="cmp-col"><div class="cmp-value" id="sb-wait-base-v">' + baseWait.toFixed(1) + ' 分钟</div>' +
          '<div class="cmp-track"><div class="cmp-bar base" id="sb-wait-base-bar" style="height:100%;animation-delay:.05s"></div></div><div class="cmp-label">现状</div></div>' +
        '<div class="cmp-col"><div class="cmp-value" id="sb-wait-plan-v">—</div>' +
          '<div class="cmp-track"><div class="cmp-bar better" id="sb-wait-plan-bar" style="height:8%;background:linear-gradient(180deg,#5aa0e0,#2f6fb0);animation-delay:.15s"></div></div><div class="cmp-label">方案</div></div>' +
      '</div></div>' +
      '<div class="bill-card"><span>空闲误判率对比</span><div class="cmp-chart">' +
        '<div class="cmp-col"><div class="cmp-value" id="sb-fake-base-v">' + (baseFake * 100).toFixed(1) + '%</div>' +
          '<div class="cmp-track"><div class="cmp-bar base" id="sb-fake-base-bar" style="height:100%;animation-delay:.05s"></div></div><div class="cmp-label">现状</div></div>' +
        '<div class="cmp-col"><div class="cmp-value" id="sb-fake-plan-v">—</div>' +
          '<div class="cmp-track"><div class="cmp-bar better" id="sb-fake-plan-bar" style="height:8%;background:linear-gradient(180deg,#48a37b,#23915f);animation-delay:.15s"></div></div><div class="cmp-label">方案</div></div>' +
      '</div></div>' +
    '</div>' +
    '<div class="bill-card"><span>方案预设</span><div class="bill-preset">' +
      '<div><small>免费宽限</small><b id="sb-p-grace">30 分钟</b></div>' +
      '<div><small>超时占用费</small><b id="sb-p-fee">0.3 元/分钟</b></div>' +
      '<div><small>单次封顶</small><b id="sb-p-cap">50 元</b></div>' +
      '<div><small>预约锁位</small><b id="sb-p-res">开启</b></div>' +
      '<div><small>估算占用费收入/日</small><b id="sb-p-rev">—</b></div>' +
    '</div></div>';

  const $ = (id) => c.querySelector('#' + id);
  const recalc = () => {{
    const grace = Number($('sb-grace').value);
    const fee = Number($('sb-fee').value);
    const cap = Number($('sb-cap').value);
    const reservation = $('sb-res').checked;
    const graceEffect = Math.max(0, 30 - grace) * 0.0008;
    const newFake = Math.max(0.02, baseFake - fee * 0.12 - (reservation ? 0.04 : 0) - graceEffect);
    const newWait = Math.max(2, baseWait * (1 - fee * 0.3) - (reservation ? 3 : 0) - Math.max(0, 30 - grace) * 0.03);
    const eff = piles * (1 - newFake);
    const events = Math.max(0, (baseFake - newFake) * piles * 8);
    const revenue = Math.min(cap, fee * 60) * events;
    const maxWait = Math.max(baseWait, newWait, 1);
    const maxFake = Math.max(baseFake, newFake, 0.01);

    $('sb-wait-new').textContent = newWait.toFixed(1) + ' 分钟';
    $('sb-fake-new').textContent = (newFake * 100).toFixed(1) + '%';
    $('sb-eff').textContent = eff.toFixed(0);
    $('sb-wait-plan-v').textContent = newWait.toFixed(1) + ' 分钟';
    $('sb-fake-plan-v').textContent = (newFake * 100).toFixed(1) + '%';
    $('sb-wait-plan-bar').style.height = Math.max(8, newWait / maxWait * 100).toFixed(1) + '%';
    $('sb-wait-base-bar').style.height = Math.max(8, baseWait / maxWait * 100).toFixed(1) + '%';
    $('sb-fake-plan-bar').style.height = Math.max(8, newFake / maxFake * 100).toFixed(1) + '%';
    $('sb-fake-base-bar').style.height = Math.max(8, baseFake / maxFake * 100).toFixed(1) + '%';
    $('sb-grace-v').textContent = grace + ' 分钟';
    $('sb-fee-v').textContent = fee.toFixed(1) + ' 元/分钟';
    $('sb-cap-v').textContent = cap + ' 元';
    $('sb-p-grace').textContent = grace + ' 分钟';
    $('sb-p-fee').textContent = fee.toFixed(1) + ' 元/分钟';
    $('sb-p-cap').textContent = cap + ' 元';
    $('sb-p-res').textContent = reservation ? '开启' : '关闭';
    $('sb-p-rev').textContent = '¥' + revenue.toFixed(0);
  }};
  c.querySelectorAll('input').forEach((el) => el.addEventListener('input', recalc));
  recalc();
}}

function showFeedbackInline(s) {{
  showBillInline(s);
  const doc = window.parent.document;
  const c = doc.getElementById('bill-content');
  if (!c) return;
  const feedbackItems = s.feedback_items || [];
  const items = feedbackItems.map((f) =>
    '<div class="bill-fb-item"><div class="bill-fb-text">' + f.text + '</div><div class="bill-fb-time">' + f.time + '</div></div>'
  ).join('');
  const mcard = (label, value) =>
    '<div class="bill-metric"><span>' + label + '</span><b>' + value + '</b></div>';
  c.innerHTML =
    '<div class="bill-head"><h2>反馈中心</h2><button class="bill-close" data-close>关闭</button></div>' +
    '<div class="bill-name">' + s.name + '</div>' +
    '<div class="bill-sub">' + s.district + ' · ' + s.operator + ' · ' + s.piles + ' 桩</div>' +
    '<div class="bill-grid">' +
      mcard('反馈总数', String(s.feedback)) +
      mcard('价格类', '1') +
      mcard('待核验', s.evidence === 'A' ? '1' : '2') +
      mcard('证据等级', s.evidence) +
    '</div>' +
    '<div class="bill-card"><span>提交一条反馈</span>' +
      '<div class="fb-inline-form">' +
        '<label>类型<select id="fb-kind-inline"><option>价格不符</option><option>占位</option><option>坏桩</option><option>排队</option><option>环境/服务</option></select></label>' +
        '<label>证据<select id="fb-evidence-inline"><option>A 实地+账单</option><option>B 现场照片</option><option>C 仅文字</option></select></label>' +
        '<textarea id="fb-content-inline" placeholder="例如：平台显示 1.20，现场扫码变成 1.65"></textarea>' +
        '<button type="button" id="fb-submit-inline">提交反馈</button>' +
      '</div>' +
    '</div>' +
    '<div class="bill-card"><span>用户反馈（' + feedbackItems.length + ' 条）</span>' +
      '<div class="bill-fb" id="fb-inline-list">' + items + '</div>' +
    '</div>';

  const submit = c.querySelector('#fb-submit-inline');
  if (submit) {{
    submit.addEventListener('click', () => {{
      const content = c.querySelector('#fb-content-inline');
      const list = c.querySelector('#fb-inline-list');
      const kind = c.querySelector('#fb-kind-inline').value;
      if (!content || !list || !content.value.trim()) return;
      const now = new Date();
      const stamp = now.getFullYear() + '-' +
        String(now.getMonth() + 1).padStart(2, '0') + '-' +
        String(now.getDate()).padStart(2, '0') + ' ' +
        String(now.getHours()).padStart(2, '0') + ':' +
        String(now.getMinutes()).padStart(2, '0');
      const item = doc.createElement('div');
      item.className = 'bill-fb-item';
      item.innerHTML = '<div class="bill-fb-text">' + kind + '：' + content.value.trim() +
        '</div><div class="bill-fb-time">' + stamp + '</div>';
      list.prepend(item);
      content.value = '';
    }});
  }}
}}

map.on('movestart zoomstart', collapsePanels);


function pinColor(v) {{
  if (v >= 20) return '#c82d3c';
  if (v >= 10) return '#f0a528';
  return '#23915f';
}}

stations.forEach(s => {{
  const marker = L.circleMarker([s.lat, s.lng], {{
    radius: 7 + Math.min(8, s.piles / 8),
    color: '#ffffff',
    weight: 1.2,
    fillColor: pinColor(s.deviation),
    fillOpacity: 0.95
  }}).addTo(map);
  marker.bindPopup(
    '<b>' + s.name + '</b><br/>' +
    s.district + ' · ' + s.operator + '<br/>' +
    '电网：' + s.grid + '<br/>' +
    '平台价：¥' + s.platform.toFixed(2) + '/度<br/>' +
    '实付价：¥' + s.field.toFixed(2) + '/度<br/>' +
    '价格偏差：' + (s.deviation > 0 ? '+' : '') + s.deviation.toFixed(1) + '%'
  );
  marker.on('popupopen', () => {{
    try {{
      const p = window.parent;
      const path = p.location.pathname;
      if (path.includes('page_sandbox')) {{
        showSandboxInline(s);
      }} else if (path.includes('page_feedback')) {{
        showFeedbackInline(s);
      }} else {{
        showBillInline(s);
      }}
      setTimeout(() => marker.closePopup(), 30);
    }} catch (e) {{}}
  }});
}});
setTimeout(() => map.invalidateSize(), 250);
</script>
</body>
</html>"""
    return doc


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.markdown("### 筛选")
        districts = st.multiselect("区域", sorted(df["district"].unique()), default=None, placeholder="全部")
        grids = st.multiselect("电网", sorted(df["grid_company"].unique()), default=None, placeholder="全部")
        operators = st.multiselect("运营商", sorted(df["operator"].unique()), default=None, placeholder="全部")
        min_dev = st.slider("最低价格偏差（%）", 0, 30, 0, 5)

    view = df.copy()
    if districts:
        view = view[view["district"].isin(districts)]
    if grids:
        view = view[view["grid_company"].isin(grids)]
    if operators:
        view = view[view["operator"].isin(operators)]
    view = view[view["price_deviation"] >= min_dev]
    return view


def page_price_map() -> None:
    df = st.session_state["df"]
    st.title("价格地图")
    st.caption("先看哪里贵、哪里平台价与实付价不一致；点开站点账单看证据。")

    view = st.session_state.get("view", df)
    if view.empty:
        st.warning("当前筛选没有站点，放宽条件再试。")
        return

    st.caption("全屏地图在背景，可拖动/缩放；左侧筛选会同时更新地图和下方清单。")

    row1 = st.columns(2)
    with row1[0]:
        st.metric("站点数", len(view), border=True)
    with row1[1]:
        st.metric("平均价格偏差", f"{view['price_deviation'].mean():.1f}%", border=True)
    row2 = st.columns(2)
    with row2[0]:
        st.metric("平均全成本", f"¥{view['full_cost_60'].mean():.0f}", border=True)
    with row2[1]:
        st.metric("平均空闲误判率", f"{view['fake_idle'].mean():.1%}", border=True)

    with st.container(border=True):
        st.subheader("差价最大的站点")
        top = view.nlargest(8, "price_deviation")[
            ["station_name", "price_deviation"]
        ].reset_index(drop=True)
        max_dev = max(float(top["price_deviation"].max()), 1.0)
        rows = []
        for idx, row in top.iterrows():
            dev = float(row["price_deviation"])
            width = max(4.0, dev / max_dev * 100)
            if dev >= 40:
                grad = "linear-gradient(90deg,#c0392b,#ef7d57)"
            elif dev >= 30:
                grad = "linear-gradient(90deg,#d97706,#f2b35e)"
            else:
                grad = "linear-gradient(90deg,#1f4e79,#5aa0e0)"
            rows.append(
                f'<div class="rank-row" style="animation-delay:{idx * 0.05:.2f}s">'
                f'<span class="rank-no">{idx + 1}</span>'
                f'<span class="rank-name" title="{row["station_name"]}">{row["station_name"]}</span>'
                f'<div class="rank-track"><div class="rank-bar" '
                f'style="width:{width:.1f}%;background:{grad};animation-delay:{0.08 + idx * 0.05:.2f}s"></div></div>'
                f'<span class="rank-val">{dev:.1f}%</span>'
                "</div>"
            )
        st.html('<div class="rank-chart">' + "".join(rows) + "</div>")

    with st.container(border=True):
        st.subheader("站点价格清单")
        show = view[
            [
                "station_name",
                "district",
                "grid_company",
                "operator",
                "platform_price",
                "field_price",
                "price_deviation",
                "full_cost_60",
                "fake_idle",
            ]
        ].sort_values("price_deviation", ascending=False)
        show = show.assign(fake_idle_pct=(show["fake_idle"] * 100).round(0)).drop(columns=["fake_idle"])
        show = show.reset_index(drop=True).rename(
            columns={
                "station_name": "站点",
                "district": "区域",
                "grid_company": "电网",
                "operator": "运营商",
                "platform_price": "平台价（元/度）",
                "field_price": "实付价（元/度）",
                "price_deviation": "价格偏差",
                "full_cost_60": "全成本（60度+停车）",
                "fake_idle_pct": "空闲误判率",
            }
        )
        st.dataframe(
            show,
            hide_index=True,
            alt="站点平台价、实付价与价格偏差清单",
            column_config={
                "平台价（元/度）": st.column_config.NumberColumn(format="%.2f"),
                "实付价（元/度）": st.column_config.NumberColumn(format="%.2f"),
                "价格偏差": st.column_config.NumberColumn(format="%.1f%%"),
                "全成本（60度+停车）": st.column_config.NumberColumn(format="¥%.0f"),
                "空闲误判率": st.column_config.NumberColumn(format="%.0f%%"),
            },
        )

    st.info(
        "结论：低价不等于低全成本；先看价格偏差大的站，再看它是否还排长队。",
        title="一句话",
    )


def page_station_bill() -> None:
    df = st.session_state["df"]
    st.title("站点账单")
    st.caption("把平台价、现场价、电费/服务费/停车费拆开；价格旁边必须有证据。")

    names = sorted(df["station_name"].unique())
    query_station = st.query_params.get("station")
    if isinstance(query_station, list):
        query_station = query_station[0] if query_station else None
    if query_station not in names:
        st.info("点击地图上的彩色圆点，查看对应充电站的账单。", title="从地图选择站点")
        return
    station = query_station
    row = df.loc[df["station_name"] == station].iloc[0]

    st.subheader(row["station_name"])
    st.caption(f"{row['district']} · {row['operator']} · 桩数 {int(row['piles'])}")
    with st.container(horizontal=True):
        st.badge(f"电网：{row['grid_company']}", color="blue")
        st.badge(f"证据等级：{row['evidence']}", color="green" if row["evidence"] == "A" else "orange")
        st.badge("核验：2026-11-18", color="gray")

    row1 = st.columns(2)
    with row1[0]:
        st.metric("平台价", f"¥{row['platform_price']:.2f}/度", border=True)
    with row1[1]:
        st.metric("实地实付", f"¥{row['field_price']:.2f}/度", border=True)
    row2 = st.columns(2)
    with row2[0]:
        st.html(
            '<div class="bill-metric"><span>价格偏差</span>'
            f'<b>{row["price_deviation"]:+.1f}%</b>'
            '<small>正数表示现场更贵，负数表示更便宜</small></div>'
        )
    with row2[1]:
        st.html(
            '<div class="bill-metric"><span>全成本</span>'
            f'<b>¥{row["full_cost_60"]:.0f}</b>'
            '<small>充 60 度电费 + 服务费 + 1 小时停车费</small></div>'
        )

    with st.container(border=True):
        components.html(
            echarts_pie_html(
                row["price_elec"] * 60,
                row["price_service"] * 60,
                row["price_parking"],
            ),
            height=360,
            scrolling=False,
        )

    with st.container(border=True):
        st.subheader("价格核对")
        check = pd.DataFrame(
            {
                "项目": ["电费（元/度）", "服务费（元/度）", "停车费（元/小时）"],
                "平台展示": [row["price_elec"], row["price_service"], row["price_parking"]],
                "现场实付": [
                    row["price_elec"] * row["field_price"] / row["platform_price"],
                    row["price_service"] * row["field_price"] / row["platform_price"],
                    row["price_parking"],
                ],
            }
        )
        st.dataframe(check, hide_index=True, alt="平台展示与现场实付价格核对")
        st.caption("示例：按总价差等比拆分电费/服务费；真实项目以账单分项为准。")

    st.info(
        f"平台标价 ¥{row['platform_price']:.2f}/度，现场实付 ¥{row['field_price']:.2f}/度，"
        f"偏差 {row['price_deviation']:+.1f}%。证据等级 {row['evidence']}，核验时间 2026-11-18。",
        title="价格结论",
    )

    with st.container(border=True):
        st.subheader(f"用户反馈（{int(row['feedback_count'])} 条）")
        feedback = pd.DataFrame(
            [
                ["价格不符", "平台显示 1.20，现场扫小程序变成 1.65", "A", "2026-11-18 09:42"],
                ["占位", "晚高峰有车充满不走，等了 20 分钟", "B", "2026-11-17 18:20"],
                ["坏桩", "3 号枪无法启动，现场没人处理", "B", "2026-11-16 12:05"],
            ],
            columns=["类型", "内容", "证据", "时间"],
        )
        st.dataframe(feedback, hide_index=True, alt="站点用户反馈")


def page_sandbox() -> None:
    df = st.session_state["df"]
    st.title("治理沙盘")
    st.caption("调免费宽限、占用费、预约，观察等待、空闲误判、有效供给的变化。")

    names = sorted(df["station_name"].unique())
    query_station = st.query_params.get("station")
    if isinstance(query_station, list):
        query_station = query_station[0] if query_station else None
    if query_station not in names:
        st.info("点击地图上的彩色圆点，查看对应充电站的治理沙盘。", title="从地图选择站点")
        return
    station = query_station
    row = df.loc[df["station_name"] == station].iloc[0]
    st.caption(f"当前站点：{station}")

    with st.sidebar:
        st.markdown("### 占位费参数")
        grace = st.slider("免费宽限（分钟）", 0, 60, 30, 5)
        fee = st.slider("超时占用费（元/分钟）", 0.1, 2.0, 0.3, 0.1)
        cap = st.slider("单次封顶（元）", 10, 100, 50, 10)
        reservation = st.toggle("启用预约锁位", value=True)

    base_wait = float(row["queue"])
    base_fake = float(row["fake_idle"])
    total_piles = float(row["piles"])

    # 仅用于框架演示的简化公式，后续替换为排队/仿真模型
    grace_effect = max(0, 30 - grace) * 0.0008
    new_fake = max(
        0.02,
        base_fake - fee * 0.12 - (0.04 if reservation else 0) - grace_effect,
    )
    new_wait = max(
        2.0,
        base_wait * (1 - fee * 0.3) - (3 if reservation else 0) - max(0, 30 - grace) * 0.03,
    )
    new_eff = total_piles * (1 - new_fake)
    events = max(0.0, (base_fake - new_fake) * total_piles * 8)
    revenue = min(cap, fee * 60) * events

    row1 = st.columns(2)
    with row1[0]:
        st.metric("平均等待（现状）", f"{base_wait:.1f} 分钟", border=True)
    with row1[1]:
        st.metric("平均等待（方案）", f"{new_wait:.1f} 分钟", f"{new_wait - base_wait:+.1f}", border=True)
    row2 = st.columns(2)
    with row2[0]:
        st.metric("空闲误判率", f"{new_fake:.1%}", f"{(new_fake - base_fake) * 100:+.1f}pp", border=True)
    with row2[1]:
        st.metric("有效桩数", f"{new_eff:.0f}", border=True)

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.subheader("等待时间对比")
            st.html(
                comparison_chart(
                    base_wait,
                    new_wait,
                    f"{base_wait:.1f} 分钟",
                    f"{new_wait:.1f} 分钟",
                    f"{new_wait - base_wait:+.1f} 分钟",
                    "#2f6fb0",
                )
            )
    with right:
        with st.container(border=True):
            st.subheader("空闲误判率对比")
            st.html(
                comparison_chart(
                    base_fake,
                    new_fake,
                    f"{base_fake:.1%}",
                    f"{new_fake:.1%}",
                    f"{(new_fake - base_fake) * 100:+.1f}pp",
                    "#23915f",
                )
            )

    with st.container(border=True):
        st.subheader("方案预设")
        st.dataframe(
            pd.DataFrame(
                {
                    "参数": ["免费宽限", "占用费", "封顶", "预约", "估算占用费收入/日"],
                    "取值": [f"{grace} 分钟", f"¥{fee:.1f}/分钟", f"¥{cap}", "开" if reservation else "关", f"¥{revenue:.0f}"],
                }
            ),
            hide_index=True,
            alt="占位治理参数与假设",
        )
        st.caption("这是框架演示公式，不是实证结论；真实项目要用到达率、服务时长、占位时长做仿真。")

    st.info(
        f"当前方案：等待从 {base_wait:.1f} 分钟降到 {new_wait:.1f} 分钟，"
        f"空闲误判率从 {base_fake:.1%} 降到 {new_fake:.1%}；需用真实数据校准费率和误伤率。",
        title="沙盘结论",
    )


def page_feedback() -> None:
    df = st.session_state["df"]
    st.title("反馈中心")
    st.caption("用户上报价格不符、占位、坏桩、排队；带证据、可审核，才能修正数据。")

    names = sorted(df["station_name"].unique())
    query_station = st.query_params.get("station")
    if isinstance(query_station, list):
        query_station = query_station[0] if query_station else None
    if query_station not in names:
        st.info("点击地图上的彩色圆点，查看对应充电站的反馈。", title="从地图选择站点")
        return
    station = query_station
    row = df.loc[df["station_name"] == station].iloc[0]
    st.caption(f"当前站点：{station}")

    if "feedback_by_station" not in st.session_state:
        st.session_state.feedback_by_station = {}
    rows = st.session_state.feedback_by_station.setdefault(
        station,
        [
            ["价格不符", f"平台 ¥{row['platform_price']:.2f}，现场 ¥{row['field_price']:.2f}", "A", "2026-11-18 09:42"],
            ["占位", f"晚高峰排队约 {int(row['queue'])} 分钟", "B", "2026-11-17 18:20"],
            ["坏桩", "现场部分充电枪无法启动", "B", "2026-11-16 12:05"],
        ],
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("反馈总数", len(rows), border=True)
    with c2:
        st.metric("价格类", sum(1 for r in rows if r[0] == "价格不符"), border=True)
    with c3:
        st.metric("待核验", sum(1 for r in rows if r[2] != "A"), border=True)

    with st.form("feedback_form", border=True):
        st.subheader("提交一条反馈")
        c1, c2 = st.columns(2)
        kind = c1.selectbox("类型", ["价格不符", "占位", "坏桩", "排队", "环境/服务"], key="fb_kind")
        evidence = c2.selectbox("证据", ["A 实地+账单", "B 现场照片", "C 仅文字"], key="fb_evidence")
        content = st.text_area(
            "具体问题",
            placeholder="例如：平台显示 1.20，现场扫码变成 1.65，服务费多 0.4",
            key="fb_content",
        )
        submitted = st.form_submit_button("提交反馈", width="stretch", key="fb_submit")

    if submitted:
        if not content.strip():
            st.error("写点具体问题，别只提交空内容。")
        else:
            rows.append([kind, content.strip(), evidence[0], "2026-11-20 14:30"])
            st.success("已加入当前站点的反馈；接后端后可持久化并进入审核。")

    with st.container(border=True):
        st.subheader(f"用户反馈（{len(rows)} 条）")
        st.dataframe(
            pd.DataFrame(rows, columns=["类型", "内容", "证据", "时间"]),
            hide_index=True,
            alt="用户反馈列表",
        )
        st.caption("演示：反馈只存在当前浏览器会话；刷新页面会回到示例数据。")


def main() -> None:
    st.html(GLASS_CSS)

    st.sidebar.markdown("### 数据")
    uploaded = st.sidebar.file_uploader(
        "上传站点 CSV",
        type=["csv"],
        help="不传就用 20 个长沙示例站点；字段见 README。",
    )
    if uploaded is not None:
        try:
            candidate = pd.read_csv(uploaded)
        except Exception as exc:
            st.sidebar.error(f"读取失败：{exc}")
            candidate = load_data(DATA_PATH)
        missing = REQUIRED - set(candidate.columns)
        if missing:
            st.sidebar.error(f"缺少字段：{', '.join(sorted(missing))}")
            candidate = load_data(DATA_PATH)
        else:
            candidate = prepare_data(candidate)
    else:
        candidate = load_data(DATA_PATH)

    st.session_state["df"] = candidate
    view = sidebar_filters(candidate)
    st.session_state["view"] = view

    map_data = view if not view.empty else candidate
    with st.container(key="map_bg"):
        components.html(make_map(map_data), height=1000, scrolling=False)

    st.sidebar.caption(
        f"当前：{len(candidate)} 个站点 · 示例数据"
        if uploaded is None
        else f"当前：{len(candidate)} 个站点 · 已上传"
    )
    st.sidebar.markdown("---")

    pages = [
        st.Page(page_price_map, title="价格地图", icon=":material/map:", default=True),
        st.Page(page_station_bill, title="站点账单", icon=":material/receipt_long:"),
        st.Page(page_sandbox, title="治理沙盘", icon=":material/tune:"),
        st.Page(page_feedback, title="反馈中心", icon=":material/forum:"),
    ]
    nav = st.navigation(pages, position="sidebar")
    nav.run()


if __name__ == "__main__":
    main()
