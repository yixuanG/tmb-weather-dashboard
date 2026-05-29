#!/usr/bin/env python3
"""Fetch Open-Meteo archive data and build a static TMB weather dashboard."""

from __future__ import annotations

import json
import math
import statistics
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DASHBOARD_PATH = ROOT / "dashboard.html"
PROCESSED_JSON = DATA_DIR / "tmb_weather_analytics_2022_2026.json"
LEGACY_PROCESSED_JSON = DATA_DIR / "tmb_weather_analytics_2022_2025.json"
HOURLY_CSV = DATA_DIR / "tmb_open_meteo_hourly_2022_2026_available.csv"

API_URL = "https://archive-api.open-meteo.com/v1/archive"
YEARS = [2022, 2023, 2024, 2025]
START_MONTH_DAY = "06-01"
END_MONTH_DAY = "07-31"
TIMEZONE = "Europe/Paris"

HOURLY_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "apparent_temperature",
    "precipitation",
    "rain",
    "snowfall",
    "weather_code",
    "cloud_cover",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "surface_pressure",
    "is_day",
]

DAILY_VARS = [
    "weather_code",
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "apparent_temperature_max",
    "apparent_temperature_min",
    "precipitation_sum",
    "rain_sum",
    "snowfall_sum",
    "precipitation_hours",
    "sunshine_duration",
    "relative_humidity_2m_mean",
    "relative_humidity_2m_max",
    "relative_humidity_2m_min",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "wind_direction_10m_dominant",
]


# Representative weather sampling points along the classic anti-clockwise TMB.
# They are not navigation waypoints; the goal is to sample distinct microclimates.
POINTS = [
    {
        "id": "les_houches",
        "name": "Les Houches",
        "country": "FR",
        "sample_km": 0,
        "lat": 45.8907,
        "lon": 6.7989,
        "elevation_m": 1008,
        "terrain": "valley trailhead",
    },
    {
        "id": "col_de_voza",
        "name": "Col de Voza / Bellevue",
        "country": "FR",
        "sample_km": 10,
        "lat": 45.8583,
        "lon": 6.7483,
        "elevation_m": 1653,
        "terrain": "ridge pass",
    },
    {
        "id": "les_contamines",
        "name": "Les Contamines-Montjoie",
        "country": "FR",
        "sample_km": 20,
        "lat": 45.8211,
        "lon": 6.7285,
        "elevation_m": 1167,
        "terrain": "valley village",
    },
    {
        "id": "nant_borrant",
        "name": "Nant Borrant / La Balme",
        "country": "FR",
        "sample_km": 30,
        "lat": 45.7771,
        "lon": 6.7067,
        "elevation_m": 1706,
        "terrain": "upper valley refuge",
    },
    {
        "id": "croix_bonhomme",
        "name": "Col de la Croix du Bonhomme",
        "country": "FR",
        "sample_km": 40,
        "lat": 45.7220,
        "lon": 6.7200,
        "elevation_m": 2433,
        "terrain": "high exposed pass",
    },
    {
        "id": "les_chapieux",
        "name": "Les Chapieux",
        "country": "FR",
        "sample_km": 50,
        "lat": 45.6966,
        "lon": 6.7330,
        "elevation_m": 1550,
        "terrain": "valley hamlet",
    },
    {
        "id": "col_de_la_seigne",
        "name": "Col de la Seigne",
        "country": "FR/IT",
        "sample_km": 60,
        "lat": 45.7514,
        "lon": 6.8061,
        "elevation_m": 2516,
        "terrain": "border pass",
    },
    {
        "id": "rifugio_elisabetta",
        "name": "Rifugio Elisabetta / Val Veny",
        "country": "IT",
        "sample_km": 70,
        "lat": 45.7658,
        "lon": 6.8258,
        "elevation_m": 2195,
        "terrain": "glacier-facing refuge",
    },
    {
        "id": "lac_combal",
        "name": "Lac Combal / Cabane du Combal",
        "country": "IT",
        "sample_km": 80,
        "lat": 45.7900,
        "lon": 6.8680,
        "elevation_m": 1970,
        "terrain": "high valley basin",
    },
    {
        "id": "courmayeur",
        "name": "Courmayeur",
        "country": "IT",
        "sample_km": 90,
        "lat": 45.7969,
        "lon": 6.9686,
        "elevation_m": 1224,
        "terrain": "town",
    },
    {
        "id": "rifugio_bertone",
        "name": "Rifugio Bertone / Mont de la Saxe",
        "country": "IT",
        "sample_km": 100,
        "lat": 45.8296,
        "lon": 6.9821,
        "elevation_m": 1989,
        "terrain": "balcony ridge",
    },
    {
        "id": "rifugio_bonatti",
        "name": "Rifugio Bonatti / Val Ferret",
        "country": "IT",
        "sample_km": 110,
        "lat": 45.8654,
        "lon": 7.0356,
        "elevation_m": 2025,
        "terrain": "high valley refuge",
    },
    {
        "id": "grand_col_ferret",
        "name": "Grand Col Ferret",
        "country": "IT/CH",
        "sample_km": 120,
        "lat": 45.8890,
        "lon": 7.0790,
        "elevation_m": 2537,
        "terrain": "highest classic pass",
    },
    {
        "id": "la_fouly",
        "name": "La Fouly",
        "country": "CH",
        "sample_km": 130,
        "lat": 45.9324,
        "lon": 7.0982,
        "elevation_m": 1600,
        "terrain": "Swiss valley village",
    },
    {
        "id": "champex_lac",
        "name": "Champex-Lac",
        "country": "CH",
        "sample_km": 140,
        "lat": 46.0313,
        "lon": 7.1166,
        "elevation_m": 1466,
        "terrain": "lake village",
    },
    {
        "id": "trient",
        "name": "Trient / Col de la Forclaz",
        "country": "CH",
        "sample_km": 150,
        "lat": 46.0550,
        "lon": 7.0020,
        "elevation_m": 1527,
        "terrain": "pass village",
    },
    {
        "id": "col_de_balme",
        "name": "Col de Balme",
        "country": "FR/CH",
        "sample_km": 160,
        "lat": 46.0272,
        "lon": 6.9694,
        "elevation_m": 2191,
        "terrain": "border pass",
    },
    {
        "id": "lac_blanc_flegere",
        "name": "Lac Blanc / La Flegere",
        "country": "FR",
        "sample_km": 170,
        "lat": 45.9810,
        "lon": 6.8890,
        "elevation_m": 2352,
        "terrain": "Aiguilles Rouges balcony",
    },
    {
        "id": "le_brevent",
        "name": "Le Brevent / return balcony",
        "country": "FR",
        "sample_km": 180,
        "lat": 45.9339,
        "lon": 6.8374,
        "elevation_m": 2525,
        "terrain": "exposed ridge",
    },
]


