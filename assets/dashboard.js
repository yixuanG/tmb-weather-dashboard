let DATA;
let points = [];
let years = [];
let series = {};

const pointNamesZh = {
  les_houches: "Les Houches村",
  col_de_voza: "Voza垭口 / Bellevue",
  les_contamines: "Les Contamines-Montjoie村",
  nant_borrant: "Nant Borrant山屋 / La Balme",
  croix_bonhomme: "Croix du Bonhomme垭口",
  les_chapieux: "Les Chapieux村",
  col_de_la_seigne: "Seigne垭口",
  rifugio_elisabetta: "Elisabetta山屋 / Val Veny",
  lac_combal: "Combal湖 / Combal小屋",
  courmayeur: "Courmayeur镇",
  rifugio_bertone: "Bertone山屋 / Mont de la Saxe",
  rifugio_bonatti: "Bonatti山屋 / Val Ferret",
  grand_col_ferret: "Grand Col Ferret垭口",
  la_fouly: "La Fouly村",
  champex_lac: "Champex-Lac湖村",
  trient: "Trient村 / Forclaz垭口",
  col_de_balme: "Balme垭口",
  lac_blanc_flegere: "Lac Blanc湖 / La Flegere",
  le_brevent: "Le Brevent山脊"
};

const terrainText = {
  en: {
    "valley trailhead": "valley trailhead",
    "ridge pass": "ridge pass",
    "valley village": "valley village",
    "upper valley refuge": "upper valley refuge",
    "high exposed pass": "high exposed pass",
    "valley hamlet": "valley hamlet",
    "border pass": "border pass",
    "glacier-facing refuge": "glacier-facing refuge",
    "high valley basin": "high valley basin",
    town: "town",
    "balcony ridge": "balcony ridge",
    "high valley refuge": "high valley refuge",
    "highest classic pass": "highest classic pass",
    "Swiss valley village": "Swiss valley village",
    "lake village": "lake village",
    "pass village": "pass village",
    "Aiguilles Rouges balcony": "Aiguilles Rouges balcony",
    "exposed ridge": "exposed ridge"
  },
  zh: {
    "valley trailhead": "谷地起点",
    "ridge pass": "山脊垭口",
    "valley village": "谷地村镇",
    "upper valley refuge": "高谷山屋",
    "high exposed pass": "高海拔暴露垭口",
    "valley hamlet": "谷地村落",
    "border pass": "边境垭口",
    "glacier-facing refuge": "冰川景观山屋",
    "high valley basin": "高谷盆地",
    town: "山镇",
    "balcony ridge": "景观山脊",
    "high valley refuge": "高谷山屋",
    "highest classic pass": "经典路线最高垭口",
    "Swiss valley village": "瑞士谷地村镇",
    "lake village": "湖畔村镇",
    "pass village": "垭口村镇",
    "Aiguilles Rouges balcony": "Aiguilles Rouges景观线",
    "exposed ridge": "暴露山脊"
  },
  fr: {},
  it: {},
  de: {}
};
terrainText.fr = terrainText.en;
terrainText.it = terrainText.en;
terrainText.de = terrainText.en;

