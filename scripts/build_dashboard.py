"""產生互動式儀表板 docs/index.html（資料：outputs/tableau_monthly.csv）"""
from pathlib import Path
import pandas as pd, numpy as np
import plotly.graph_objects as go
from scipy import stats
import plotly.io as pio

ROOT = Path(__file__).resolve().parents[1]
d = pd.read_csv(ROOT / "outputs/tableau_monthly.csv", parse_dates=["month"])
a = d.dropna(subset=["taiex_ret"]).copy()
start, end, n = a.month.min().strftime("%Y-%m"), a.month.max().strftime("%Y-%m"), len(a)

reg = a.groupby("regime").taiex_ret.agg(["mean", "count"]).reindex(["升息", "不動", "降息"])
c = a.dropna(subset=["d_ffr"])
r_ffr, p_ffr = stats.pearsonr(c.d_ffr, c.taiex_ret)
f = a.dropna(subset=["fx_chg"])
lr = stats.linregress(f.fx_chg, f.taiex_ret)
R2 = lr.rvalue ** 2
FONT = "'Noto Sans TC','PingFang TC','Microsoft JhengHei',sans-serif"
COL = {"升息": "#d64545", "不動": "#8a94a6", "降息": "#2f9e6e"}
base = dict(template="plotly_white", font=dict(family=FONT, size=13),
            margin=dict(l=50, r=20, t=50, b=40), height=420,
            legend=dict(orientation="h", y=-0.15))

# 1. 時間序列
f1 = go.Figure()
for rg, col in [("升息", "rgba(214,69,69,.13)"), ("降息", "rgba(47,158,110,.13)")]:
    for m in d.loc[d.regime == rg, "month"]:
        f1.add_vrect(x0=m, x1=m + pd.offsets.MonthBegin(1), fillcolor=col, line_width=0, layer="below")
f1.add_trace(go.Scatter(x=d.month, y=d.taiex_close, name="加權指數", line=dict(color="#1f4e8c")))
f1.add_trace(go.Scatter(x=d.month, y=d.ffr, name="聯邦基金利率 (%)", yaxis="y2", line=dict(color="#e08a1e")))
f1.add_trace(go.Bar(x=[None], y=[None], name="升息月", marker_color="rgba(214,69,69,.4)"))
f1.add_trace(go.Bar(x=[None], y=[None], name="降息月", marker_color="rgba(47,158,110,.4)"))
f1.update_layout(**base, title="聯邦基金利率 vs 台股加權指數（紅底＝升息月、綠底＝降息月）",
                 yaxis=dict(title="加權指數", type="log"),
                 yaxis2=dict(title="利率 (%)", overlaying="y", side="right", showgrid=False))

# 2. 長條圖
f2 = go.Figure(go.Bar(x=reg.index, y=reg["mean"], marker_color=[COL[k] for k in reg.index],
                      text=[f"{v:+.2f}%<br>({int(c_)} 個月)" for v, c_ in zip(reg["mean"], reg["count"])],
                      textposition="outside"))
f2.update_layout(**base, title="不同利率狀態下，台股平均月報酬", yaxis_title="平均月報酬 (%)")
f2.update_yaxes(range=[min(0, reg["mean"].min()) * 1.6 - .3, reg["mean"].max() * 1.4])

# 3. 散佈圖
xs = np.linspace(f.fx_chg.min(), f.fx_chg.max(), 50)
f3 = go.Figure()
f3.add_trace(go.Scatter(x=f.fx_chg, y=f.taiex_ret, mode="markers", name="每月資料",
                        marker=dict(color="#1f4e8c", opacity=.5, size=7),
                        text=f.month.dt.strftime("%Y-%m"),
                        hovertemplate="%{text}<br>台幣變動 %{x:.2f}%<br>台股報酬 %{y:.2f}%<extra></extra>"))
f3.add_trace(go.Scatter(x=xs, y=lr.intercept + lr.slope * xs, name=f"迴歸線：斜率 {lr.slope:.2f}",
                        line=dict(color="#d64545", width=3)))
f3.update_layout(**base, title="USD/TWD 月變動 vs 台股月報酬（正值＝台幣貶值）",
                 xaxis_title="USD/TWD 月變動 (%)", yaxis_title="台股月報酬 (%)")