def api_request(point: dict, year: int) -> dict:
    params = {
        "latitude": point["lat"],
        "longitude": point["lon"],
        "start_date": f"{year}-{START_MONTH_DAY}",
        "end_date": f"{year}-{END_MONTH_DAY}",
        "hourly": ",".join(HOURLY_VARS),
        "daily": ",".join(DAILY_VARS),
        "timezone": TIMEZONE,
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
        "timeformat": "iso8601",
        "cell_selection": "land",
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)
    for attempt in range(6):
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                if response.status >= 400:
                    raise RuntimeError(f"Open-Meteo returned HTTP {response.status}: {url}")
                payload = json.loads(response.read().decode("utf-8"))
            break
        except HTTPError as exc:
            if exc.code != 429 or attempt == 5:
                raise
            wait = 8 * (attempt + 1)
            print(f"Rate limited by Open-Meteo; waiting {wait}s before retry...")
            time.sleep(wait)
        except URLError:
            if attempt == 5:
                raise
            wait = 4 * (attempt + 1)
            print(f"Network hiccup; waiting {wait}s before retry...")
            time.sleep(wait)
    else:
        raise RuntimeError(f"Failed to fetch {point['name']} {year}")
    if "error" in payload:
        raise RuntimeError(f"Open-Meteo error for {point['name']} {year}: {payload}")
    return payload


def values(series: list) -> list[float]:
    return [x for x in series if isinstance(x, (int, float)) and not math.isnan(x)]


def mean(series: list) -> float | None:
    clean = values(series)
    return round(statistics.fmean(clean), 2) if clean else None


def total(series: list) -> float:
    return round(sum(values(series)), 2)


def count_where(series: list, predicate) -> int:
    return sum(1 for x in series if isinstance(x, (int, float)) and predicate(x))


def summarize_point_year(point: dict, year: int, payload: dict) -> dict:
    hourly = payload["hourly"]
    daily = payload["daily"]
    precip_days = values(daily.get("precipitation_sum", []))
    temps = values(hourly.get("temperature_2m", []))
    gusts = values(hourly.get("wind_gusts_10m", []))

    wet_days = sum(1 for x in precip_days if x >= 1)
    heavy_days = sum(1 for x in precip_days if x >= 10)
    dry_days = sum(1 for x in precip_days if x < 1)

    return {
        "point_id": point["id"],
        "year": year,
        "mean_temp_c": mean(hourly.get("temperature_2m", [])),
        "mean_apparent_temp_c": mean(hourly.get("apparent_temperature", [])),
        "min_temp_c": round(min(temps), 2) if temps else None,
        "max_temp_c": round(max(temps), 2) if temps else None,
        "freeze_hours": count_where(hourly.get("temperature_2m", []), lambda x: x <= 0),
        "cold_hours_lt5": count_where(hourly.get("temperature_2m", []), lambda x: x < 5),
        "hot_hours_gt25": count_where(hourly.get("temperature_2m", []), lambda x: x > 25),
        "mean_humidity_pct": mean(hourly.get("relative_humidity_2m", [])),
        "total_precip_mm": total(hourly.get("precipitation", [])),
        "total_rain_mm": total(hourly.get("rain", [])),
        "total_snow_cm": total(hourly.get("snowfall", [])),
        "wet_hours": count_where(hourly.get("precipitation", []), lambda x: x >= 0.1),
        "wet_days": wet_days,
        "heavy_precip_days": heavy_days,
        "dry_days": dry_days,
        "mean_wind_kmh": mean(hourly.get("wind_speed_10m", [])),
        "max_gust_kmh": round(max(gusts), 2) if gusts else None,
        "mean_cloud_pct": mean(hourly.get("cloud_cover", [])),
        "sunshine_hours_total": round(total(daily.get("sunshine_duration", [])) / 3600, 1),
    }


def add_risk_scores(summaries: list[dict]) -> None:
    raw_scores = []
    for item in summaries:
        wet_component = item["wet_days"] / 61 * 35
        heavy_component = item["heavy_precip_days"] / 61 * 25
        cold_component = item["cold_hours_lt5"] / (61 * 24) * 20
        wind_component = min((item["max_gust_kmh"] or 0) / 80, 1) * 15
        snow_component = min(item["total_snow_cm"] / 20, 1) * 5
        raw = wet_component + heavy_component + cold_component + wind_component + snow_component
        item["_raw_risk"] = raw
        raw_scores.append(raw)

    low = min(raw_scores) if raw_scores else 0
    high = max(raw_scores) if raw_scores else 1
    spread = high - low or 1
    for item in summaries:
        item["hiking_weather_risk"] = round(100 * (item.pop("_raw_risk") - low) / spread, 1)


