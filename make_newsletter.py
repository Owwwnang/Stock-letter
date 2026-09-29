# -*- coding: utf-8 -*-
"""
매일 주식 뉴스레터 만들기 (국내 / 미국)

실행 방법
  python make_newsletter.py          -> docs/index.html 파일이 만들어져요
  python make_newsletter.py --open   -> 만들고 바로 인터넷 창으로 열어요
  python make_newsletter.py --demo   -> 인터넷 없이 '가짜 숫자'로 모양만 미리 봐요

주의: 이 뉴스레터는 공부용 참고 자료예요. 투자 추천이 아니에요.
"""
import os
import sys
import html
import random
import webbrowser
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd

KST = timezone(timedelta(hours=9))

# =====================================================================
# 1. 지켜볼 종목 목록  (여기만 고쳐도 돼요. "코드": "이름" 형식)
#    - 코스피 종목은 뒤에 .KS, 코스닥 종목은 뒤에 .KQ 를 붙여요
#    - 미국 종목은 티커 그대로 (예: AAPL)
# =====================================================================
KR_STOCKS = {
    "005930.KS": "삼성전자", "000660.KS": "SK하이닉스", "373220.KS": "LG에너지솔루션",
    "207940.KS": "삼성바이오로직스", "005380.KS": "현대차", "000270.KS": "기아",
    "068270.KS": "셀트리온", "105560.KS": "KB금융", "055550.KS": "신한지주",
    "086790.KS": "하나금융지주", "316140.KS": "우리금융지주", "035420.KS": "NAVER",
    "035720.KS": "카카오", "005490.KS": "POSCO홀딩스", "051910.KS": "LG화학",
    "006400.KS": "삼성SDI", "012330.KS": "현대모비스", "028260.KS": "삼성물산",
    "032830.KS": "삼성생명", "003550.KS": "LG", "066570.KS": "LG전자",
    "096770.KS": "SK이노베이션", "034020.KS": "두산에너빌리티", "012450.KS": "한화에어로스페이스",
    "329180.KS": "HD현대중공업", "009540.KS": "HD한국조선해양", "042660.KS": "한화오션",
    "010140.KS": "삼성중공업", "267260.KS": "HD현대일렉트릭", "298040.KS": "효성중공업",
    "064350.KS": "현대로템", "079550.KS": "LIG넥스원", "017670.KS": "SK텔레콤",
    "030200.KS": "KT", "015760.KS": "한국전력", "010130.KS": "고려아연",
    "011200.KS": "HMM", "003670.KS": "포스코퓨처엠", "259960.KS": "크래프톤",
    "352820.KS": "하이브", "036570.KS": "엔씨소프트", "251270.KS": "넷마블",
    "018260.KS": "삼성에스디에스", "009150.KS": "삼성전기", "064400.KS": "LG CNS",
    "090430.KS": "아모레퍼시픽", "051900.KS": "LG생활건강", "192820.KS": "코스맥스",
    "161890.KS": "한국콜마", "278470.KS": "에이피알", "271560.KS": "오리온",
    "097950.KS": "CJ제일제당", "004370.KS": "농심", "003490.KS": "대한항공",
    "139480.KS": "이마트", "323410.KS": "카카오뱅크", "377300.KS": "카카오페이",
    # 코스닥
    "247540.KQ": "에코프로비엠", "086520.KQ": "에코프로", "196170.KQ": "알테오젠",
    "028300.KQ": "HLB", "068760.KQ": "셀트리온제약", "293490.KQ": "카카오게임즈",
    "263750.KQ": "펄어비스", "035900.KQ": "JYP Ent.", "041510.KQ": "에스엠",
    "122870.KQ": "와이지엔터테인먼트", "214150.KQ": "클래시스", "145020.KQ": "휴젤",
    "058470.KQ": "리노공업", "240810.KQ": "원익IPS", "039030.KQ": "이오테크닉스",
}