const I18N = {
  en: {
    eyebrow: "Outdoor Weather Intelligence",
    title: "Tour du Mont Blanc Weather Intelligence",
    subtitle: "Hourly historical weather analytics for the classic TMB summer window, built for hikers planning timing, layers, rain strategy, and exposed-pass decisions.",
    controlTitle: "Global route window",
    controlHint: "Choose a reference weather year and start/end dates. Every aggregate view below follows this range.",
    point: "Waypoint",
    year: "Reference year",
    startDate: "Start date",
    endDate: "End date",
    heatMetric: "Route metric",
    routeMap: "Route Map",
    routeMapHint: "Hover for waypoint names; click a marker to inspect that microclimate.",
    dailyWindow: "Daily Weather Window",
    dailyHint: "Temperature range, precipitation, and gusts inside the global date window.",
    intraday: "Intraday Curve",
    intradayHint: "Slide day by day through hourly temperature, humidity, precipitation, and gust exposure.",
    diurnal: "Diurnal Profile by Year",
    diurnalHint: "Typical hourly pattern across the selected date window, compared by year.",
    heatmap: "Route Risk Heatmap",
    heatmapHint: "Compare waypoints and years using the same global date window.",
    regimes: "Hourly Weather Regimes",
    regimeHint: "Aggregated hourly classes, split into daytime and nighttime.",
    scatter: "Temperature x Humidity",
    scatterHint: "Hourly relationship; marker intensity reflects precipitation.",
    planning: "Planning Signals",
    planningHint: "Selected dates that deserve attention for dry windows, heavy rain, cold starts, or wind.",
    downloadTitle: "Data export",
    downloadHint: "Small utility export for the currently selected year and date range.",
    downloadCsv: "Download CSV",
    sourceNote: "Data source: Open-Meteo Historical Weather API. Sampling points are weather-analysis approximations, not navigation-grade GPX points. Always check current mountain forecasts and local safety notices before hiking.",
    temp: "Mean temp",
    precip: "Precipitation",
    wetDays: "Wet days",
    risk: "Weather risk",
    cold: "Cold hours",
    gust: "Max gust",
    humidity: "Humidity",
    day: "Day",
    night: "Night",
    hours: "hours",
    dryStable: "Dry stable",
    warmWet: "Warm wet",
    coldWetSnow: "Cold wet / snow",
    windExposed: "Wind exposed",
    mixed: "Mixed",
    dry: "dry",
    heavyRain: "heavy rain",
    coldStart: "cold start",
    wind: "wind",
    snow: "snow",
    signal: "Signal",
    date: "Date",
    sun: "Sun",
    allWaypoints: "all waypoints"
  },
  zh: {
    eyebrow: "Outdoor Weather Intelligence",
    title: "环勃朗峰徒步气象智能看板",
    subtitle: "基于小时级历史天气数据，服务于 TMB 夏季徒步的时间窗口、穿衣、防雨和暴露山口决策。",
    controlTitle: "全局环线时间窗口",
    controlHint: "选择参考年份、开始日期和结束日期。下方所有汇总视图都会跟随这个范围。",
    point: "点位",
    year: "参考年份",
    startDate: "开始日期",
    endDate: "结束日期",
    heatMetric: "路线指标",
    routeMap: "路线地图",
    routeMapHint: "鼠标悬停显示点位名称；点击标记切换微气候点位。",
    dailyWindow: "每日天气窗口",
    dailyHint: "全局日期范围内的温度区间、降水和阵风。",
    intraday: "日内小时曲线",
    intradayHint: "拖动日期滑块，逐日查看温度、湿度、降水和阵风暴露。",
    diurnal: "跨年份日内典型曲线",
    diurnalHint: "在选定日期范围内按小时聚合，对比不同年份的典型日内节律。",
    heatmap: "路线风险热力图",
    heatmapHint: "按相同全局日期范围比较点位与年份。",
    regimes: "小时级天气状态",
    regimeHint: "小时级天气分类聚合，并区分日间与夜间。",
    scatter: "温度 x 湿度",
    scatterHint: "小时级关系图；点的颜色和强度反映降水。",
    planning: "徒步准备信号",
    planningHint: "筛选值得关注的干燥窗口、强降水、低温清晨或大风日期。",
    downloadTitle: "数据导出",
    downloadHint: "轻量工具：导出当前年份和日期范围的数据。",
    downloadCsv: "下载 CSV",
    sourceNote: "数据源：Open-Meteo Historical Weather API。采样点用于气象分析近似，不是导航级 GPX 点。出行前请务必查看最新山区预报和当地安全公告。",
    temp: "平均气温",
    precip: "降水量",
    wetDays: "湿天",
    risk: "天气风险",
    cold: "低温小时",
    gust: "最大阵风",
    humidity: "湿度",
    day: "日间",
    night: "夜间",
    hours: "小时",
    dryStable: "干燥稳定",
    warmWet: "温暖潮湿",
    coldWetSnow: "寒冷湿雪",
    windExposed: "大风暴露",
    mixed: "混合天气",
    dry: "干燥",
    heavyRain: "强降水",
    coldStart: "低温清晨",
    wind: "大风",
    snow: "降雪",
    signal: "信号",
    date: "日期",
    sun: "日照",
    allWaypoints: "所有点位"
  },
  fr: {
    eyebrow: "Outdoor Weather Intelligence",
    title: "Meteo Intelligence du Tour du Mont Blanc",
    subtitle: "Analyse meteo horaire historique pour la fenetre estivale classique du TMB: timing, couches, pluie et passages exposes.",
    controlTitle: "Fenetre globale de route",
    controlHint: "Choisissez l'annee de reference, la date de depart et la date de fin. Toutes les vues agregees suivent cette plage.",
    point: "Point",
    year: "Annee de reference",
    startDate: "Depart",
    endDate: "Fin",
    heatMetric: "Indicateur",
    routeMap: "Carte de route",
    routeMapHint: "Survolez les points; cliquez pour inspecter un microclimat.",
    dailyWindow: "Fenetre meteo quotidienne",
    dailyHint: "Temperature, precipitation et rafales dans la plage choisie.",
    intraday: "Courbe intrajournaliere",
    intradayHint: "Faites glisser la date pour voir les courbes horaires.",
    diurnal: "Profil journalier par annee",
    diurnalHint: "Profil horaire type sur la plage choisie, compare par annee.",
    heatmap: "Carte thermique du risque",
    heatmapHint: "Comparez points et annees avec la meme plage de dates.",
    regimes: "Regimes horaires",
    regimeHint: "Classes horaires agregees, separees jour et nuit.",
    scatter: "Temperature x humidite",
    scatterHint: "Relation horaire; l'intensite indique la precipitation.",
    planning: "Signaux de preparation",
    planningHint: "Dates a surveiller: sec, forte pluie, froid ou vent.",
    downloadTitle: "Export",
    downloadHint: "Export simple pour l'annee et la plage choisies.",
    downloadCsv: "Telecharger CSV",
    sourceNote: "Source: Open-Meteo Historical Weather API. Les points sont des approximations analytiques, pas des points GPX de navigation.",
    temp: "Temp. moyenne",
    precip: "Precipitation",
    wetDays: "Jours humides",
    risk: "Risque meteo",
    cold: "Heures froides",
    gust: "Rafale max",
    humidity: "Humidite",
    day: "Jour",
    night: "Nuit",
    hours: "heures",
    dryStable: "Sec stable",
    warmWet: "Doux humide",
    coldWetSnow: "Froid humide / neige",
    windExposed: "Vent expose",
    mixed: "Mixte",
    dry: "sec",
    heavyRain: "forte pluie",
    coldStart: "depart froid",
    wind: "vent",
    snow: "neige",
    signal: "Signal",
    date: "Date",
    sun: "Soleil",
    allWaypoints: "tous les points"
  },
  it: {
    eyebrow: "Outdoor Weather Intelligence",
    title: "Meteo Intelligence del Tour du Mont Blanc",
    subtitle: "Analisi meteo oraria storica per la finestra estiva del TMB: orari, abbigliamento, pioggia e passaggi esposti.",
    controlTitle: "Finestra globale del percorso",
    controlHint: "Scegli l'anno di riferimento, la data iniziale e finale. Tutte le viste aggregate seguono questo intervallo.",
    point: "Punto",
    year: "Anno di riferimento",
    startDate: "Inizio",
    endDate: "Fine",
    heatMetric: "Metrica",
    routeMap: "Mappa del percorso",
    routeMapHint: "Passa sopra ai punti; clicca per ispezionare un microclima.",
    dailyWindow: "Finestra meteo giornaliera",
    dailyHint: "Temperatura, precipitazioni e raffiche nell'intervallo scelto.",
    intraday: "Curva intragiornaliera",
    intradayHint: "Scorri la data per vedere le curve orarie.",
    diurnal: "Profilo diurno per anno",
    diurnalHint: "Profilo orario tipico nell'intervallo scelto, confrontato per anno.",
    heatmap: "Heatmap del rischio",
    heatmapHint: "Confronta punti e anni con lo stesso intervallo.",
    regimes: "Regimi orari",
    regimeHint: "Classi orarie aggregate, divise tra giorno e notte.",
    scatter: "Temperatura x umidita",
    scatterHint: "Relazione oraria; l'intensita indica la precipitazione.",
    planning: "Segnali di pianificazione",
    planningHint: "Date da notare: asciutto, pioggia intensa, freddo o vento.",
    downloadTitle: "Export dati",
    downloadHint: "Export semplice per anno e intervallo selezionati.",
    downloadCsv: "Scarica CSV",
    sourceNote: "Fonte: Open-Meteo Historical Weather API. I punti sono approssimazioni analitiche, non punti GPX di navigazione.",
    temp: "Temp. media",
    precip: "Precipitazione",
    wetDays: "Giorni piovosi",
    risk: "Rischio meteo",
    cold: "Ore fredde",
    gust: "Raffica max",
    humidity: "Umidita",
    day: "Giorno",
    night: "Notte",
    hours: "ore",
    dryStable: "Secco stabile",
    warmWet: "Caldo umido",
    coldWetSnow: "Freddo umido / neve",
    windExposed: "Vento esposto",
    mixed: "Misto",
    dry: "secco",
    heavyRain: "pioggia forte",
    coldStart: "partenza fredda",
    wind: "vento",
    snow: "neve",
    signal: "Segnale",
    date: "Data",
    sun: "Sole",
    allWaypoints: "tutti i punti"
  },
  de: {
    eyebrow: "Outdoor Weather Intelligence",
    title: "Wetter-Intelligence fur den Tour du Mont Blanc",
    subtitle: "Historische stuendliche Wetteranalyse fuer das klassische TMB-Sommerfenster: Timing, Kleidung, Regen und exponierte Paesse.",
    controlTitle: "Globales Routenfenster",
    controlHint: "Referenzjahr, Start- und Enddatum waehlen. Alle aggregierten Ansichten folgen diesem Zeitraum.",
    point: "Punkt",
    year: "Referenzjahr",
    startDate: "Start",
    endDate: "Ende",
    heatMetric: "Metrik",
    routeMap: "Routenkarte",
    routeMapHint: "Punkte mit der Maus beruehren; klicken, um ein Mikroklima zu pruefen.",
    dailyWindow: "Taegliches Wetterfenster",
    dailyHint: "Temperatur, Niederschlag und Boeen im ausgewaehlten Zeitraum.",
    intraday: "Tageskurve",
    intradayHint: "Datum verschieben, um stuendliche Kurven zu sehen.",
    diurnal: "Tagesprofil nach Jahr",
    diurnalHint: "Typisches Stundenprofil im Zeitraum, nach Jahr verglichen.",
    heatmap: "Risiko-Heatmap",
    heatmapHint: "Punkte und Jahre mit demselben Zeitraum vergleichen.",
    regimes: "Stuendliche Wetterlagen",
    regimeHint: "Aggregierte Stundenklassen, getrennt nach Tag und Nacht.",
    scatter: "Temperatur x Feuchte",
    scatterHint: "Stuendliche Beziehung; Intensitaet zeigt Niederschlag.",
    planning: "Planungssignale",
    planningHint: "Auffaellige Tage: trocken, Starkregen, kalt oder windig.",
    downloadTitle: "Datenexport",
    downloadHint: "Einfacher Export fuer gewaehltes Jahr und Datum.",
    downloadCsv: "CSV herunterladen",
    sourceNote: "Quelle: Open-Meteo Historical Weather API. Punkte sind analytische Naeherungen, keine GPX-Navigationspunkte.",
    temp: "Mittl. Temp.",
    precip: "Niederschlag",
    wetDays: "Nasse Tage",
    risk: "Wetterrisiko",
    cold: "Kalte Stunden",
    gust: "Max. Boee",
    humidity: "Feuchte",
    day: "Tag",
    night: "Nacht",
    hours: "Stunden",
    dryStable: "Trocken stabil",
    warmWet: "Warm feucht",
    coldWetSnow: "Kalt nass / Schnee",
    windExposed: "Wind exponiert",
    mixed: "Gemischt",
    dry: "trocken",
    heavyRain: "Starkregen",
    coldStart: "kalter Start",
    wind: "Wind",
    snow: "Schnee",
    signal: "Signal",
    date: "Datum",
    sun: "Sonne",
    allWaypoints: "alle Punkte"
  }
};