def derive_weather_classes(series_by_point: dict) -> dict:
    classes = {}
    for point_id, by_year in series_by_point.items():
        classes[point_id] = {}
        for year, payload in by_year.items():
            daily = payload["daily"]
            counts = {
                "dry_stable": 0,
                "warm_wet": 0,
                "cold_wet_snow": 0,
                "wind_exposed": 0,
                "mixed": 0,
            }
            for i, date in enumerate(daily["time"]):
                precip = daily.get("precipitation_sum", [0])[i] or 0
                temp_mean = daily.get("temperature_2m_mean", [None])[i]
                temp_min = daily.get("temperature_2m_min", [None])[i]
                snow = daily.get("snowfall_sum", [0])[i] or 0
                gust = daily.get("wind_gusts_10m_max", [0])[i] or 0
                if precip < 1 and gust < 35 and (temp_mean or 0) >= 8:
                    label = "dry_stable"
                elif snow > 0 or (precip >= 1 and temp_min is not None and temp_min <= 2):
                    label = "cold_wet_snow"
                elif gust >= 45:
                    label = "wind_exposed"
                elif precip >= 5 and (temp_mean or 0) > 8:
                    label = "warm_wet"
                else:
                    label = "mixed"
                counts[label] += 1
            classes[point_id][year] = counts
    return classes


def flatten_csv(series_by_point: dict) -> str:
    cols = [
        "point_id",
        "year",
        "time",
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "precipitation",
        "rain",
        "snowfall",
        "cloud_cover",
        "wind_speed_10m",
        "wind_gusts_10m",
        "weather_code",
    ]
    lines = [",".join(cols)]
    for point_id, by_year in series_by_point.items():
        for year, payload in by_year.items():
            hourly = payload["hourly"]
            for i, ts in enumerate(hourly["time"]):
                row = [point_id, str(year), ts]
                for col in cols[3:]:
                    val = hourly.get(col, [None] * len(hourly["time"]))[i]
                    row.append("" if val is None else str(val))
                lines.append(",".join(row))
    return "\n".join(lines) + "\n"