cfg = dict(displaylogo=False, responsive=True, displayModeBar=False)
divs = [pio.to_html(fig, full_html=False, include_plotlyjs=(i == 0), config=cfg) for i, fig in enumerate([f1, f2, f3])]
hike, flat, cut = reg["mean"]
kpis = [
    ("升息月台股平均月報酬", f"{hike:+.2f}%", f"利率不動月 {flat:+.2f}%、降息月 {cut:+.2f}%"),
    ("升息幅度與台股報酬相關係數", f"{r_ffr:.3f}", f"p = {p_ffr:.2f}，統計上不顯著"),
    ("台幣每貶值 1%，台股當月", f"{lr.slope:+.2f}%", f"p {'< 0.001' if lr.pvalue < .001 else '= %.3f' % lr.pvalue}，r = {lr.rvalue:.2f}"),
    ("匯率可解釋的台股波動 (R²)", f"{R2*100:.1f}%", "其餘大多來自其他因素"),
]
kh = "".join(f'<div class="kpi"><div class="kt">{t}</div><div class="kv">{v}</div><div class="ks">{s}</div></div>' for t, v, s in kpis)
html = f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>美國升息對台股與新台幣的影響｜互動儀表板</title>
<style>
body{{margin:0;background:#f4f6fa;color:#1d2433;font-family:{FONT};line-height:1.7}}
header{{background:linear-gradient(120deg,#16325c,#1f4e8c);color:#fff;padding:32px 20px}}
.w{{max-width:1100px;margin:auto;padding:0 16px}} h1{{margin:0 0 6px;font-size:1.7rem}}
header p{{margin:0;opacity:.85}} header a{{color:#ffd58a}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:-22px auto 20px}}
.kpi,.card{{background:#fff;border-radius:12px;box-shadow:0 2px 10px rgba(20,40,80,.08);padding:16px 18px}}
.kt{{font-size:.9rem;color:#5b6475}} .kv{{font-size:2rem;font-weight:700;color:#16325c}} .ks{{font-size:.85rem;color:#7a8394}}
.card{{margin-bottom:18px}} .grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
@media(max-width:800px){{.grid{{grid-template-columns:1fr}} h1{{font-size:1.35rem}}}}
h2{{font-size:1.2rem;color:#16325c;margin-top:0}} footer{{text-align:center;color:#7a8394;padding:20px;font-size:.9rem}}
</style></head><body>
<header><div class="w"><h1>美國升息對台股與新台幣的影響</h1>
<p>{start} – {end}，共 {n} 個月｜資料：FRED（聯邦基金利率、USD/TWD）、Yahoo Finance（^TWII）｜作者：吳柏逸｜<a href="https://github.com/Wu0510/fed-rate-hike-taiex">GitHub 原始碼</a></p></div></header>
<div class="w"><div class="kpis">{kh}</div>
<div class="card">{divs[0]}</div>
<div class="grid"><div class="card">{divs[1]}</div><div class="card">{divs[2]}</div></div>
<div class="card"><h2>結論</h2><ul>
<li><b>升息不等於台股一定跌。</b>升息月平均月報酬 {hike:+.2f}%，比利率不動月（{flat:+.2f}%）差，但兩者每月的相關係數只有 {r_ffr:.3f}（p = {p_ffr:.2f}），統計上看不出穩定關係。</li>
<li><b>真正跟台股同步的是匯率。</b>台幣當月每貶值 1%，台股平均下跌約 {abs(lr.slope):.2f}%，而且非常顯著；可能反映外資匯出時「股匯雙殺」。</li>
<li><b>但匯率也只解釋一小部分。</b>R² 約 {R2*100:.1f}%，台股大部分波動仍來自景氣、產業（如半導體）與全球資金等因素。</li></ul>
<h2>限制</h2><ul>
<li>使用月資料，看不到議息會議前後幾天的短期反應；市場也常在升息前就先反映預期。</li>
<li>相關不等於因果：匯率與股價可能同時受外資動向影響，不能說「台幣貶值造成台股下跌」。</li>
<li>以利率月變動劃分升息／降息，未區分升息幅度與當時的景氣循環；指數為價格指數，未含股利。</li></ul></div></div>
<footer>© 吳柏逸｜以 scripts/build_dashboard.py 自動產生｜<a href="https://github.com/Wu0510/fed-rate-hike-taiex">github.com/Wu0510/fed-rate-hike-taiex</a></footer>
</body></html>"""
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs/index.html").write_text(html, encoding="utf-8")
print(dict(hike=hike, flat=flat, cut=cut, r_ffr=r_ffr, p_ffr=p_ffr, slope=lr.slope, p=lr.pvalue, r=lr.rvalue, R2=R2, n=n, start=start, end=end))