const metricOptions = [
  ["hiking_weather_risk", "risk"],
  ["total_precip_mm", "precip"],
  ["wet_days", "wetDays"],
  ["cold_hours_lt5", "cold"],
  ["max_gust_kmh", "gust"]
];

const weekdayLabels = {
  en: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
  zh: ["周日", "周一", "周二", "周三", "周四", "周五", "周六"],
  fr: ["dim.", "lun.", "mar.", "mer.", "jeu.", "ven.", "sam."],
  it: ["dom", "lun", "mar", "mer", "gio", "ven", "sab"],
  de: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"]
};

const colors = {
  emerald: "#24d39a",
  teal: "#2dd4bf",
  sky: "#38bdf8",
  amber: "#f5b84b",
  rose: "#fb7185",
  violet: "#a78bfa",
  muted: "#8fa2af",
  grid: "rgba(148,163,184,0.14)",
  text: "#eef6f6",
  panel: "rgba(0,0,0,0)"
};

const state = {
  lang: "en",
  pointId: "grand_col_ferret",
  year: "",
  startDate: "",
  endDate: "",
  intradayDate: "",
  heatMetric: "hiking_weather_risk"
};

const $ = (id) => document.getElementById(id);
let pointById = new Map();
const plotConfig = { responsive: true, displayModeBar: false };