def build_html(data: dict) -> str:
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tour du Mont Blanc Weather Analytics Dashboard</title>
  <link rel="preconnect" href="https://cdn.plot.ly">
  <link rel="preconnect" href="https://unpkg.com">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    :root {{
      --ink: #172026;
      --muted: #5f6d75;
      --paper: #fbfaf7;
      --panel: #ffffff;
      --line: #d8ded8;
      --teal: #247c78;
      --blue: #3867b7;
      --coral: #d95d4f;
      --gold: #c89225;
      --green: #4f8f54;
      --shadow: 0 14px 32px rgba(23, 32, 38, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--paper);
      color: var(--ink);
    }}
    header {{
      padding: 22px clamp(16px, 4vw, 42px) 14px;
      border-bottom: 1px solid var(--line);
      background: #f6f4ee;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(24px, 3vw, 40px);
      line-height: 1.05;
      letter-spacing: 0;
    }}
    .subtitle {{
      max-width: 1120px;
      color: var(--muted);
      line-height: 1.55;
      margin: 0;
      font-size: 15px;
    }}
    main {{
      padding: 18px clamp(16px, 4vw, 42px) 36px;
    }}
    .controls {{
      display: grid;
      grid-template-columns: repeat(5, minmax(150px, 1fr));
      gap: 12px;
      margin-bottom: 16px;
      align-items: end;
    }}
    label {{
      display: grid;
      gap: 6px;
      font-size: 12px;
      color: var(--muted);
      font-weight: 650;
    }}
    select, input[type="text"] {{
      width: 100%;
      min-height: 42px;
      border: 1px solid var(--line);
      border-radius: 7px;
      padding: 8px 10px;
      background: var(--panel);
      color: var(--ink);
      font-size: 14px;
    }}
    button {{
      min-height: 42px;
      border: 1px solid #1d625f;
      border-radius: 7px;
      background: var(--teal);
      color: #fff;
      font-weight: 750;
      cursor: pointer;
    }}
    .grid {{
      display: grid;
      gap: 16px;
    }}
    .top-grid {{
      grid-template-columns: minmax(280px, 0.95fr) minmax(420px, 1.55fr);
      align-items: stretch;
    }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(4, minmax(140px, 1fr));
      gap: 12px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}
    .kpi {{
      padding: 14px;
      min-height: 94px;
    }}
    .kpi span {{
      display: block;
      font-size: 12px;
      color: var(--muted);
      font-weight: 700;
      margin-bottom: 10px;
    }}
    .kpi strong {{
      display: block;
      font-size: clamp(24px, 3vw, 34px);
      line-height: 1;
    }}
    .kpi small {{
      display: block;
      color: var(--muted);
      margin-top: 7px;
      line-height: 1.35;
    }}
    .panel {{
      padding: 14px;
      min-height: 360px;
    }}
    .panel h2 {{
      margin: 0 0 4px;
      font-size: 16px;
      letter-spacing: 0;
    }}
    .panel p {{
      margin: 0 0 10px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }}
    #map {{
      height: 356px;
      border-radius: 7px;
      border: 1px solid var(--line);
      overflow: hidden;
    }}
    .chart {{
      width: 100%;
      height: 390px;
    }}
    .small-chart {{
      height: 330px;
    }}
    .two-col {{
      grid-template-columns: minmax(360px, 1fr) minmax(360px, 1fr);
    }}
    .three-col {{
      grid-template-columns: repeat(3, minmax(260px, 1fr));
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      text-align: left;
      border-bottom: 1px solid var(--line);
      padding: 8px 9px;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      background: #f5f7f5;
    }}
    .note {{
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
      margin-top: 14px;
    }}
    .pill {{
      display: inline-block;
      padding: 3px 7px;
      border-radius: 999px;
      background: #edf4f1;
      color: #1d625f;
      font-size: 12px;
      font-weight: 750;
      white-space: nowrap;
    }}
    a {{ color: var(--blue); }}
    @media (max-width: 1080px) {{
      .controls, .top-grid, .two-col, .three-col {{ grid-template-columns: 1fr; }}
      .kpis {{ grid-template-columns: repeat(2, minmax(140px, 1fr)); }}
      .chart {{ height: 340px; }}
    }}
    @media (max-width: 620px) {{
      main, header {{ padding-left: 12px; padding-right: 12px; }}
      .controls {{ gap: 10px; }}
      .kpis {{ grid-template-columns: 1fr; }}
      .panel {{ padding: 10px; }}
      table {{ font-size: 12px; }}
      th, td {{ padding: 7px 6px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Tour du Mont Blanc Weather Analytics</h1>
    <p class="subtitle">2023-2025 年每年 6 月 1 日至 7 月 31 日，基于 Open-Meteo Historical Weather API 的小时级天气分析。点位是面向徒步准备的气象采样网，覆盖山口、山屋、城镇、暴露山脊与谷地。</p>
  </header>

  <main>
    <section class="controls" aria-label="dashboard filters">
      <label>点位
        <select id="pointSelect"></select>
      </label>
      <label>年份
        <select id="yearSelect"></select>
      </label>
      <label>日内曲线日期
        <input id="dateSelect" type="text">
      </label>
      <label>路线热力图指标
        <select id="heatMetric">
          <option value="hiking_weather_risk">Hiking weather risk</option>
          <option value="total_precip_mm">Total precipitation</option>
          <option value="wet_days">Wet days</option>
          <option value="cold_hours_lt5">Cold hours &lt; 5C</option>
          <option value="max_gust_kmh">Max gust</option>
        </select>
      </label>
      <button id="downloadCsv">下载小时级 CSV</button>
    </section>

    <section class="kpis" id="kpiGrid"></section>

    <section class="grid top-grid" style="margin-top:16px;">
      <div class="card panel">
        <h2>Route Map</h2>
        <p>点位颜色按所选年份的综合徒步天气风险显示，点击标记可切换点位。</p>
        <div id="map"></div>
      </div>
      <div class="card panel">
        <h2>Daily Weather Window</h2>
        <p>最高/最低温、日降水与阵风，用于看连续天气窗口和高风险日期。</p>
        <div id="dailyChart" class="chart"></div>
      </div>
    </section>

    <section class="grid two-col" style="margin-top:16px;">
      <div class="card panel">
        <h2>Intraday Curve</h2>
        <p>某一天的温度、体感温度、湿度、降水与风阵，适合规划早出发或避开午后降雨。</p>
        <div id="intradayChart" class="chart"></div>
      </div>
      <div class="card panel">
        <h2>Diurnal Profile by Year</h2>
        <p>把 6-7 月所有日期按小时取均值，对比不同年份的日内典型曲线。</p>
        <div id="diurnalChart" class="chart"></div>
      </div>
    </section>

    <section class="grid two-col" style="margin-top:16px;">
      <div class="card panel">
        <h2>Route Risk Heatmap</h2>
        <p>按路线顺序比较点位与年份，快速发现暴露山口和湿冷路段。</p>
        <div id="heatmapChart" class="chart"></div>
      </div>
      <div class="card panel">
        <h2>Weather Regimes</h2>
        <p>将每日天气按阈值分类：干稳、暖湿、冷湿/雪、风大暴露、混合。</p>
        <div id="regimeChart" class="chart"></div>
      </div>
    </section>

    <section class="grid two-col" style="margin-top:16px;">
      <div class="card panel">
        <h2>Temperature vs Humidity</h2>
        <p>小时级散点用于观察潮湿、降水与冷暖之间的关系，点大小代表降水强度。</p>
        <div id="scatterChart" class="chart"></div>
      </div>
      <div class="card panel">
        <h2>Planning Table</h2>
        <p>面向户外准备的日期筛选：干燥日、重降水日、低温日和大风日。</p>
        <div style="overflow:auto; max-height:390px;">
          <table id="planningTable"></table>
        </div>
      </div>
    </section>

    <p class="note">数据源：<a href="https://open-meteo.com/en/docs/historical-weather-api?locale=en">Open-Meteo Historical Weather API</a>，接口端点 <code>archive-api.open-meteo.com/v1/archive</code>。Open-Meteo 文档说明历史天气来自再分析数据，小时变量包括 2m 温度、相对湿度、降水、云量和 10m 风等；降水是前一小时累计值。路线长度、点位和 km 标记为分析采样近似，不用于导航。高山天气变化快，实际出行仍需临近日期查看官方天气预报、山屋信息和当地风险公告。</p>
  </main>

  <script id="weather-data" type="application/json">{data_json}</script>
  <script>
    const DATA = JSON.parse(document.getElementById('weather-data').textContent);
    const points = DATA.points;
    const years = DATA.years.map(String);
    const series = DATA.series;
    const summaries = DATA.summaries;
    const regimes = DATA.weather_classes;
    const summaryByKey = new Map(summaries.map(d => [`${{d.point_id}}-${{d.year}}`, d]));
    const pointById = new Map(points.map(p => [p.id, p]));
    const palette = {{ teal: '#247c78', blue: '#3867b7', coral: '#d95d4f', gold: '#c89225', green: '#4f8f54', ink: '#172026', muted: '#5f6d75' }};

    const pointSelect = document.getElementById('pointSelect');
    const yearSelect = document.getElementById('yearSelect');
    const dateSelect = document.getElementById('dateSelect');
    const heatMetric = document.getElementById('heatMetric');

    function fmt(value, suffix = '', digits = 1) {{
      if (value === null || value === undefined || Number.isNaN(value)) return 'n/a';
      return `${{Number(value).toFixed(digits)}}${{suffix}}`;
    }}

    function selectedPoint() {{ return pointSelect.value; }}
    function selectedYear() {{ return yearSelect.value; }}
    function payload(pointId = selectedPoint(), year = selectedYear()) {{ return series[pointId][year]; }}
    function summary(pointId = selectedPoint(), year = selectedYear()) {{ return summaryByKey.get(`${{pointId}}-${{year}}`); }}

    function colorForRisk(risk) {{
      if (risk >= 75) return '#c74338';
      if (risk >= 50) return '#d9902e';
      if (risk >= 25) return '#c6a833';
      return '#3b8c69';
    }}

    function initControls() {{
      pointSelect.innerHTML = points.map(p => `<option value="${{p.id}}">${{String(p.sample_km).padStart(3, '0')}} km · ${{p.name}}</option>`).join('');
      yearSelect.innerHTML = years.map(y => `<option value="${{y}}">${{y}}</option>`).join('');
      pointSelect.value = 'grand_col_ferret';
      yearSelect.value = '2025';
      refreshDateBounds();
    }}

    function refreshDateBounds() {{
      const dates = payload().daily.time;
      dateSelect.min = dates[0];
      dateSelect.max = dates[dates.length - 1];
      if (!dates.includes(dateSelect.value)) dateSelect.value = dates[Math.floor(dates.length / 2)];
    }}

    function renderKpis() {{
      const s = summary();
      const p = pointById.get(selectedPoint());
      const html = [
        ['点位 / 海拔', `${{p.name}}`, `${{p.elevation_m}} m · ${{p.terrain}}`],
        ['均温 / 体感', fmt(s.mean_temp_c, 'C'), `apparent ${{fmt(s.mean_apparent_temp_c, 'C')}}`],
        ['总降水 / 湿天', fmt(s.total_precip_mm, ' mm'), `${{s.wet_days}} wet days · ${{s.heavy_precip_days}} heavy`],
        ['低温 / 最大阵风', `${{s.cold_hours_lt5}} h`, `max gust ${{fmt(s.max_gust_kmh, ' km/h')}}`],
      ].map(item => `<div class="card kpi"><span>${{item[0]}}</span><strong>${{item[1]}}</strong><small>${{item[2]}}</small></div>`).join('');
      document.getElementById('kpiGrid').innerHTML = html;
    }}

    let map;
    let markers = [];
    function renderMap() {{
      if (!map) {{
        map = L.map('map', {{ scrollWheelZoom: false }}).setView([45.91, 6.93], 10);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
          maxZoom: 13,
          attribution: '&copy; OpenStreetMap contributors'
        }}).addTo(map);
        const route = L.polyline(points.map(p => [p.lat, p.lon]), {{ color: palette.teal, weight: 3, opacity: 0.78 }}).addTo(map);
        map.fitBounds(route.getBounds().pad(0.12));
      }}
      markers.forEach(m => m.remove());
      markers = points.map(p => {{
        const s = summaryByKey.get(`${{p.id}}-${{selectedYear()}}`);
        const marker = L.circleMarker([p.lat, p.lon], {{
          radius: p.id === selectedPoint() ? 9 : 6,
          color: '#ffffff',
          weight: 2,
          fillColor: colorForRisk(s.hiking_weather_risk),
          fillOpacity: 0.92
        }}).addTo(map);
        marker.bindPopup(`<b>${{p.name}}</b><br>${{p.elevation_m}} m · km ${{p.sample_km}}<br>Risk ${{s.hiking_weather_risk}} / 100<br>Precip ${{s.total_precip_mm}} mm`);
        marker.on('click', () => {{
          pointSelect.value = p.id;
          refreshAll();
        }});
        return marker;
      }});
    }}

    const plotConfig = {{ responsive: true, displayModeBar: false, displaylogo: false }};
    const layoutBase = {{
      margin: {{ l: 46, r: 36, t: 16, b: 42 }},
      paper_bgcolor: '#ffffff',
      plot_bgcolor: '#ffffff',
      font: {{ family: 'Inter, system-ui, sans-serif', color: '#172026' }},
      legend: {{ orientation: 'h', y: 1.08, x: 0 }},
      hovermode: 'x unified'
    }};

    function renderDailyChart() {{
      const d = payload().daily;
      Plotly.react('dailyChart', [
        {{ x: d.time, y: d.temperature_2m_max, name: 'T max C', type: 'scatter', mode: 'lines', line: {{ color: palette.coral, width: 2 }} }},
        {{ x: d.time, y: d.temperature_2m_min, name: 'T min C', type: 'scatter', mode: 'lines', line: {{ color: palette.blue, width: 2 }} }},
        {{ x: d.time, y: d.precipitation_sum, name: 'Precip mm', type: 'bar', marker: {{ color: 'rgba(36,124,120,0.45)' }}, yaxis: 'y2' }},
        {{ x: d.time, y: d.wind_gusts_10m_max, name: 'Gust km/h', type: 'scatter', mode: 'lines', line: {{ color: palette.gold, width: 1.8, dash: 'dot' }}, yaxis: 'y3' }}
      ], {{
        ...layoutBase,
        yaxis: {{ title: 'Temperature C', zeroline: false }},
        yaxis2: {{ title: 'Precip mm', overlaying: 'y', side: 'right', rangemode: 'tozero', showgrid: false }},
        yaxis3: {{ title: 'Gust', overlaying: 'y', side: 'right', anchor: 'free', position: 0.94, showgrid: false, visible: false }}
      }}, plotConfig);
    }}

    function renderIntradayChart() {{
      const h = payload().hourly;
      const date = dateSelect.value;
      const idx = h.time.map((t, i) => [t, i]).filter(([t]) => t.startsWith(date)).map(([, i]) => i);
      const x = idx.map(i => h.time[i].slice(11, 16));
      function pick(key) {{ return idx.map(i => h[key][i]); }}
      Plotly.react('intradayChart', [
        {{ x, y: pick('temperature_2m'), name: 'Temp C', type: 'scatter', mode: 'lines+markers', line: {{ color: palette.coral }} }},
        {{ x, y: pick('apparent_temperature'), name: 'Feels C', type: 'scatter', mode: 'lines', line: {{ color: palette.gold, dash: 'dot' }} }},
        {{ x, y: pick('relative_humidity_2m'), name: 'Humidity %', type: 'scatter', mode: 'lines', line: {{ color: palette.blue }}, yaxis: 'y2' }},
        {{ x, y: pick('precipitation'), name: 'Precip mm', type: 'bar', marker: {{ color: 'rgba(36,124,120,0.48)' }}, yaxis: 'y3' }},
        {{ x, y: pick('wind_gusts_10m'), name: 'Gust km/h', type: 'scatter', mode: 'lines', line: {{ color: palette.green, width: 1.6 }}, yaxis: 'y4' }}
      ], {{
        ...layoutBase,
        yaxis: {{ title: 'C' }},
        yaxis2: {{ title: '%', overlaying: 'y', side: 'right', range: [0, 100], showgrid: false }},
        yaxis3: {{ title: 'mm', overlaying: 'y', side: 'right', visible: false, rangemode: 'tozero' }},
        yaxis4: {{ title: 'km/h', overlaying: 'y', side: 'right', visible: false }}
      }}, plotConfig);
    }}

    function hourlyMeanByHour(year, key) {{
      const h = series[selectedPoint()][year].hourly;
      const buckets = Array.from({{ length: 24 }}, () => []);
      h.time.forEach((t, i) => {{
        const val = h[key][i];
        if (typeof val === 'number') buckets[Number(t.slice(11, 13))].push(val);
      }});
      return buckets.map(arr => arr.reduce((a, b) => a + b, 0) / Math.max(arr.length, 1));
    }}

    function renderDiurnalChart() {{
      const x = Array.from({{ length: 24 }}, (_, i) => `${{String(i).padStart(2, '0')}}:00`);
      const colors = ['#3867b7', '#d95d4f', '#247c78'];
      const traces = years.map((year, i) => ({{
        x,
        y: hourlyMeanByHour(year, 'temperature_2m'),
        name: `${{year}} temp`,
        type: 'scatter',
        mode: 'lines',
        line: {{ color: colors[i], width: 2.4 }}
      }}));
      traces.push(...years.map((year, i) => ({{
        x,
        y: hourlyMeanByHour(year, 'relative_humidity_2m'),
        name: `${{year}} humidity`,
        type: 'scatter',
        mode: 'lines',
        yaxis: 'y2',
        line: {{ color: colors[i], dash: 'dot', width: 1.8 }}
      }})));
      Plotly.react('diurnalChart', traces, {{
        ...layoutBase,
        yaxis: {{ title: 'Temperature C' }},
        yaxis2: {{ title: 'Humidity %', overlaying: 'y', side: 'right', range: [40, 100], showgrid: false }}
      }}, plotConfig);
    }}

    function renderHeatmap() {{
      const metric = heatMetric.value;
      const z = points.map(p => years.map(y => summaryByKey.get(`${{p.id}}-${{y}}`)[metric]));
      Plotly.react('heatmapChart', [{{
        z,
        x: years,
        y: points.map(p => `${{p.sample_km}} km · ${{p.name}}`),
        type: 'heatmap',
        colorscale: [[0, '#edf4f1'], [0.35, '#89b8a6'], [0.65, '#e3bd62'], [1, '#c74338']],
        colorbar: {{ title: metric.replaceAll('_', ' ') }},
        hovertemplate: '%{{y}}<br>%{{x}}<br>%{{z:.1f}}<extra></extra>'
      }}], {{
        ...layoutBase,
        margin: {{ l: 190, r: 24, t: 16, b: 42 }}
      }}, plotConfig);
    }}

    function renderRegimes() {{
      const r = regimes[selectedPoint()][selectedYear()];
      const labels = ['dry_stable', 'warm_wet', 'cold_wet_snow', 'wind_exposed', 'mixed'];
      const names = ['Dry stable', 'Warm wet', 'Cold wet/snow', 'Wind exposed', 'Mixed'];
      Plotly.react('regimeChart', [{{
        x: names,
        y: labels.map(k => r[k]),
        type: 'bar',
        marker: {{ color: ['#4f8f54', '#247c78', '#3867b7', '#c89225', '#8b9298'] }}
      }}], {{
        ...layoutBase,
        yaxis: {{ title: 'Days', rangemode: 'tozero' }},
        showlegend: false
      }}, plotConfig);
    }}

    function renderScatter() {{
      const h = payload().hourly;
      const step = 2;
      const idx = h.time.map((_, i) => i).filter(i => i % step === 0);
      Plotly.react('scatterChart', [{{
        x: idx.map(i => h.temperature_2m[i]),
        y: idx.map(i => h.relative_humidity_2m[i]),
        mode: 'markers',
        type: 'scattergl',
        text: idx.map(i => h.time[i]),
        marker: {{
          size: idx.map(i => Math.max(4, Math.min(18, 4 + (h.precipitation[i] || 0) * 5))),
          color: idx.map(i => h.precipitation[i] || 0),
          colorscale: [[0, '#dce7ef'], [0.45, '#247c78'], [1, '#d95d4f']],
          colorbar: {{ title: 'mm/h' }},
          opacity: 0.72
        }},
        hovertemplate: '%{{text}}<br>Temp %{{x:.1f}} C<br>Humidity %{{y:.0f}}%<extra></extra>'
      }}], {{
        ...layoutBase,
        xaxis: {{ title: 'Temperature C' }},
        yaxis: {{ title: 'Relative humidity %', range: [20, 105] }},
        showlegend: false
      }}, plotConfig);
    }}

    function renderPlanningTable() {{
      const d = payload().daily;
      const rows = d.time.map((date, i) => ({{
        date,
        tempMin: d.temperature_2m_min[i],
        tempMax: d.temperature_2m_max[i],
        precip: d.precipitation_sum[i],
        snow: d.snowfall_sum[i],
        gust: d.wind_gusts_10m_max[i],
        sunshine: (d.sunshine_duration[i] || 0) / 3600
      }}));
      const flagged = rows
        .filter(r => r.precip < 1 || r.precip >= 10 || r.tempMin <= 3 || r.gust >= 45)
        .sort((a, b) => {{
          const score = (b.precip >= 10) - (a.precip >= 10) || (b.gust >= 45) - (a.gust >= 45) || a.precip - b.precip;
          return score;
        }})
        .slice(0, 28);
      document.getElementById('planningTable').innerHTML = `
        <thead><tr><th>Date</th><th>Signal</th><th>Temp</th><th>Precip</th><th>Gust</th><th>Sun</th></tr></thead>
        <tbody>${{flagged.map(r => {{
          const signals = [];
          if (r.precip < 1) signals.push('<span class="pill">dry</span>');
          if (r.precip >= 10) signals.push('<span class="pill">heavy rain</span>');
          if (r.tempMin <= 3) signals.push('<span class="pill">cold start</span>');
          if (r.gust >= 45) signals.push('<span class="pill">wind</span>');
          if (r.snow > 0) signals.push('<span class="pill">snow</span>');
          return `<tr><td>${{r.date}}</td><td>${{signals.join(' ')}}</td><td>${{fmt(r.tempMin, 'C')}} / ${{fmt(r.tempMax, 'C')}}</td><td>${{fmt(r.precip, ' mm')}}</td><td>${{fmt(r.gust, ' km/h')}}</td><td>${{fmt(r.sunshine, ' h')}}</td></tr>`;
        }}).join('')}}</tbody>`;
    }}

    function downloadCsv() {{
      const blob = new Blob([''], {{ type: 'text/csv;charset=utf-8' }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'tmb_open_meteo_hourly_selected.csv';
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    }}

    function refreshAll() {{
      refreshDateBounds();
      renderKpis();
      renderMap();
      renderDailyChart();
      renderIntradayChart();
      renderDiurnalChart();
      renderHeatmap();
      renderRegimes();
      renderScatter();
      renderPlanningTable();
    }}

    initControls();
    refreshAll();
    pointSelect.addEventListener('change', refreshAll);
    yearSelect.addEventListener('change', refreshAll);
    dateSelect.addEventListener('change', () => {{ renderIntradayChart(); }});
    heatMetric.addEventListener('change', renderHeatmap);
    document.getElementById('downloadCsv').addEventListener('click', downloadCsv);
  </script>
</body>
</html>
"""


def build_html_modern(data: dict) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tour du Mont Blanc Weather Intelligence</title>
  <link rel="preconnect" href="https://cdn.plot.ly">
  <link rel="preconnect" href="https://unpkg.com">
  <link rel="preconnect" href="https://basemaps.cartocdn.com">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <link rel="stylesheet" href="assets/dashboard.css?v=20260529-hover-analog">
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
</head>
<body>
  <div class="shell">
    <header class="app-header">
      <div>
        <div class="eyebrow"><i data-lucide="compass"></i><span data-i18n="eyebrow">Outdoor Weather Intelligence</span></div>
        <h1 data-i18n="title">Tour du Mont Blanc Weather Intelligence</h1>
        <p data-i18n="subtitle">Hourly historical weather analytics for the classic TMB summer window, built for hikers planning timing, layers, rain strategy, and exposed-pass decisions.</p>
      </div>
      <div class="language-switch" role="group" aria-label="Language">
        <button class="lang-btn active" data-lang="en">EN</button>
        <button class="lang-btn" data-lang="zh">中文</button>
        <button class="lang-btn" data-lang="fr">FR</button>
        <button class="lang-btn" data-lang="it">IT</button>
        <button class="lang-btn" data-lang="de">DE</button>
      </div>
    </header>

    <main>
      <section class="control-panel" aria-label="Global controls">
        <div class="control-title">
          <i data-lucide="sliders-horizontal"></i>
          <div>
            <h2 data-i18n="controlTitle">Global route window</h2>
            <p data-i18n="controlHint">Choose your hiking year and start/end dates. Every aggregate view below follows this range.</p>
          </div>
        </div>
        <div class="controls-grid">
          <label><span data-i18n="point">Waypoint</span><select id="pointSelect"></select></label>
          <label class="reference-year-control">
            <div class="label-inline">
              <span data-i18n="year">Reference year</span>
              <span class="analog-hover">
                <button type="button" class="analog-trigger" aria-label="Recommended reference year" aria-describedby="analogPopover">
                  <i data-lucide="sparkles"></i>
                </button>
                <div id="analogPopover" class="analog-popover" role="tooltip">
                  <div class="analog-head">
                    <div>
                      <h2 data-i18n="analogTitle">Recommended reference year</h2>
                      <p data-i18n="analogHint">2026 latest route-season signal compared with historical reference years.</p>
                    </div>
                  </div>
                  <div id="analogTopList" class="analog-list"></div>
                  <div class="analog-meta">
                    <div><span data-i18n="confidence">Confidence</span><strong id="analogConfidence">n/a</strong></div>
                    <div><span data-i18n="forecast7d">7-day forecast</span><strong id="forecastSummary">n/a</strong></div>
                  </div>
                  <p class="analog-reason"><strong data-i18n="reason">Reason</strong>: <span id="analogReason">n/a</span></p>
                  <p class="analog-caveat"><strong data-i18n="caveat">Caveat</strong>: <span id="analogCaveat">n/a</span></p>
                </div>
              </span>
            </div>
            <select id="yearSelect"></select>
          </label>
          <label><span data-i18n="startDate">Start date</span><input id="rangeStart" type="text" inputmode="numeric" autocomplete="off"></label>
          <label><span data-i18n="endDate">End date</span><input id="rangeEnd" type="text" inputmode="numeric" autocomplete="off"></label>
          <label><span data-i18n="heatMetric">Route metric</span><select id="heatMetric"></select></label>
        </div>
      </section>

      <section class="kpi-grid" id="kpiGrid"></section>

      <section class="dashboard-grid top-layout">
        <article class="panel map-panel">
          <div class="panel-head">
            <div><h2 data-i18n="routeMap">Route Map</h2><p data-i18n="routeMapHint">Hover for waypoint names; click a marker to inspect that microclimate.</p></div>
          </div>
          <div id="map"></div>
        </article>
        <article class="panel">
          <div class="panel-head">
            <div><h2 data-i18n="dailyWindow">Daily Weather Window</h2><p data-i18n="dailyHint">Temperature range, precipitation, and gusts inside the global date window.</p></div>
          </div>
          <div id="dailyChart" class="chart"></div>
        </article>
      </section>

      <section class="dashboard-grid split-layout">
        <article class="panel">
          <div class="panel-head">
            <div><h2 data-i18n="intraday">Intraday Curve</h2><p data-i18n="intradayHint">Slide day by day through hourly temperature, humidity, precipitation, and gust exposure.</p></div>
            <div class="date-chip" id="intradayDateLabel"></div>
          </div>
          <div class="slider-row">
            <input id="dateSlider" type="range" min="0" max="0" value="0">
          </div>
          <div id="intradayChart" class="chart"></div>
        </article>
        <article class="panel">
          <div class="panel-head">
            <div><h2 data-i18n="diurnal">Diurnal Profile by Year</h2><p data-i18n="diurnalHint">Typical hourly pattern across the selected date window, compared by year.</p></div>
          </div>
          <div id="diurnalChart" class="chart"></div>
        </article>
      </section>

      <section class="dashboard-grid split-layout">
        <article class="panel">
          <div class="panel-head">
            <div><h2 data-i18n="heatmap">Route Risk Heatmap</h2><p data-i18n="heatmapHint">Compare waypoints and years using the same global date window.</p></div>
          </div>
          <div id="heatmapChart" class="chart tall-chart"></div>
        </article>
        <article class="panel">
          <div class="panel-head">
            <div><h2 data-i18n="regimes">Hourly Weather Regimes</h2><p data-i18n="regimeHint">Aggregated hourly classes, split into daytime and nighttime.</p></div>
          </div>
          <div id="regimeChart" class="chart tall-chart"></div>
        </article>
      </section>

      <section class="dashboard-grid split-layout">
        <article class="panel">
          <div class="panel-head">
            <div><h2 data-i18n="scatter">Temperature x Humidity</h2><p data-i18n="scatterHint">Hourly relationship; marker intensity reflects precipitation.</p></div>
          </div>
          <div id="scatterChart" class="chart"></div>
        </article>
        <article class="panel">
          <div class="panel-head">
            <div><h2 data-i18n="planning">Planning Signals</h2><p data-i18n="planningHint">Selected dates that deserve attention for dry windows, heavy rain, cold starts, or wind.</p></div>
          </div>
          <div class="table-wrap"><table id="planningTable"></table></div>
        </article>
      </section>

      <section class="download-strip">
        <div>
          <h2 data-i18n="downloadTitle">Data export</h2>
          <p data-i18n="downloadHint">Small utility export for the currently selected year and date range.</p>
        </div>
        <button id="downloadCsv"><i data-lucide="download"></i><span data-i18n="downloadCsv">Download CSV</span></button>
      </section>

      <p class="source-note"><span data-i18n="sourceNote">Data source: Open-Meteo Historical Weather and Forecast APIs. Sampling points are weather-analysis approximations, not navigation-grade GPX points. Always check current mountain forecasts and local safety notices before hiking.</span> <a href="https://open-meteo.com/en/docs/historical-weather-api?locale=en">Open-Meteo docs</a></p>
    </main>
  </div>

  <script src="assets/dashboard.js?v=20260529-hover-analog"></script>
</body>
</html>
"""


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    series_by_point: dict[str, dict[str, dict]] = {}
    summaries: list[dict] = []

    for point in POINTS:
        series_by_point[point["id"]] = {}
        for year in YEARS:
            cache_path = DATA_DIR / f"open_meteo_{point['id']}_{year}.json"
            if cache_path.exists():
                payload = json.loads(cache_path.read_text(encoding="utf-8"))
            else:
                print(f"Fetching {point['name']} {year}...")
                payload = api_request(point, year)
                cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                time.sleep(1.1)
            slim_payload = {
                "latitude": payload.get("latitude"),
                "longitude": payload.get("longitude"),
                "generationtime_ms": payload.get("generationtime_ms"),
                "utc_offset_seconds": payload.get("utc_offset_seconds"),
                "timezone": payload.get("timezone"),
                "elevation": payload.get("elevation"),
                "hourly_units": payload.get("hourly_units"),
                "daily_units": payload.get("daily_units"),
                "hourly": payload["hourly"],
                "daily": payload["daily"],
            }
            series_by_point[point["id"]][str(year)] = slim_payload
            summaries.append(summarize_point_year(point, year, slim_payload))

    add_risk_scores(summaries)
    data = {
        "metadata": {
            "title": "Tour du Mont Blanc Weather Analytics",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "api": API_URL,
            "source_docs": "https://open-meteo.com/en/docs/historical-weather-api?locale=en",
            "timezone": TIMEZONE,
        "periods": [f"{year}-{START_MONTH_DAY} to {year}-{END_MONTH_DAY}" for year in YEARS],
            "method_note": "Representative TMB weather sampling points, approximately every 8-12 km and at key microclimate locations; not a navigation-grade GPX track.",
        },
        "years": YEARS,
        "points": POINTS,
        "summaries": summaries,
        "weather_classes": derive_weather_classes(series_by_point),
        "series": series_by_point,
    }
    existing_path = PROCESSED_JSON if PROCESSED_JSON.exists() else LEGACY_PROCESSED_JSON
    if existing_path.exists():
        existing = json.loads(existing_path.read_text(encoding="utf-8"))
        for key in ("forecast_7d", "analog_reference"):
            if key in existing:
                data[key] = existing[key]
        if "2026" in existing.get("series", {}).get(POINTS[0]["id"], {}):
            if 2026 not in data["years"]:
                data["years"].append(2026)
            for point in POINTS:
                data["series"][point["id"]]["2026"] = existing["series"][point["id"]]["2026"]
            data["summaries"] = [item for item in data["summaries"] if item.get("year") != 2026]
            data["summaries"].extend(item for item in existing.get("summaries", []) if item.get("year") == 2026)
        if existing.get("metadata", {}).get("forecast_updated_at"):
            data["metadata"]["forecast_updated_at"] = existing["metadata"]["forecast_updated_at"]
        if existing.get("metadata", {}).get("forecast_source_docs"):
            data["metadata"]["forecast_source_docs"] = existing["metadata"]["forecast_source_docs"]
    HOURLY_CSV.write_text(
        flatten_csv(data["series"]), encoding="utf-8"
    )
    PROCESSED_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    DASHBOARD_PATH.write_text(build_html_modern(data), encoding="utf-8")
    print(f"Wrote {DASHBOARD_PATH}")
    print(f"Wrote {PROCESSED_JSON}")


if __name__ == "__main__":
    main()