US_STOCKS = {
    "AAPL": "애플", "MSFT": "마이크로소프트", "NVDA": "엔비디아", "AMZN": "아마존",
    "GOOGL": "구글(알파벳)", "META": "메타", "TSLA": "테슬라", "AVGO": "브로드컴",
    "BRK-B": "버크셔해서웨이", "JPM": "JP모건", "V": "비자", "MA": "마스터카드",
    "UNH": "유나이티드헬스", "LLY": "일라이릴리", "XOM": "엑슨모빌", "JNJ": "존슨앤드존슨",
    "WMT": "월마트", "PG": "P&G", "HD": "홈디포", "COST": "코스트코",
    "NFLX": "넷플릭스", "AMD": "AMD", "INTC": "인텔", "ORCL": "오라클",
    "CRM": "세일즈포스", "ADBE": "어도비", "QCOM": "퀄컴", "TXN": "텍사스인스트루먼트",
    "MU": "마이크론", "PLTR": "팔란티어", "UBER": "우버", "DIS": "디즈니",
    "NKE": "나이키", "SBUX": "스타벅스", "MCD": "맥도날드", "KO": "코카콜라",
    "PEP": "펩시코", "PFE": "화이자", "MRK": "머크", "ABBV": "애브비",
    "BA": "보잉", "CAT": "캐터필러", "GE": "GE에어로스페이스", "F": "포드",
    "GM": "GM", "BAC": "뱅크오브아메리카", "WFC": "웰스파고", "GS": "골드만삭스",
    "PYPL": "페이팔", "SHOP": "쇼피파이", "COIN": "코인베이스", "TSM": "TSMC",
    "ASML": "ASML", "ARM": "ARM", "CVS": "CVS헬스", "TGT": "타깃",
    "LULU": "룰루레몬", "ELF": "e.l.f. 뷰티", "EL": "에스티로더", "ULTA": "울타뷰티",
}

# 시장 전체를 보여주는 '바구니' 지수들
INDEXES = {
    "^KS11": ("코스피", "KR", "한국 대표 회사 800여 개를 한 바구니에 담은 가격표예요."),
    "^KQ11": ("코스닥", "KR", "한국의 작지만 빨리 크는 회사들(바이오·2차전지·게임 등) 바구니예요."),
    "^GSPC": ("S&P 500", "US", "미국 대표 회사 500개 바구니예요. 미국 시장의 '평균 성적표'라고 보면 돼요."),
    "^IXIC": ("나스닥", "US", "애플·엔비디아 같은 기술 회사가 많이 들어 있는 바구니예요."),
    "^DJI": ("다우", "US", "미국의 오래된 대기업 30개만 담은 바구니예요."),
}
FX = "KRW=X"   # 원/달러 환율
VIX = "^VIX"   # 미국 공포지수

# =====================================================================
# 2. 기준 숫자  (바꿔도 돼요)
# =====================================================================
PANIC_DROP = -4.0        # 하루에 -4% 이상 떨어지면 '망했다고 난리' 후보
DIP_DRAWDOWN = -20.0     # 1년 중 제일 비쌀 때보다 20% 이상 싸졌고
DIP_RSI = 40             # '팔자 체력 게이지(RSI)'가 40 이하이고
DIP_TODAY_MIN = -3.0     # 오늘 -3%보다 더 빠지는 중이면 '떨어지는 칼날'이라 뺌

OUT_DIR = "docs"         # 완성된 웹페이지가 저장되는 폴더


# =====================================================================
# 3. 데이터 가져오기 (야후 파이낸스, 무료)
# =====================================================================
def download(tickers):
    """종목들의 1년치 가격을 한 번에 받아와요."""
    import yfinance as yf

    raw = yf.download(list(tickers), period="1y", interval="1d", auto_adjust=True,
                      group_by="ticker", progress=False, threads=True)
    out = {}
    for t in tickers:
        try:
            df = raw[t][["Close", "Volume"]].dropna(subset=["Close"])
        except (KeyError, TypeError):
            continue
        if len(df) >= 30:
            out[t] = df
    return out