function t(key) {
  return I18N[state.lang][key] || I18N.en[key] || key;
}

function pointName(point) {
  if (state.lang === "zh") return pointNamesZh[point.id] || point.name;
  return point.name;
}

function terrain(point) {
  return (terrainText[state.lang] && terrainText[state.lang][point.terrain]) || point.terrain;
}

function fmt(value, suffix = "", digits = 1) {
  if (value === null || value === undefined || Number.isNaN(value)) return "n/a";
  return `${Number(value).toFixed(digits)}${suffix}`;
}

function mean(arr) {
  const values = arr.filter((x) => typeof x === "number" && !Number.isNaN(x));
  return values.length ? values.reduce((a, b) => a + b, 0) / values.length : null;
}

function sum(arr) {
  return arr.filter((x) => typeof x === "number").reduce((a, b) => a + b, 0);
}

function monthDay(date) {
  return date.slice(5, 10);
}

function withYear(year, date) {
  return `${year}-${monthDay(date)}`;
}

function isValidIsoDate(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [year, month, day] = value.split("-").map(Number);
  const parsed = new Date(Date.UTC(year, month - 1, day));
  return (
    parsed.getUTCFullYear() === year &&
    parsed.getUTCMonth() === month - 1 &&
    parsed.getUTCDate() === day
  );
}

function formatDateLabel(date) {
  const labels = weekdayLabels[state.lang] || weekdayLabels.en;
  const [year, month, dayOfMonth] = date.split("-").map(Number);
  const day = new Date(Date.UTC(year, month - 1, dayOfMonth)).getUTCDay();
  return `${date} (${labels[day]})`;
}

function parseDateInput(raw, fallback) {
  const cleaned = raw.trim().replace(/[().,，]/g, " ").replace(/\s+/g, " ");
  const full = cleaned.match(/(\d{4})[-/](\d{1,2})[-/](\d{1,2})/);
  const partial = cleaned.match(/(?:^|\s)(\d{1,2})[-/](\d{1,2})(?:\s|$)/);
  let year = state.year;
  let month;
  let day;

  if (full) {
    if (years.includes(full[1])) year = full[1];
    month = full[2];
    day = full[3];
  } else if (partial) {
    month = partial[1];
    day = partial[2];
  } else {
    return fallback;
  }

  const candidate = `${year}-${String(Number(month)).padStart(2, "0")}-${String(Number(day)).padStart(2, "0")}`;
  if (!isValidIsoDate(candidate)) return fallback;
  if (monthDay(candidate) < "06-01" || monthDay(candidate) > "07-31") return fallback;
  state.year = year;
  return candidate;
}

function clampRange() {
  const min = `${state.year}-06-01`;
  const max = `${state.year}-07-31`;
  if (!state.startDate) state.startDate = min;
  if (!state.endDate) state.endDate = max;
  state.startDate = `${state.year}-${monthDay(state.startDate)}`;
  state.endDate = `${state.year}-${monthDay(state.endDate)}`;
  if (state.startDate < min) state.startDate = min;
  if (state.endDate > max) state.endDate = max;
  if (state.startDate > state.endDate) state.endDate = state.startDate;
}

function rangeForYear(year) {
  return [withYear(year, state.startDate), withYear(year, state.endDate)];
}

function dailyIndices(pointId, year) {
  const [start, end] = rangeForYear(year);
  return series[pointId][year].daily.time
    .map((date, index) => ({ date, index }))
    .filter((d) => d.date >= start && d.date <= end);
}

function hourlyIndices(pointId, year) {
  const [start, end] = rangeForYear(year);
  return series[pointId][year].hourly.time
    .map((time, index) => ({ time, index, date: time.slice(0, 10), hour: Number(time.slice(11, 13)) }))
    .filter((d) => d.date >= start && d.date <= end);
}

