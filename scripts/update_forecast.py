#!/usr/bin/env python3
"""Update the TMB dashboard with latest 7-day forecast and analog year data."""

from __future__ import annotations

import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "tmb_weather_analytics_2022_2026.json"
LEGACY_DATA_PATH = ROOT / "data" / "tmb_weather_analytics_2022_2025.json"
HOURLY_CSV_PATH = ROOT / "data" / "tmb_open_meteo_hourly_2022_2026_available.csv"
RAW_FORECAST_DIR = ROOT / "data" / "forecast"
FORECAST_API = "https://api.open-meteo.com/v1/forecast"
FORECAST_DOCS = "https://open-meteo.com/en/docs"
TIMEZONE = "Europe/Paris"
ANALOG_YEAR = 2026
ROUTE_START = "06-01"
ROUTE_END = "07-31"
FORECAST_DAYS = 7
PAST_DAYS = 92

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


def request_json(url: str, params: dict[str, str | int | float]) -> dict:
    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(full_url, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            time.sleep(1.6 * (attempt + 1))
    raise RuntimeError(f"Open-Meteo request failed: {last_error}")


def fetch_point_forecast(point: dict) -> dict:
    params = {
        "latitude": point["lat"],
        "longitude": point["lon"],
        "hourly": ",".join(HOURLY_VARS),
        "daily": ",".join(DAILY_VARS),
        "timezone": TIMEZONE,
        "past_days": PAST_DAYS,
        "forecast_days": FORECAST_DAYS,
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }
    return request_json(FORECAST_API, params)


def load_dashboard_data() -> dict:
    path = DATA_PATH if DATA_PATH.exists() else LEGACY_DATA_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def values(items: list[float | int | None]) -> list[float]:
    return [float(x) for x in items if isinstance(x, (int, float)) and not math.isnan(float(x))]


def mean(items: list[float | int | None]) -> float | None:
    clean = values(items)
    return round(sum(clean) / len(clean), 2) if clean else None


def total(items: list[float | int | None]) -> float:
    return round(sum(values(items)), 2)


def max_value(items: list[float | int | None]) -> float | None:
    clean = values(items)
    return round(max(clean), 2) if clean else None


def month_day(date: str) -> str:
    return date[5:10]


def in_route_window(date: str) -> bool:
    return date.startswith(f"{ANALOG_YEAR}-") and ROUTE_START <= month_day(date) <= ROUTE_END


def slim_forecast_payload(payload: dict) -> dict:
    return {
        "latitude": payload.get("latitude"),
        "longitude": payload.get("longitude"),
        "generationtime_ms": payload.get("generationtime_ms"),
        "utc_offset_seconds": payload.get("utc_offset_seconds"),
        "timezone": payload.get("timezone"),
        "elevation": payload.get("elevation"),
        "hourly_units": payload.get("hourly_units"),
        "daily_units": payload.get("daily_units"),
        "data_status": "observed_to_date_plus_7d_forecast",
        "hourly": {"time": payload.get("hourly", {}).get("time", [])}
        | {key: payload.get("hourly", {}).get(key, []) for key in HOURLY_VARS},
        "daily": {"time": payload.get("daily", {}).get("time", [])}
        | {key: payload.get("daily", {}).get(key, []) for key in DAILY_VARS},
    }


def merge_time_payload(existing: dict | None, latest: dict) -> dict:
    if not existing:
        return latest

    merged = dict(latest)
    merged["data_status"] = "observed_to_date_plus_rolling_7d_forecast_accumulated"

    for section in ("hourly", "daily"):
        existing_section = existing.get(section, {})
        latest_section = latest.get(section, {})
        time_key = "time"
        all_times = sorted(set(existing_section.get(time_key, [])) | set(latest_section.get(time_key, [])))
        keys = sorted((set(existing_section) | set(latest_section)) - {time_key})
        merged_section = {time_key: all_times}

        for key in keys:
            values_by_time = {}
            for source in (existing_section, latest_section):
                times = source.get(time_key, [])
                values_for_key = source.get(key, [])
                for index, stamp in enumerate(times):
                    values_by_time[stamp] = values_for_key[index] if index < len(values_for_key) else None
            merged_section[key] = [values_by_time.get(stamp) for stamp in all_times]
        merged[section] = merged_section

    return merged


def summarize_point_year(point: dict, year: int, payload: dict) -> dict:
    hourly = payload["hourly"]
    daily = payload["daily"]
    precip_days = values(daily.get("precipitation_sum", []))
    temps = values(hourly.get("temperature_2m", []))
    gusts = values(hourly.get("wind_gusts_10m", []))
    wet_days = sum(1 for x in precip_days if x >= 1)
    heavy_days = sum(1 for x in precip_days if x >= 10)
    dry_days = sum(1 for x in precip_days if x < 1)
    sunshine = total(daily.get("sunshine_duration", []))
    return {
        "point_id": point["id"],
        "year": year,
        "data_status": payload.get("data_status"),
        "_hours": len(hourly.get("time", [])),
        "_daily_dates": daily.get("time", []),
        "mean_temp_c": mean(hourly.get("temperature_2m", [])),
        "mean_apparent_temp_c": mean(hourly.get("apparent_temperature", [])),
        "min_temp_c": round(min(temps), 2) if temps else None,
        "max_temp_c": round(max(temps), 2) if temps else None,
        "freeze_hours": sum(1 for x in temps if x <= 0),
        "cold_hours_lt5": sum(1 for x in temps if x < 5),
        "hot_hours_gt25": sum(1 for x in temps if x > 25),
        "mean_humidity_pct": mean(hourly.get("relative_humidity_2m", [])),
        "total_precip_mm": total(hourly.get("precipitation", [])),
        "total_rain_mm": total(hourly.get("rain", [])),
        "total_snow_cm": total(hourly.get("snowfall", [])),
        "wet_hours": sum(1 for x in values(hourly.get("precipitation", [])) if x >= 0.1),
        "wet_days": wet_days,
        "heavy_precip_days": heavy_days,
        "dry_days": dry_days,
        "mean_wind_kmh": mean(hourly.get("wind_speed_10m", [])),
        "max_gust_kmh": round(max(gusts), 2) if gusts else None,
        "mean_cloud_pct": mean(hourly.get("cloud_cover", [])),
        "sunshine_hours_total": round(sunshine / 3600, 1),
    }


def raw_risk(item: dict) -> float:
    days = max(len(set(item.get("_daily_dates", []))), 1) if "_daily_dates" in item else 61
    hours = max(item.get("_hours", 61 * 24), 1)
    return (
        item["wet_days"] / days * 35
        + item["heavy_precip_days"] / days * 25
        + item["cold_hours_lt5"] / hours * 20
        + min((item["max_gust_kmh"] or 0) / 80, 1) * 15
        + min(item["total_snow_cm"] / 20, 1) * 5
    )


def refresh_summaries(data: dict) -> None:
    existing = [item for item in data.get("summaries", []) if item.get("year") != ANALOG_YEAR]
    current = []
    for point in data["points"]:
        payload = data["series"][point["id"]][str(ANALOG_YEAR)]
        summary = summarize_point_year(point, ANALOG_YEAR, payload)
        summary["_raw_risk"] = raw_risk(summary)
        current.append(summary)
    if existing:
        historical_raw = []
        for item in existing:
            clone = dict(item)
            clone["_raw_risk"] = raw_risk(clone)
            historical_raw.append(clone)
        combined = historical_raw + current
        low = min(item["_raw_risk"] for item in combined)
        high = max(item["_raw_risk"] for item in combined)
        spread = high - low or 1
        for item in current:
            item["hiking_weather_risk"] = round(100 * (item.pop("_raw_risk") - low) / spread, 1)
            item.pop("_hours", None)
            item.pop("_daily_dates", None)
    else:
        for item in current:
            item.pop("_raw_risk", None)
            item.pop("_hours", None)
            item.pop("_daily_dates", None)
    data["summaries"] = existing + current


def point_day_features(point_id: str, point: dict, payload: dict) -> list[dict]:
    hourly = payload["hourly"]
    by_date: dict[str, list[int]] = defaultdict(list)
    for index, stamp in enumerate(hourly["time"]):
        by_date[stamp[:10]].append(index)

    daily = payload.get("daily", {})
    daily_dates = daily.get("time", sorted(by_date))
    rows = []
    for date in daily_dates:
        indices = by_date.get(date, [])
        daily_index = daily_dates.index(date)
        temps = [hourly["temperature_2m"][i] for i in indices]
        precip = [hourly["precipitation"][i] for i in indices]
        snow = [hourly["snowfall"][i] for i in indices]
        gusts = [hourly["wind_gusts_10m"][i] for i in indices]
        humidity = [hourly["relative_humidity_2m"][i] for i in indices]
        cold_hours = sum(1 for i in indices if hourly["temperature_2m"][i] is not None and hourly["temperature_2m"][i] < 5)
        row = {
            "point_id": point_id,
            "date": date,
            "month_day": month_day(date),
            "sample_km": point["sample_km"],
            "elevation_m": point["elevation_m"],
            "mean_temp_c": mean(temps),
            "mean_humidity_pct": mean(humidity),
            "total_precip_mm": total(precip),
            "total_snow_cm": total(snow),
            "max_gust_kmh": max_value(gusts),
            "cold_hours_lt5": cold_hours,
            "wet_hours": sum(1 for i in indices if (hourly["precipitation"][i] or 0) >= 0.1),
            "weather_code": daily.get("weather_code", [None] * len(daily_dates))[daily_index]
            if daily.get("weather_code")
            else None,
        }
        row["risk_score"] = round(
            min(row["total_precip_mm"] / 12, 1) * 32
            + min(row["max_gust_kmh"] or 0, 80) / 80 * 18
            + min(row["cold_hours_lt5"] / 12, 1) * 22
            + min(row["total_snow_cm"] / 8, 1) * 12
            + min(row["wet_hours"] / 12, 1) * 16,
            1,
        )
        rows.append(row)
    return rows


def historical_day_features(data: dict, point_id: str, year: int, md: str) -> dict | None:
    payload = data["series"][point_id][str(year)]
    date = f"{year}-{md}"
    daily = payload["daily"]
    try:
        daily_index = daily["time"].index(date)
    except ValueError:
        return None
    hourly = payload["hourly"]
    hourly_indices = [i for i, stamp in enumerate(hourly["time"]) if stamp.startswith(date)]
    return {
        "mean_temp_c": daily.get("temperature_2m_mean", [None])[daily_index],
        "mean_humidity_pct": daily.get("relative_humidity_2m_mean", [None])[daily_index],
        "total_precip_mm": daily["precipitation_sum"][daily_index] or 0,
        "total_snow_cm": daily["snowfall_sum"][daily_index] or 0,
        "max_gust_kmh": daily["wind_gusts_10m_max"][daily_index] or 0,
        "cold_hours_lt5": sum(
            1 for i in hourly_indices if hourly["temperature_2m"][i] is not None and hourly["temperature_2m"][i] < 5
        ),
    }


def feature_loss(current: dict, historical: dict) -> float:
    def diff(key: str, scale: float, weight: float) -> float:
        a = current.get(key)
        b = historical.get(key)
        if a is None or b is None:
            return 0
        return min(abs(float(a) - float(b)) / scale * weight, weight)

    return (
        diff("mean_temp_c", 8, 24)
        + diff("total_precip_mm", 25, 28)
        + diff("max_gust_kmh", 50, 18)
        + diff("cold_hours_lt5", 12, 16)
        + diff("mean_humidity_pct", 35, 8)
        + diff("total_snow_cm", 8, 6)
    )


def compare_analog_years(data: dict, latest_rows: list[dict], proxy_mode: bool = False) -> tuple[list[dict], dict]:
    years = [int(year) for year in data["years"] if int(year) < ANALOG_YEAR]
    points = {point["id"]: point for point in data["points"]}
    date_order = {date: index for index, date in enumerate(sorted({row["date"] for row in latest_rows}))}
    scored = []
    climatology_pairs = []

    for year in years:
        weighted_losses = []
        for row in latest_rows:
            md = row["month_day"]
            if proxy_mode:
                offset = date_order[row["date"]]
                md = f"06-{offset + 1:02d}"
            historical = historical_day_features(data, row["point_id"], year, md)
            if not historical:
                continue
            weight = 1.35 if points[row["point_id"]]["elevation_m"] >= 2000 else 1.0
            weighted_losses.append((feature_loss(row, historical), weight))
            climatology_pairs.append((row, historical))
        if weighted_losses:
            loss = sum(value * weight for value, weight in weighted_losses) / sum(weight for _, weight in weighted_losses)
            scored.append({"year": year, "similarity": round(max(0, min(100, 100 - loss)))})

    scored.sort(key=lambda item: (-item["similarity"], item["year"]))
    signals = derive_signals(climatology_pairs)
    return scored, signals


def derive_signals(pairs: list[tuple[dict, dict]]) -> dict:
    if not pairs:
        return {"precip_delta_pct": None, "temp_delta_c": None, "gust_delta_kmh": None}
    current_precip = mean([row["total_precip_mm"] for row, _ in pairs])
    normal_precip = mean([hist["total_precip_mm"] for _, hist in pairs])
    current_temp = mean([row["mean_temp_c"] for row, _ in pairs])
    normal_temp = mean([hist["mean_temp_c"] for _, hist in pairs])
    current_gust = mean([row["max_gust_kmh"] for row, _ in pairs])
    normal_gust = mean([hist["max_gust_kmh"] for _, hist in pairs])
    return {
        "precip_delta_pct": round((current_precip - normal_precip) / max(normal_precip, 0.1) * 100)
        if current_precip is not None and normal_precip is not None
        else None,
        "temp_delta_c": round(current_temp - normal_temp, 1)
        if current_temp is not None and normal_temp is not None
        else None,
        "gust_delta_kmh": round(current_gust - normal_gust, 1)
        if current_gust is not None and normal_gust is not None
        else None,
    }


def describe_signals(top_year: int | None, signals: dict, proxy_mode: bool) -> tuple[str, str]:
    precip = signals.get("precip_delta_pct")
    temp = signals.get("temp_delta_c")
    gust = signals.get("gust_delta_kmh")

    if precip is None:
        wetter_en, wetter_zh = "limited precipitation signal", "降水信号样本有限"
    elif precip >= 25:
        wetter_en, wetter_zh = "wetter than the same-date reference window", "比同日期参考窗口更湿"
    elif precip <= -25:
        wetter_en, wetter_zh = "drier than the same-date reference window", "比同日期参考窗口更干"
    else:
        wetter_en, wetter_zh = "near the same-date precipitation normal", "接近同日期降水常态"

    if temp is None:
        temp_en, temp_zh = "temperature signal is limited", "温度信号样本有限"
    elif temp >= 1.5:
        temp_en, temp_zh = f"{abs(temp):.1f}C warmer", f"偏暖 {abs(temp):.1f}C"
    elif temp <= -1.5:
        temp_en, temp_zh = f"{abs(temp):.1f}C cooler", f"偏冷 {abs(temp):.1f}C"
    else:
        temp_en, temp_zh = "temperature close to normal", "温度接近常态"

    if gust is None:
        wind_en, wind_zh = "gust signal is limited", "阵风信号样本有限"
    elif abs(gust) < 5:
        wind_en, wind_zh = "similar gust exposure", "阵风暴露相似"
    elif gust > 0:
        wind_en, wind_zh = "stronger gust exposure", "阵风暴露更强"
    else:
        wind_en, wind_zh = "lighter gust exposure", "阵风暴露更弱"

    mode_en = "using an early-season proxy alignment" if proxy_mode else "on available same-date route-season data"
    mode_zh = "采用早季代理对齐" if proxy_mode else "基于可用同日期路线季节数据"
    year_en = f"{top_year}" if top_year else "the top ranked year"
    year_zh = f"{top_year}" if top_year else "排名最高的年份"
    return (
        f"{ANALOG_YEAR} is {wetter_en}, with {temp_en} and {wind_en}; {year_en} is the closest aggregate analog {mode_en}.",
        f"{ANALOG_YEAR} {wetter_zh}，{temp_zh}，且{wind_zh}；{year_zh} 是{mode_zh}下最接近的综合参考年。",
    )


def confidence_for(unique_days: int, proxy_mode: bool) -> str:
    if proxy_mode or unique_days < 4:
        return "Low"
    if unique_days < 14:
        return "Medium"
    return "High"


def aggregate_route_future(rows: list[dict]) -> dict:
    by_date: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_date[row["date"]].append(row)
    route_daily = []
    for date, day_rows in sorted(by_date.items()):
        route_daily.append(
            {
                "date": date,
                "mean_temp_c": mean([row["mean_temp_c"] for row in day_rows]),
                "avg_point_precip_mm": mean([row["total_precip_mm"] for row in day_rows]),
                "max_point_precip_mm": max_value([row["total_precip_mm"] for row in day_rows]),
                "max_gust_kmh": max_value([row["max_gust_kmh"] for row in day_rows]),
                "cold_point_hours_lt5": sum(row["cold_hours_lt5"] for row in day_rows),
                "max_point_risk": max_value([row["risk_score"] for row in day_rows]),
            }
        )
    return {
        "daily": route_daily,
        "summary": {
            "days": len(route_daily),
            "mean_temp_c": mean([row["mean_temp_c"] for row in rows]),
            "avg_point_precip_mm": mean([row["total_precip_mm"] for row in rows]),
            "max_point_precip_mm": max_value([row["total_precip_mm"] for row in rows]),
            "max_gust_kmh": max_value([row["max_gust_kmh"] for row in rows]),
            "max_point_risk": max_value([row["risk_score"] for row in rows]),
        },
    }


def flatten_csv(data: dict) -> str:
    cols = [
        "point_id",
        "point_name",
        "year",
        "time",
        "temperature_2m",
        "relative_humidity_2m",
        "dew_point_2m",
        "apparent_temperature",
        "precipitation",
        "rain",
        "snowfall",
        "cloud_cover",
        "wind_speed_10m",
        "wind_direction_10m",
        "wind_gusts_10m",
        "surface_pressure",
        "weather_code",
        "is_day",
    ]
    rows = [",".join(cols)]
    for point in data["points"]:
        for year in data["years"]:
            payload = data["series"].get(point["id"], {}).get(str(year))
            if not payload:
                continue
            hourly = payload["hourly"]
            for index, stamp in enumerate(hourly.get("time", [])):
                rows.append(
                    ",".join(
                        [
                            point["id"],
                            '"' + point["name"].replace('"', '""') + '"',
                            str(year),
                            stamp,
                            *[str(hourly.get(col, [None] * len(hourly.get("time", [])))[index]) for col in cols[4:]],
                        ]
                    )
                )
    return "\n".join(rows) + "\n"


def build_updates(data: dict, point_payloads: dict[str, dict], generated_at: str) -> dict:
    all_rows = []
    future_rows = []
    per_point = {}
    for point in data["points"]:
        forecast_payload = slim_forecast_payload(point_payloads[point["id"]])
        existing_payload = data["series"].setdefault(point["id"], {}).get(str(ANALOG_YEAR))
        merged_payload = merge_time_payload(existing_payload, forecast_payload)
        data["series"][point["id"]][str(ANALOG_YEAR)] = merged_payload
        rows = point_day_features(point["id"], point, merged_payload)
        all_rows.extend(rows)
        future = rows[-FORECAST_DAYS:]
        future_rows.extend(future)
        per_point[point["id"]] = {"daily": future}

    if ANALOG_YEAR not in [int(year) for year in data.get("years", [])]:
        data["years"].append(ANALOG_YEAR)
    data["years"] = sorted(int(year) for year in data["years"])
    refresh_summaries(data)

    latest_route_rows = [row for row in all_rows if in_route_window(row["date"])]
    proxy_mode = False
    if not latest_route_rows:
        latest_route_rows = future_rows
        proxy_mode = True

    scored, signals = compare_analog_years(data, latest_route_rows, proxy_mode=proxy_mode)
    top_year = scored[0]["year"] if scored else None
    reason, reason_zh = describe_signals(top_year, signals, proxy_mode)
    unique_days = len({row["date"] for row in latest_route_rows})
    confidence = confidence_for(unique_days, proxy_mode)
    caveat = (
        "Based on observed-to-date and short-range forecast data inside the Jun-Jul route season; "
        "this is an analog guide, not a deterministic seasonal forecast."
        if not proxy_mode
        else "Current 7-day forecast has no Jun-Jul overlap, so the analog uses an early-season proxy alignment; interpret as low-confidence context only."
    )
    caveat_zh = (
        "基于 6-7 月路线季节内已观测至今与短期预报数据；这是相似年份参考，不是确定性的季节预报。"
        if not proxy_mode
        else "当前 7 日预报与 6-7 月窗口没有重叠，因此使用早季代理对齐；仅可作为低置信度背景参考。"
    )
    route_future = aggregate_route_future(future_rows)
    future_dates = sorted({row["date"] for row in future_rows})

    return {
        "forecast_7d": {
            "generated_at": generated_at,
            "api": FORECAST_API,
            "source_docs": FORECAST_DOCS,
            "timezone": TIMEZONE,
            "forecast_start": future_dates[0] if future_dates else None,
            "forecast_end": future_dates[-1] if future_dates else None,
            "points": per_point,
            "route": route_future,
        },
        "analog_reference": {
            "generated_at": generated_at,
            "year": ANALOG_YEAR,
            "method": "calendar_analog" if not proxy_mode else "early_season_proxy",
            "top": scored[:2],
            "confidence": confidence,
            "overlap_days": unique_days,
            "sample_point_days": len(latest_route_rows),
            "signals": signals,
            "reason": reason,
            "reason_zh": reason_zh,
            "caveat": caveat,
            "caveat_zh": caveat_zh,
        },
    }


def main() -> None:
    data = load_dashboard_data()
    RAW_FORECAST_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    point_payloads = {}

    for index, point in enumerate(data["points"], start=1):
        cache_path = RAW_FORECAST_DIR / f"open_meteo_forecast_{point['id']}.json"
        try:
            print(f"Fetching forecast {index:02d}/{len(data['points'])}: {point['name']}")
            payload = fetch_point_forecast(point)
            cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            time.sleep(0.25)
        except Exception:
            if not cache_path.exists():
                raise
            payload = json.loads(cache_path.read_text(encoding="utf-8"))
            print(f"Using cached forecast {index:02d}/{len(data['points'])}: {point['name']}")
        point_payloads[point["id"]] = payload

    updates = build_updates(data, point_payloads, generated_at)
    data.update(updates)
    data.setdefault("metadata", {})["forecast_updated_at"] = generated_at
    data["metadata"]["forecast_source_docs"] = FORECAST_DOCS
    data["metadata"]["current_year_note"] = (
        "2026 hourly data is observed-to-date plus the latest 7-day forecast. "
        "Full Jun-Jul 2026 historical data will only be available after the season."
    )
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    HOURLY_CSV_PATH.write_text(flatten_csv(data), encoding="utf-8")

    analog = updates["analog_reference"]
    top = ", ".join(f"{item['year']} {item['similarity']}/100" for item in analog["top"])
    print(f"Updated forecast_7d and analog_reference: {top} ({analog['confidence']})")


if __name__ == "__main__":
    main()