def demo_download(tickers):
    """--demo 용: 인터넷 없이 가짜 가격을 만들어요 (진짜 시세 아님)."""
    days = pd.bdate_range(end=datetime.now(KST).date(), periods=250)
    out = {}
    for t in tickers:
        rnd = random.Random(t + str(datetime.now(KST).date()))
        price, closes, vols = rnd.uniform(20, 500), [], []
        trend = rnd.uniform(-0.002, 0.002)
        for i in range(len(days)):
            shock = rnd.gauss(trend, 0.02)
            if i == len(days) - 1:
                shock = rnd.gauss(0, 0.03)
            price *= 1 + shock
            closes.append(price)
            vols.append(rnd.uniform(0.7, 1.3) * 1e6 * (3 if abs(shock) > 0.05 else 1))
        out[t] = pd.DataFrame({"Close": closes, "Volume": vols}, index=days)
    return out


# =====================================================================
# 4. 숫자 계산
# =====================================================================
def rsi(close, n=14):
    """RSI: 최근 14일 동안 '사자'와 '팔자' 중 누가 더 셌는지 0~100 점수."""
    diff = close.diff()
    up = diff.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    down = (-diff.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = up / down.replace(0, np.nan)
    value = (100 - 100 / (1 + rs)).iloc[-1]
    return float(value) if pd.notna(value) else 50.0


def stats(ticker, name, df):
    c, v = df["Close"], df["Volume"]
    last, prev = float(c.iloc[-1]), float(c.iloc[-2])
    avg_vol = float(v.iloc[-21:-1].mean())
    return {
        "ticker": ticker, "name": name, "price": last, "date": c.index[-1],
        "chg": (last / prev - 1) * 100,
        "chg5": (last / float(c.iloc[-6]) - 1) * 100 if len(c) > 6 else 0.0,
        "high": float(c.max()),
        "dd": (last / float(c.max()) - 1) * 100,
        "rsi": rsi(c),
        "vol_x": float(v.iloc[-1]) / avg_vol if avg_vol > 0 else 0.0,
    }


def build_rows(names, data):
    rows = [stats(t, names[t], data[t]) for t in names if t in data]
    if not rows:
        return rows
    newest = max(r["date"] for r in rows)
    # 거래정지 등으로 오래된 데이터는 빼요
    return [r for r in rows if (newest - r["date"]).days <= 5]


def pick_panic(rows):
    hit = sorted([r for r in rows if r["chg"] <= PANIC_DROP], key=lambda r: r["chg"])[:5]
    if hit:
        return hit, True
    return sorted(rows, key=lambda r: r["chg"])[:3], False


def pick_dip(rows):
    cands = [r for r in rows
             if r["dd"] <= DIP_DRAWDOWN and r["rsi"] <= DIP_RSI and r["chg"] > DIP_TODAY_MIN]
    for r in cands:
        # 많이 싸졌을수록, 많이 지쳤을수록, 최근 5일 반등 중이면 점수 UP
        r["score"] = -r["dd"] * 0.5 + (DIP_RSI - r["rsi"]) + (5 if r["chg5"] > 0 else 0)
    return sorted(cands, key=lambda r: -r["score"])[:5]


# =====================================================================
# 5. 초딩도 알아듣는 문장 만들기
# =====================================================================
def weather(chg):
    if chg >= 1:
        return "맑음", "up"
    if chg >= 0:
        return "조금 맑음", "up"
    if chg > -1:
        return "흐림", "down"
    return "비", "down"


def pct(x):
    return f"{x:+.2f}%"


def won_example(chg):
    diff = int(round(1_000_000 * chg / 100, -2))
    word = "늘었어요" if diff >= 0 else "줄었어요"
    return f"100만 원어치 갖고 있었다면 {abs(diff):,}원 {word}."


def money(x, market):
    return f"{x:,.0f}원" if market == "KR" else f"${x:,.2f}"


def breadth_text(rows):
    if not rows:
        return "", 0.5
    up = sum(r["chg"] > 0 for r in rows)
    ratio = up / len(rows)
    base = f"우리가 지켜보는 {len(rows)}개 종목 중 <b>{up}개 오르고 {len(rows) - up}개 내렸어요.</b> "
    if ratio >= 0.7:
        tail = "거의 다 같이 올랐어요 → 시장 전체 분위기가 좋았던 날이에요."
    elif ratio <= 0.3:
        tail = "거의 다 같이 내렸어요 → 특정 회사 문제라기보다 시장 전체 분위기 탓일 가능성이 커요."
    else:
        tail = "오른 종목과 내린 종목이 섞였어요 → 회사마다 사정이 달랐던 날이에요."
    return base + tail, ratio


def panic_reason(r, ratio):
    lines = [f"하루 만에 <b>{pct(r['chg'])}</b> 떨어졌어요. {won_example(r['chg'])}"]
    if r["vol_x"] >= 2:
        lines.append(f"평소보다 <b>{r['vol_x']:.1f}배</b> 많이 사고팔았어요 → 사람들이 놀라서 우르르 움직였다는 뜻이에요.")
    elif r["vol_x"] > 0:
        lines.append(f"거래량은 평소의 {r['vol_x']:.1f}배예요.")
    if ratio <= 0.3:
        lines.append("오늘은 시장 전체가 빠진 날이라, 이 회사만의 문제가 아닐 수도 있어요.")
    else:
        lines.append("시장은 그럭저럭인데 혼자 크게 빠졌어요 → 회사에 무슨 일이 있었을 가능성이 커요. 뉴스를 꼭 확인하세요.")
    return lines


def dip_reason(r, market):
    high, now = r["high"], r["price"]
    lines = [
        f"1년 중 제일 비쌀 때 {money(high, market)} → 지금 {money(now, market)} "
        f"(<b>{r['dd']:.0f}%</b> 싸졌어요).",
        f"'팔자 체력 게이지(RSI)' <b>{r['rsi']:.0f}</b>/100 → 30 아래면 너무 많이 팔려서 지친 상태, 40 아래면 지쳐가는 중이에요.",
    ]
    if r["chg5"] > 0:
        lines.append(f"최근 5일은 {pct(r['chg5'])}로 살짝 고개를 드는 중이에요.")
    else:
        lines.append(f"최근 5일은 {pct(r['chg5'])}로 아직 내려가는 중이에요. 서두르지 말고 지켜보세요.")
    return lines


def news_link(r, market):
    code = r["ticker"].split(".")[0]
    if market == "KR":
        return f"https://finance.naver.com/item/news.naver?code={code}"
    return f"https://finance.yahoo.com/quote/{r['ticker']}/news"


# =====================================================================
# 6. 웹페이지(HTML) 만들기
# =====================================================================
CSS = """
:root{--bg:#f6f7fb;--card:#fff;--ink:#1d2330;--sub:#5b6475;--line:#e4e7ee;
--up:#d93a3a;--down:#2f6fe0;--accent:#6b4eff;--warn-bg:#fff4e5;--warn:#8a5300}
@media (prefers-color-scheme:dark){:root{--bg:#12151c;--card:#1b1f29;--ink:#e8ebf2;
--sub:#9aa3b5;--line:#2a3040;--up:#ff6b6b;--down:#6aa0ff;--accent:#a18cff;
--warn-bg:#2d2415;--warn:#ffcf88}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 -apple-system,
"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif}
.wrap{max-width:760px;margin:0 auto;padding:24px 16px 60px}
h1{font-size:26px;margin:0 0 4px}
h2{font-size:20px;margin:36px 0 12px;padding-bottom:6px;border-bottom:2px solid var(--line)}
h3{font-size:17px;margin:22px 0 10px}
.meta{color:var(--sub);font-size:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;margin:10px 0}
.summary{border-left:5px solid var(--accent)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}
.idx .n{font-weight:700}.idx .v{font-size:22px;font-weight:700}
.up{color:var(--up)}.down{color:var(--down)}
.badge{display:inline-block;font-size:13px;padding:1px 9px;border-radius:99px;
border:1px solid currentColor;margin-left:6px;vertical-align:2px}
.small{font-size:14px;color:var(--sub)}
.stock .top{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;align-items:baseline}
.stock .name{font-weight:700;font-size:17px}
.stock ul{margin:8px 0 6px;padding-left:20px}
.stock a{color:var(--accent);font-size:14px}
.warn{background:var(--warn-bg);color:var(--warn);border-radius:12px;padding:12px 14px;font-size:14px}
.empty{color:var(--sub)}
.movers{display:flex;flex-wrap:wrap;gap:6px}
.chip{background:var(--card);border:1px solid var(--line);border-radius:99px;padding:3px 12px;font-size:14px}
footer{margin-top:40px;font-size:13px;color:var(--sub)}
footer a{color:var(--sub)}
"""


def esc(s):
    return html.escape(str(s))


def index_cards(idx_rows, market):
    cards = []
    for t, (name, mk, desc) in INDEXES.items():
        if mk != market or t not in idx_rows:
            continue
        r = idx_rows[t]
        w, cls = weather(r["chg"])
        cards.append(
            f'<div class="card idx"><div class="n">{esc(name)}<span class="badge {cls}">{w}</span></div>'
            f'<div class="v {cls}">{pct(r["chg"])}</div>'
            f'<div class="small">{esc(desc)} {won_example(r["chg"])}</div></div>')
    return '<div class="grid">' + "".join(cards) + "</div>" if cards else ""


def stock_card(r, market, lines):
    cls = "up" if r["chg"] >= 0 else "down"
    items = "".join(f"<li>{x}</li>" for x in lines)
    return (f'<div class="card stock"><div class="top"><span class="name">{esc(r["name"])} '
            f'<span class="small">{esc(r["ticker"])}</span></span>'
            f'<span class="{cls}"><b>{money(r["price"], market)}</b> ({pct(r["chg"])})</span></div>'
            f'<ul>{items}</ul><a href="{news_link(r, market)}" target="_blank" rel="noopener">'
            f'왜 그런지 뉴스 보기 →</a></div>')


def movers_html(rows, market):
    top = sorted(rows, key=lambda r: -r["chg"])[:3]
    chips = "".join(f'<span class="chip">{esc(r["name"])} <span class="up">{pct(r["chg"])}</span></span>'
                    for r in top if r["chg"] > 0)
    return f'<p class="small">오늘 제일 많이 오른 종목</p><div class="movers">{chips}</div>' if chips else ""


def market_section(title, market, rows, idx_rows):
    parts = [f"<h2>{title}</h2>", index_cards(idx_rows, market)]
    text, ratio = breadth_text(rows)
    if text:
        parts.append(f'<div class="card">{text}{movers_html(rows, market)}</div>')

    panic, is_panic = pick_panic(rows)
    parts.append("<h3>사람들이 '망했다'고 난리인 종목</h3>")
    if not is_panic:
        parts.append(f'<p class="empty">오늘은 {abs(PANIC_DROP):.0f}% 넘게 폭락한 종목이 없어요. '
                     f'대신 가장 많이 내린 종목을 보여드려요.</p>')
    for r in panic:
        parts.append(stock_card(r, market, panic_reason(r, ratio)))

    dips = pick_dip(rows)
    parts.append("<h3>저점매수 '후보' (공부용)</h3>")
    parts.append('<p class="small">조건: 1년 최고가보다 20% 이상 싸짐 + 팔자 체력 게이지 40 이하 + '
                 '오늘 폭락 중인 종목은 제외</p>')
    if not dips:
        parts.append('<p class="empty">오늘은 조건에 맞는 종목이 없어요. 억지로 채우지 않았어요.</p>')
    for r in dips:
        parts.append(stock_card(r, market, dip_reason(r, market)))
    return "\n".join(parts)


def headline(idx_rows, kr_rows, us_rows):
    def avg(market):
        v = [idx_rows[t]["chg"] for t, x in INDEXES.items() if x[1] == market and t in idx_rows]
        return sum(v) / len(v) if v else None

    kr, us = avg("KR"), avg("US")
    bits = []
    if kr is not None:
        bits.append(f"한국은 <b>{weather(kr)[0]}</b>")
    if us is not None:
        bits.append(f"미국은 <b>{weather(us)[0]}</b>")
    line = "오늘의 날씨: " + ", ".join(bits) + "."
    extra = []
    if FX in idx_rows:
        r = idx_rows[FX]
        diff = r["price"] * r["chg"] / (100 + r["chg"])
        direction = "비싸졌어요" if diff > 0 else "싸졌어요"
        extra.append(f"1달러 = <b>{r['price']:,.0f}원</b> (어제보다 {diff:+.0f}원, 달러가 {direction}). "
                     "달러가 비싸지면 해외직구·여행이 조금 비싸지고, 외국인이 한국 주식을 팔고 나갈 때 자주 이런 모습이 나와요.")
    if VIX in idx_rows:
        v = idx_rows[VIX]["price"]
        mood = "많이 불안해요" if v >= 30 else "조금 불안해요" if v >= 20 else "차분해요"
        extra.append(f"미국 공포지수(VIX) <b>{v:.1f}</b> → 20 아래면 차분, 30 넘으면 겁먹은 상태예요. 지금은 {mood}.")
    return f'<div class="card summary"><p><b>{line}</b></p>' + "".join(f"<p>{x}</p>" for x in extra) + "</div>"


def archive_links():
    folder = os.path.join(OUT_DIR, "archive")
    if not os.path.isdir(folder):
        return ""
    files = sorted((f for f in os.listdir(folder) if f.endswith(".html")), reverse=True)[:30]
    links = " · ".join(f'<a href="archive/{f}">{f[:-5]}</a>' for f in files)
    return f"<p>지난 뉴스레터: {links}</p>" if links else ""


def page(body, now, demo, kr_date, us_date, footer_extra=""):
    banner = ('<div class="warn"><b>예시 화면이에요.</b> --demo 모드라서 숫자는 모두 가짜예요.</div>'
              if demo else "")
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>오늘의 주식 날씨 {now:%m/%d}</title><style>{CSS}</style></head>
<body><div class="wrap">
<h1>오늘의 주식 날씨</h1>
<div class="meta">만든 시각 {now:%Y-%m-%d %H:%M} (한국시간) · 한국장 {kr_date} 마감 · 미국장 {us_date} 마감 기준</div>
{banner}
{body}
<div class="warn" style="margin-top:28px">이 페이지는 숫자를 자동으로 정리한 <b>공부용 자료</b>예요.
'저점매수 후보'는 싸졌다는 뜻이지, 오른다는 보장이 아니에요. 투자 결정은 뉴스와 회사 사정을 직접 확인하고 스스로 판단하세요.</div>
<footer>{footer_extra}<p>데이터: Yahoo Finance (무료, 약간 늦거나 틀릴 수 있어요)</p></footer>
</div></body></html>"""


# =====================================================================
# 7. 전체 실행
# =====================================================================
def main():
    demo = "--demo" in sys.argv
    get = demo_download if demo else download
    now = datetime.now(KST)

    print("1/3 가격 데이터 받는 중...")
    idx_data = get(list(INDEXES) + [FX, VIX])
    kr_data = get(list(KR_STOCKS))
    us_data = get(list(US_STOCKS))

    print("2/3 계산 중...")
    idx_rows = {t: stats(t, t, df) for t, df in idx_data.items()}
    kr_rows = build_rows(KR_STOCKS, kr_data)
    us_rows = build_rows(US_STOCKS, us_data)
    if not kr_rows and not us_rows:
        sys.exit("데이터를 하나도 못 받았어요. 인터넷 연결을 확인하거나 잠시 후 다시 해보세요.")

    kr_date = max(r["date"] for r in kr_rows).strftime("%m/%d") if kr_rows else "-"
    us_date = max(r["date"] for r in us_rows).strftime("%m/%d") if us_rows else "-"

    body = "\n".join([
        headline(idx_rows, kr_rows, us_rows),
        market_section("한국 시장", "KR", kr_rows, idx_rows),
        market_section("미국 시장", "US", us_rows, idx_rows),
    ])

    print("3/3 웹페이지 저장 중...")
    os.makedirs(os.path.join(OUT_DIR, "archive"), exist_ok=True)
    day_file = os.path.join(OUT_DIR, "archive", f"{now:%Y-%m-%d}.html")
    with open(day_file, "w", encoding="utf-8") as f:
        f.write(page(body, now, demo, kr_date, us_date, '<p><a href="../index.html">← 오늘 것 보기</a></p>'))
    index_file = os.path.join(OUT_DIR, "index.html")
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(page(body, now, demo, kr_date, us_date, archive_links()))

    print(f"완성! → {os.path.abspath(index_file)}")
    if "--open" in sys.argv:
        webbrowser.open("file://" + os.path.abspath(index_file))


if __name__ == "__main__":
    main()