function summarize(pointId, year) {
  const payload = series[pointId][year];
  const hourly = payload.hourly;
  const daily = payload.daily;
  const hIdx = hourlyIndices(pointId, year).map((d) => d.index);
  const dIdx = dailyIndices(pointId, year).map((d) => d.index);
  const temps = hIdx.map((i) => hourly.temperature_2m[i]).filter((x) => typeof x === "number");
  const gusts = hIdx.map((i) => hourly.wind_gusts_10m[i]).filter((x) => typeof x === "number");
  const precipDays = dIdx.map((i) => daily.precipitation_sum[i] || 0);
  const hours = Math.max(hIdx.length, 1);
  const days = Math.max(dIdx.length, 1);
  const coldHours = hIdx.filter((i) => hourly.temperature_2m[i] < 5).length;
  const heavyDays = precipDays.filter((x) => x >= 10).length;
  const wetDays = precipDays.filter((x) => x >= 1).length;
  const totalSnow = sum(hIdx.map((i) => hourly.snowfall[i] || 0));
  const maxGust = gusts.length ? Math.max(...gusts) : 0;
  const rawRisk =
    (wetDays / days) * 35 +
    (heavyDays / days) * 25 +
    (coldHours / hours) * 20 +
    Math.min(maxGust / 80, 1) * 15 +
    Math.min(totalSnow / 20, 1) * 5;

  return {
    point_id: pointId,
    year,
    days,
    hours: hIdx.length,
    mean_temp_c: mean(hIdx.map((i) => hourly.temperature_2m[i])),
    mean_apparent_temp_c: mean(hIdx.map((i) => hourly.apparent_temperature[i])),
    mean_humidity_pct: mean(hIdx.map((i) => hourly.relative_humidity_2m[i])),
    total_precip_mm: sum(hIdx.map((i) => hourly.precipitation[i] || 0)),
    total_snow_cm: totalSnow,
    wet_days: wetDays,
    heavy_precip_days: heavyDays,
    dry_days: precipDays.filter((x) => x < 1).length,
    cold_hours_lt5: coldHours,
    freeze_hours: hIdx.filter((i) => hourly.temperature_2m[i] <= 0).length,
    max_gust_kmh: maxGust,
    hiking_weather_risk: Math.max(0, Math.min(100, rawRisk))
  };
}

function classifyHour(hourly, i) {
  const temp = hourly.temperature_2m[i];
  const precip = hourly.precipitation[i] || 0;
  const snow = hourly.snowfall[i] || 0;
  const gust = hourly.wind_gusts_10m[i] || 0;
  if (snow > 0 || (precip >= 0.1 && temp <= 3)) return "coldWetSnow";
  if (gust >= 45) return "windExposed";
  if (precip >= 0.1 && temp > 8) return "warmWet";
  if (precip < 0.1 && gust < 35 && temp >= 8) return "dryStable";
  return "mixed";
}

function layout(extra = {}) {
  return {
    margin: { l: 48, r: 24, t: 10, b: 42 },
    paper_bgcolor: colors.panel,
    plot_bgcolor: colors.panel,
    font: { family: "Inter, system-ui, sans-serif", color: colors.text },
    hoverlabel: { bgcolor: "#0b1720", bordercolor: "rgba(148,163,184,0.28)", font: { color: colors.text } },
    legend: { orientation: "h", y: 1.12, x: 0, font: { color: colors.muted } },
    xaxis: { gridcolor: colors.grid, zeroline: false, tickfont: { color: colors.muted } },
    yaxis: { gridcolor: colors.grid, zeroline: false, tickfont: { color: colors.muted } },
    hovermode: "x unified",
    ...extra
  };
}

function heatColor(risk) {
  if (risk >= 70) return "#fb7185";
  if (risk >= 45) return "#f5b84b";
  if (risk >= 25) return "#2dd4bf";
  return "#24d39a";
}

function syncI18n() {
  document.documentElement.lang = state.lang === "zh" ? "zh-CN" : state.lang;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.lang === state.lang);
  });
  if (window.lucide) window.lucide.createIcons();
}

function fillControls() {
  $("pointSelect").innerHTML = points
    .map((p) => `<option value="${p.id}">${String(p.sample_km).padStart(3, "0")} km · ${pointName(p)}</option>`)
    .join("");
  $("pointSelect").value = state.pointId;
  $("yearSelect").innerHTML = years.map((year) => `<option value="${year}">${year}</option>`).join("");
  $("yearSelect").value = state.year;
  $("heatMetric").innerHTML = metricOptions
    .map(([value, label]) => `<option value="${value}">${t(label)}</option>`)
    .join("");
  $("heatMetric").value = state.heatMetric;
  $("rangeStart").placeholder = `${state.year}-06-01`;
  $("rangeEnd").placeholder = `${state.year}-07-31`;
  $("rangeStart").value = formatDateLabel(state.startDate);
  $("rangeEnd").value = formatDateLabel(state.endDate);
}

function availableDates() {
  return dailyIndices(state.pointId, state.year).map((d) => d.date);
}

function resetIntradayToStart() {
  state.intradayDate = state.startDate;
}

function syncSlider() {
  const dates = availableDates();
  if (!dates.length) return;
  if (!dates.includes(state.intradayDate)) state.intradayDate = dates[0];
  $("dateSlider").min = 0;
  $("dateSlider").max = Math.max(dates.length - 1, 0);
  $("dateSlider").value = dates.indexOf(state.intradayDate);
  $("intradayDateLabel").textContent = formatDateLabel(state.intradayDate);
}

function renderKpis() {
  const point = pointById.get(state.pointId);
  const s = summarize(state.pointId, state.year);
  const items = [
    [pointName(point), `${point.elevation_m} m · ${terrain(point)}`, "map-pin"],
    [fmt(s.mean_temp_c, "C"), `${t("humidity")} ${fmt(s.mean_humidity_pct, "%")}`, "thermometer"],
    [fmt(s.total_precip_mm, " mm"), `${s.wet_days} ${t("wetDays")} · ${s.heavy_precip_days} heavy`, "cloud-rain"],
    [`${Math.round(s.hiking_weather_risk)}/100`, `${t("gust")} ${fmt(s.max_gust_kmh, " km/h")}`, "shield-alert"]
  ];
  $("kpiGrid").innerHTML = items
    .map(([value, hint, icon], index) => {
      const labels = [t("point"), t("temp"), t("precip"), t("risk")];
      return `<div class="kpi"><span><i data-lucide="${icon}"></i>${labels[index]}</span><strong>${value}</strong><small>${hint}</small></div>`;
    })
    .join("");
  if (window.lucide) window.lucide.createIcons();
}

let map;
let markers = [];
function renderMap() {
  if (!map) {
    map = L.map("map", { scrollWheelZoom: false, zoomControl: true }).setView([45.91, 6.93], 10);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      maxZoom: 14,
      attribution: "&copy; OpenStreetMap &copy; CARTO"
    }).addTo(map);
    const route = L.polyline(points.map((p) => [p.lat, p.lon]), {
      color: colors.emerald,
      weight: 3,
      opacity: 0.72
    }).addTo(map);
    map.fitBounds(route.getBounds().pad(0.12));
  }
  markers.forEach((marker) => marker.remove());
  markers = points.map((p) => {
    const s = summarize(p.id, state.year);
    const marker = L.circleMarker([p.lat, p.lon], {
      radius: p.id === state.pointId ? 9 : 6,
      color: "rgba(238,246,246,0.9)",
      weight: 2,
      fillColor: heatColor(s.hiking_weather_risk),
      fillOpacity: 0.9
    }).addTo(map);
    const name = pointName(p);
    marker.bindTooltip(name, { direction: "top", className: "tmb-tooltip", sticky: true });
    marker.bindPopup(`<b>${name}</b><br>${p.elevation_m} m · km ${p.sample_km}<br>${t("risk")} ${fmt(s.hiking_weather_risk, "", 0)}/100`);
    marker.on("click", () => {
      state.pointId = p.id;
      fillControls();
      refreshAll(false);
    });
    return marker;
  });
}

function renderDailyChart() {
  const payload = series[state.pointId][state.year];
  const d = payload.daily;
  const idx = dailyIndices(state.pointId, state.year).map((x) => x.index);
  const x = idx.map((i) => d.time[i]);
  Plotly.react(
    "dailyChart",
    [
      { x, y: idx.map((i) => d.temperature_2m_max[i]), name: "T max C", type: "scatter", mode: "lines", line: { color: colors.rose, width: 3, shape: "spline" } },
      { x, y: idx.map((i) => d.temperature_2m_min[i]), name: "T min C", type: "scatter", mode: "lines", line: { color: colors.sky, width: 3, shape: "spline" } },
      { x, y: idx.map((i) => d.precipitation_sum[i]), name: `${t("precip")} mm`, type: "bar", marker: { color: "rgba(45,212,191,0.42)" }, yaxis: "y2" },
      { x, y: idx.map((i) => d.wind_gusts_10m_max[i]), name: `${t("gust")} km/h`, type: "scatter", mode: "lines", line: { color: colors.amber, width: 2, dash: "dot" }, yaxis: "y3" }
    ],
    layout({
      yaxis: { title: "C", gridcolor: colors.grid, zeroline: false },
      yaxis2: { title: "mm", overlaying: "y", side: "right", rangemode: "tozero", showgrid: false },
      yaxis3: { overlaying: "y", side: "right", visible: false, showgrid: false }
    }),
    plotConfig
  );
}

function renderIntradayChart() {
  const payload = series[state.pointId][state.year];
  const h = payload.hourly;
  const idx = h.time.map((time, index) => ({ time, index })).filter((d) => d.time.startsWith(state.intradayDate)).map((d) => d.index);
  const x = idx.map((i) => h.time[i].slice(11, 16));
  Plotly.react(
    "intradayChart",
    [
      { x, y: idx.map((i) => h.temperature_2m[i]), name: "Temp C", type: "scatter", mode: "lines", line: { color: colors.rose, width: 3, shape: "spline" } },
      { x, y: idx.map((i) => h.relative_humidity_2m[i]), name: `${t("humidity")} %`, type: "scatter", mode: "lines", line: { color: colors.sky, width: 2 }, yaxis: "y2" },
      { x, y: idx.map((i) => h.precipitation[i]), name: `${t("precip")} mm`, type: "bar", marker: { color: "rgba(45,212,191,0.48)" }, yaxis: "y3" },
      { x, y: idx.map((i) => h.wind_gusts_10m[i]), name: `${t("gust")} km/h`, type: "scatter", mode: "lines", line: { color: colors.amber, width: 2 }, yaxis: "y4" }
    ],
    layout({
      yaxis: { title: "C", gridcolor: colors.grid, zeroline: false },
      yaxis2: { title: "%", overlaying: "y", side: "right", range: [0, 100], showgrid: false },
      yaxis3: { overlaying: "y", visible: false, rangemode: "tozero" },
      yaxis4: { overlaying: "y", visible: false }
    }),
    plotConfig
  );
}

function hourlyMeanByHour(pointId, year, key) {
  const h = series[pointId][year].hourly;
  const indices = hourlyIndices(pointId, year);
  const buckets = Array.from({ length: 24 }, () => []);
  indices.forEach(({ index, hour }) => {
    const value = h[key][index];
    if (typeof value === "number") buckets[hour].push(value);
  });
  return buckets.map((bucket) => mean(bucket));
}

function renderDiurnalChart() {
  const x = Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, "0")}:00`);
  const yearColors = [colors.violet, colors.sky, colors.amber, colors.emerald];
  const traces = years.map((year, index) => ({
    x,
    y: hourlyMeanByHour(state.pointId, year, "temperature_2m"),
    name: `${year} C`,
    type: "scatter",
    mode: "lines",
    line: { color: yearColors[index % yearColors.length], width: 3, shape: "spline" }
  }));
  traces.push(
    ...years.map((year, index) => ({
      x,
      y: hourlyMeanByHour(state.pointId, year, "relative_humidity_2m"),
      name: `${year} %`,
      type: "scatter",
      mode: "lines",
      yaxis: "y2",
      line: { color: yearColors[index % yearColors.length], width: 1.8, dash: "dot" }
    }))
  );
  Plotly.react(
    "diurnalChart",
    traces,
    layout({
      yaxis: { title: "C", gridcolor: colors.grid, zeroline: false },
      yaxis2: { title: "%", overlaying: "y", side: "right", range: [35, 100], showgrid: false }
    }),
    plotConfig
  );
}

function renderHeatmap() {
  const metric = state.heatMetric;
  const rawZ = points.map((p) => years.map((year) => summarize(p.id, year)[metric]));
  const flat = rawZ.flat().filter((value) => typeof value === "number");
  const min = Math.min(...flat);
  const max = Math.max(...flat);
  const spread = max - min || 1;
  const z = metric === "hiking_weather_risk"
    ? rawZ.map((row) => row.map((value) => Math.round(((value - min) / spread) * 100)))
    : rawZ;
  const hovertemplate = metric === "hiking_weather_risk"
    ? "%{y}<br>%{x}<br>%{z:.0f}/100<br>raw score %{customdata:.1f}<extra></extra>"
    : "%{y}<br>%{x}<br>%{z:.1f}<extra></extra>";
  Plotly.react(
    "heatmapChart",
    [
      {
        z,
        customdata: rawZ,
        x: years,
        y: points.map((p) => `${p.sample_km} km · ${pointName(p)}`),
        type: "heatmap",
        colorscale: [
          [0, "#0d1f25"],
          [0.25, "#1e6b64"],
          [0.5, "#e0b84f"],
          [0.75, "#dc7546"],
          [1, "#fb7185"]
        ],
        colorbar: { title: t(metricOptions.find((m) => m[0] === metric)?.[1] || "risk"), tickfont: { color: colors.muted }, titlefont: { color: colors.text } },
        hovertemplate
      }
    ],
    layout({
      margin: { l: 178, r: 18, t: 8, b: 38 },
      yaxis: { tickfont: { color: colors.muted, size: 11 }, automargin: true },
      xaxis: { tickfont: { color: colors.muted } }
    }),
    plotConfig
  );
}

function renderRegimes() {
  const labels = ["dryStable", "warmWet", "coldWetSnow", "windExposed", "mixed"];
  const counts = {
    day: Object.fromEntries(labels.map((label) => [label, 0])),
    night: Object.fromEntries(labels.map((label) => [label, 0]))
  };
  const h = series[state.pointId][state.year].hourly;
  hourlyIndices(state.pointId, state.year).forEach(({ index, hour }) => {
    const bucket = hour >= 6 && hour < 18 ? "day" : "night";
    counts[bucket][classifyHour(h, index)] += 1;
  });
  const y = labels.map((label) => t(label));
  Plotly.react(
    "regimeChart",
    [
      { y, x: labels.map((label) => counts.day[label]), name: t("day"), type: "bar", orientation: "h", marker: { color: colors.emerald } },
      { y, x: labels.map((label) => counts.night[label]), name: t("night"), type: "bar", orientation: "h", marker: { color: colors.sky } }
    ],
    layout({
      barmode: "group",
      margin: { l: 138, r: 20, t: 8, b: 44 },
      xaxis: { title: t("hours"), gridcolor: colors.grid, zeroline: false },
      yaxis: { tickfont: { color: colors.muted } }
    }),
    plotConfig
  );
}

function renderScatter() {
  const h = series[state.pointId][state.year].hourly;
  const idx = hourlyIndices(state.pointId, state.year).filter((_, i) => i % 2 === 0).map((d) => d.index);
  Plotly.react(
    "scatterChart",
    [
      {
        x: idx.map((i) => h.temperature_2m[i]),
        y: idx.map((i) => h.relative_humidity_2m[i]),
        text: idx.map((i) => h.time[i]),
        type: "scattergl",
        mode: "markers",
        marker: {
          size: idx.map((i) => Math.max(5, Math.min(20, 5 + (h.precipitation[i] || 0) * 5))),
          color: idx.map((i) => h.precipitation[i] || 0),
          colorscale: [
            [0, "#1d3440"],
            [0.4, "#2dd4bf"],
            [1, "#fb7185"]
          ],
          opacity: 0.78,
          colorbar: { title: "mm/h", tickfont: { color: colors.muted }, titlefont: { color: colors.text } }
        },
        hovertemplate: "%{text}<br>%{x:.1f} C<br>%{y:.0f}%<extra></extra>"
      }
    ],
    layout({
      xaxis: { title: "Temperature C", gridcolor: colors.grid, zeroline: false },
      yaxis: { title: `${t("humidity")} %`, range: [20, 105], gridcolor: colors.grid, zeroline: false },
      showlegend: false
    }),
    plotConfig
  );
}

function renderPlanningTable() {
  const d = series[state.pointId][state.year].daily;
  const rows = dailyIndices(state.pointId, state.year).map(({ index }) => ({
    date: d.time[index],
    tempMin: d.temperature_2m_min[index],
    tempMax: d.temperature_2m_max[index],
    precip: d.precipitation_sum[index] || 0,
    snow: d.snowfall_sum[index] || 0,
    gust: d.wind_gusts_10m_max[index] || 0,
    sunshine: (d.sunshine_duration[index] || 0) / 3600
  }));
  const flagged = rows
    .filter((r) => r.precip < 1 || r.precip >= 10 || r.tempMin <= 3 || r.gust >= 45 || r.snow > 0)
    .sort((a, b) => Number(b.precip >= 10) - Number(a.precip >= 10) || Number(b.gust >= 45) - Number(a.gust >= 45) || a.date.localeCompare(b.date))
    .slice(0, 30);

  $("planningTable").innerHTML = `
    <thead><tr><th>${t("date")}</th><th>${t("signal")}</th><th>Temp</th><th>${t("precip")}</th><th>${t("gust")}</th><th>${t("sun")}</th></tr></thead>
    <tbody>${flagged
      .map((r) => {
        const signals = [];
        if (r.precip < 1) signals.push(t("dry"));
        if (r.precip >= 10) signals.push(t("heavyRain"));
        if (r.tempMin <= 3) signals.push(t("coldStart"));
        if (r.gust >= 45) signals.push(t("wind"));
        if (r.snow > 0) signals.push(t("snow"));
        return `<tr><td>${formatDateLabel(r.date)}</td><td>${signals.map((s) => `<span class="pill">${s}</span>`).join("")}</td><td>${fmt(r.tempMin, "C")} / ${fmt(r.tempMax, "C")}</td><td>${fmt(r.precip, " mm")}</td><td>${fmt(r.gust, " km/h")}</td><td>${fmt(r.sunshine, " h")}</td></tr>`;
      })
      .join("")}</tbody>`;
}

function downloadCsv() {
  const cols = ["point_id", "point_name", "year", "time", "temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "rain", "snowfall", "cloud_cover", "wind_speed_10m", "wind_gusts_10m", "weather_code"];
  const rows = [cols.join(",")];
  points.forEach((p) => {
    const h = series[p.id][state.year].hourly;
    hourlyIndices(p.id, state.year).forEach(({ index }) => {
      rows.push(
        [
          p.id,
          `"${pointName(p).replaceAll('"', '""')}"`,
          state.year,
          h.time[index],
          h.temperature_2m[index],
          h.relative_humidity_2m[index],
          h.apparent_temperature[index],
          h.precipitation[index],
          h.rain[index],
          h.snowfall[index],
          h.cloud_cover[index],
          h.wind_speed_10m[index],
          h.wind_gusts_10m[index],
          h.weather_code[index]
        ].join(",")
      );
    });
  });
  const blob = new Blob([rows.join("\n") + "\n"], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `tmb_open_meteo_${state.year}_${monthDay(state.startDate)}_${monthDay(state.endDate)}.csv`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function refreshAll(resetIntraday = true) {
  clampRange();
  if (resetIntraday) resetIntradayToStart();
  syncI18n();
  fillControls();
  syncSlider();
  renderKpis();
  renderMap();
  renderDailyChart();
  renderIntradayChart();
  renderDiurnalChart();
  renderHeatmap();
  renderRegimes();
  renderScatter();
  renderPlanningTable();
}

function bindEvents() {
  $("pointSelect").addEventListener("change", (event) => {
    state.pointId = event.target.value;
    refreshAll(false);
  });
  $("yearSelect").addEventListener("change", (event) => {
    state.year = event.target.value;
    clampRange();
    refreshAll(true);
  });
  bindDateInput("rangeStart", "startDate");
  bindDateInput("rangeEnd", "endDate");
  $("dateSlider").addEventListener("input", (event) => {
    const dates = availableDates();
    state.intradayDate = dates[Number(event.target.value)] || dates[0];
    syncSlider();
    renderIntradayChart();
  });
  $("heatMetric").addEventListener("change", (event) => {
    state.heatMetric = event.target.value;
    renderHeatmap();
  });
  $("downloadCsv").addEventListener("click", downloadCsv);
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.lang = btn.dataset.lang;
      refreshAll(false);
    });
  });
}

function commitDateInput(id, field) {
  const input = $(id);
  const parsed = parseDateInput(input.value, state[field]);
  state[field] = parsed;
  if (field === "startDate" && state.startDate > state.endDate) state.endDate = state.startDate;
  if (field === "endDate" && state.endDate < state.startDate) state.startDate = state.endDate;
  refreshAll(true);
}

function isCompleteDateDraft(raw) {
  const cleaned = raw.trim();
  return /^\d{4}[-/]\d{2}[-/]\d{2}$/.test(cleaned) || /^\d{2}[-/]\d{2}$/.test(cleaned);
}

function bindDateInput(id, field) {
  const input = $(id);
  let timer;
  input.addEventListener("focus", () => {
    input.value = state[field];
    input.select();
  });
  input.addEventListener("input", () => {
    window.clearTimeout(timer);
    if (isCompleteDateDraft(input.value)) {
      timer = window.setTimeout(() => commitDateInput(id, field), 350);
    }
  });
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      window.clearTimeout(timer);
      input.blur();
    }
    if (event.key === "Escape") {
      window.clearTimeout(timer);
      input.value = formatDateLabel(state[field]);
      input.blur();
    }
  });
  input.addEventListener("blur", () => commitDateInput(id, field));
}

async function loadDashboardData() {
  const embedded = document.getElementById("weather-data");
  if (embedded && embedded.textContent.trim()) {
    return JSON.parse(embedded.textContent);
  }
  const response = await fetch("data/tmb_weather_analytics_2022_2025.json");
  if (!response.ok) throw new Error(`Failed to load dashboard data: ${response.status}`);
  return response.json();
}

async function initDashboard() {
  DATA = await loadDashboardData();
  points = DATA.points;
  years = DATA.years.map(String);
  series = DATA.series;
  pointById = new Map(points.map((p) => [p.id, p]));
  state.year = years.includes("2025") ? "2025" : years[years.length - 1];
  state.startDate = `${state.year}-06-01`;
  state.endDate = `${state.year}-07-31`;
  state.intradayDate = state.startDate;
  bindEvents();
  refreshAll(true);
}

initDashboard().catch((error) => {
  console.error(error);
  document.body.insertAdjacentHTML(
    "afterbegin",
    `<div style="margin:16px;padding:12px;border:1px solid #fb7185;color:#fff;background:#3b1018;border-radius:8px">Dashboard data failed to load. Please serve this project over HTTP, for example with GitHub Pages or a local static server.</div>`
  );
});
