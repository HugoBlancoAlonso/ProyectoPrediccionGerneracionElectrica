from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

try:
    from IPython.display import HTML, IFrame, display
except Exception:  # pragma: no cover
    HTML = None
    IFrame = None
    display = None


WORKSPACE_ROOT = Path(r"c:\Users\hubla\Desktop\IAyBD\BigData\BDSistemas\jupyter\notebooks\ProyectoFinal")


def localizar_parquet_consolidado() -> Path:
    nombre_archivo = "datos_consolidados.parquet"
    script_dir = Path(__file__).resolve().parent
    candidatos = [
        script_dir / "data" / nombre_archivo,
        script_dir / nombre_archivo,
        script_dir.parent / "oro" / "data" / nombre_archivo,
        script_dir.parent / "data" / nombre_archivo,
        WORKSPACE_ROOT / "oro" / "data" / nombre_archivo,
        WORKSPACE_ROOT / "oro" / nombre_archivo,
        WORKSPACE_ROOT / "data" / nombre_archivo,
        Path.cwd().resolve() / nombre_archivo,
        Path.cwd().resolve() / "data" / nombre_archivo,
        Path.cwd().resolve() / "oro" / "data" / nombre_archivo,
    ]
    for candidato in candidatos:
        if candidato.exists():
            return candidato
    raise FileNotFoundError("No se encontró datos_consolidados.parquet en el workspace.")


def cargar_dataframe() -> pd.DataFrame:
    parquet_path = localizar_parquet_consolidado()
    if "df_consolidado" in globals():
        df = globals()["df_consolidado"].copy()
    else:
        df = pd.read_parquet(parquet_path)

    columnas_base = [
        "fecha",
        "Provincia",
        "Estación",
        "tipo_dia",
        "tipo de energia_Hidráulica",
        "tipo de energia",
        "porcentaje",
        "valor",
        "Temperatura media (ºC)",
        "HDD",
        "CDD",
        "Amplitud_Termica",
        "Precipitacion_Total_Calculada",
    ]
    columnas_disponibles = [col for col in columnas_base if col in df.columns]
    df = df[columnas_disponibles].copy()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df.dropna(subset=["fecha"]).copy()

    for columna in [
        "porcentaje",
        "valor",
        "Temperatura media (ºC)",
        "HDD",
        "CDD",
        "Amplitud_Termica",
        "Precipitacion_Total_Calculada",
    ]:
        if columna in df.columns:
            df[columna] = pd.to_numeric(df[columna], errors="coerce").round(3)

    for columna in ["Provincia", "Estación", "tipo_dia"]:
        if columna in df.columns:
            df[columna] = df[columna].astype("string")

    if "tipo de energia" in df.columns:
        df["tipo_energia"] = df["tipo de energia"].astype("string")
    elif "tipo de energia_Hidráulica" in df.columns:
        dummy_hidraulica = pd.to_numeric(df["tipo de energia_Hidráulica"], errors="coerce").fillna(0)
        df["tipo_energia"] = dummy_hidraulica.map({1: "Hidráulica", 0: "Eólica"}).fillna("Sin dato")
    else:
        df["tipo_energia"] = "Sin dato"

    df["fecha"] = df["fecha"].dt.strftime("%Y-%m-%d")
    return df


def construir_html(df: pd.DataFrame) -> str:
    registros_json = json.dumps(df.to_dict(orient="records"), ensure_ascii=False).replace("</", "<\\/")
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Dashboard df_consolidado</title>
  <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
  <style>
    :root {{
      --bg: #07111f;
      --ink: #0f172a;
      --muted: #64748b;
      --accent: #2563eb;
      --accent-2: #14b8a6;
      --line: #dbeafe;
      --shadow: 0 18px 45px rgba(2, 6, 23, 0.18);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(37, 99, 235, 0.18), transparent 32%),
        radial-gradient(circle at top right, rgba(20, 184, 166, 0.16), transparent 30%),
        linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
    }}
    .wrap {{ max-width: 1500px; margin: 0 auto; padding: 20px; }}
    .hero {{
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(37, 99, 235, 0.92));
      color: white;
      border-radius: 22px;
      padding: 24px 26px;
      box-shadow: var(--shadow);
      margin-bottom: 16px;
    }}
    .hero h1 {{ margin: 0 0 8px 0; font-size: 30px; letter-spacing: -0.03em; }}
    .hero p {{ margin: 0; opacity: 0.92; max-width: 980px; line-height: 1.45; }}
    .panel {{
      background: rgba(255, 255, 255, 0.94);
      border: 1px solid rgba(148, 163, 184, 0.28);
      border-radius: 20px;
      box-shadow: var(--shadow);
      padding: 16px;
      margin-bottom: 16px;
    }}
    .controls {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 12px; align-items: end; }}
    .control {{ grid-column: span 3; }}
    .control.wide {{ grid-column: span 4; }}
    .control.small {{ grid-column: span 2; }}
    label {{
      display: block;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.03em;
      color: var(--muted);
      margin-bottom: 6px;
      text-transform: uppercase;
    }}
    input, select {{
      width: 100%;
      padding: 10px 12px;
      border-radius: 12px;
      border: 1px solid #cbd5e1;
      background: white;
      color: var(--ink);
      outline: none;
    }}
    input:focus, select:focus {{ border-color: var(--accent); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12); }}
    
    .tick-container {{
      display: flex;
      flex-direction: column;
      gap: 6px;
      padding: 4px 0;
    }}
    .tick-label {{
      display: flex;
      align-items: center;
      position: relative;
      padding-left: 28px;
      cursor: pointer;
      font-size: 13px;
      color: var(--ink);
      user-select: none;
      text-transform: none;
      font-weight: 500;
      letter-spacing: normal;
      margin-bottom: 0;
    }}
    .tick-label input {{
      position: absolute;
      opacity: 0;
      cursor: pointer;
      height: 0;
      width: 0;
    }}
    .checkmark {{
      position: absolute;
      top: 0;
      left: 0;
      height: 18px;
      width: 18px;
      background-color: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      transition: all 0.2s ease;
    }}
    .tick-label:hover input ~ .checkmark {{
      border-color: var(--accent);
    }}
    .tick-label input:checked ~ .checkmark {{
      background-color: var(--accent);
      border-color: var(--accent);
    }}
    .checkmark:after {{
      content: "";
      position: absolute;
      display: none;
    }}
    .tick-label input:checked ~ .checkmark:after {{
      display: block;
    }}
    .tick-label .checkmark:after {{
      left: 6px;
      top: 2px;
      width: 4px;
      height: 9px;
      border: solid white;
      border-width: 0 2px 2px 0;
      transform: rotate(45deg);
    }}
    
    .kpis {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; }}
    .kpi {{
      background: linear-gradient(180deg, #ffffff, #f8fbff);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px 16px;
      box-shadow: 0 10px 30px rgba(37, 99, 235, 0.06);
    }}
    .kpi .label {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.03em; }}
    .kpi .value {{ font-size: 26px; font-weight: 800; margin-top: 7px; line-height: 1.05; }}
    .kpi .sub {{ font-size: 12px; color: #475569; margin-top: 6px; }}
    
    /* Configuración de 3 columnas para lograr simetría perfecta con 6 gráficos */
    .charts {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }}
    .chart-card {{
      background: white;
      border: 1px solid rgba(148, 163, 184, 0.22);
      border-radius: 18px;
      padding: 12px;
      min-height: 420px;
      box-shadow: 0 12px 32px rgba(15, 23, 42, 0.05);
    }}
    .chart-card h3 {{ margin: 2px 4px 10px 4px; font-size: 14px; color: #0f172a; }}
    .chart {{ width: 100%; height: 360px; }}
    
    .table-wrap {{
      overflow: auto;
      border-radius: 14px;
      border: 1px solid #e2e8f0;
      max-height: 420px;
    }}
    table {{ width: 100%; border-collapse: collapse; background: white; }}
    thead th {{
      position: sticky;
      top: 0;
      background: #eff6ff;
      color: #0f172a;
      text-align: left;
      font-size: 12px;
      padding: 10px 12px;
      border-bottom: 1px solid #dbeafe;
      z-index: 1;
    }}
    tbody td {{
      font-size: 12px;
      padding: 9px 12px;
      border-bottom: 1px solid #f1f5f9;
      color: #0f172a;
      white-space: nowrap;
    }}
    .footer-note {{ color: #475569; font-size: 12px; margin-top: 8px; }}
    .status {{ margin-top: 8px; font-size: 12px; color: #475569; }}
    @media (max-width: 1400px) {{
      .charts {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 1200px) {{
      .control, .control.wide, .control.small {{ grid-column: span 6; }}
      .kpis {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    }}
    @media (max-width: 760px) {{
      .control, .control.wide, .control.small {{ grid-column: span 12; }}
      .kpis {{ grid-template-columns: 1fr; }}
      .charts {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>Dashboard interactivo de DataFrame de generacion de energía Eólica e Hidráulica</h1>
      <p>Explora el consolidado final combinando clima, generación energética y festivos. Los gráficos se recalculan en el navegador sobre el subconjunto filtrado por provincia, estación, fechas y tipo de día.</p>
    </section>

    <section class="panel">
      <div class="controls">
        <div class="control wide">
          <label for="provinceFilter">Provincia</label>
          <select id="provinceFilter"></select>
        </div>
        <div class="control wide">
          <label for="stationFilter">Estación</label>
          <select id="stationFilter"></select>
        </div>
        <div class="control small">
          <label for="dateStart">Desde</label>
          <input id="dateStart" type="date" />
        </div>
        <div class="control small">
          <label for="dateEnd">Hasta</label>
          <input id="dateEnd" type="date" />
        </div>
        <div class="control wide">
          <label for="metricFilter">Serie temporal</label>
          <select id="metricFilter">
            <option value="valor">Valor</option>
            <option value="Temperatura media (ºC)">Temperatura media</option>
            <option value="HDD">HDD</option>
            <option value="CDD">CDD</option>
            <option value="Amplitud_Termica">Amplitud térmica</option>
            <option value="Precipitacion_Total_Calculada">Precipitación total</option>
          </select>
        </div>
        <div class="control wide">
          <label for="groupFilter">Comparar por</label>
          <select id="groupFilter">
            <option value="Provincia">Provincia</option>
            <option value="Estación">Estación</option>
          </select>
        </div>
        <div class="control wide">
          <label for="energyFilter">Generación de energía</label>
          <select id="energyFilter">
            <option value="Todas">Ambas</option>
            <option value="Eólica">Solo eólica</option>
            <option value="Hidráulica">Solo hidráulica</option>
          </select>
        </div>
        <div class="control small">
          <label for="topN">Top N </label>
          <input id="topN" type="range" min="5" max="25" value="10" />
          <div class="status"><span id="topNLabel">10</span> categorías</div>
        </div>
        <div class="control wide">
          <label>Tipo de día</label>
          <div class="tick-container" id="typeFilterContainer"></div>
          <div class="status">Marca o desmarca casillas para filtrar en tiempo real</div>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="kpis" id="kpiGrid"></div>
      <div class="footer-note" id="filterStatus"></div>
    </section>

    <section class="charts">
      <div class="chart-card"><h3 id="lineTitle">Serie temporal</h3><div id="lineChart" class="chart"></div></div>
      <div class="chart-card"><h3 id="barTitle">Comparativa</h3><div id="barChart" class="chart"></div></div>
      <div class="chart-card"><h3 id="pieTitle">Distribución porcentual de generación</h3><div id="pieChart" class="chart"></div></div>
      <div class="chart-card"><h3>Relación temperatura - generación electrica</h3><div id="scatterChart" class="chart"></div></div>
      <div class="chart-card"><h3>Distribución de generación por tipo de día</h3><div id="boxChart" class="chart"></div></div>
      
      <div class="chart-card"><h3>Matriz de Correlación Climático-Energética</h3><div id="heatmapChart" class="chart"></div></div>
    </section>

    <section class="panel">
      <h3 style="margin: 0 0 10px 0;">Muestra del subconjunto filtrado</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Provincia</th>
              <th>Estación</th>
              <th>Generación</th>
              <th>Tipo día</th>
              <th>Valor</th>
              <th>Temp. media</th>
              <th>HDD</th>
              <th>CDD</th>
              <th>Amplitud térmica</th>
              <th>Precipitación total</th>
            </tr>
          </thead>
          <tbody id="sampleTable"></tbody>
        </table>
      </div>
      <div class="footer-note">Los gráficos se actualizan en el navegador sin recargar el notebook.</div>
    </section>
  </div>

  <script id="data-json" type="application/json">{registros_json}</script>
  <script>
    const rawData = JSON.parse(document.getElementById('data-json').textContent);
    const controls = {{
      province: document.getElementById('provinceFilter'),
      station: document.getElementById('stationFilter'),
      dateStart: document.getElementById('dateStart'),
      dateEnd: document.getElementById('dateEnd'),
      metric: document.getElementById('metricFilter'),
      group: document.getElementById('groupFilter'),
      energy: document.getElementById('energyFilter'),
      topN: document.getElementById('topN'),
      typeContainer: document.getElementById('typeFilterContainer'),
    }};

    const labels = {{
      valor: 'Valor Gen.',
      'Temperatura media (ºC)': 'Temp. Media',
      HDD: 'HDD',
      CDD: 'CDD',
      Amplitud_Termica: 'Amp. Térmica',
      Precipitacion_Total_Calculada: 'Precip. Total'
    }};

    const formatNumber = (value, digits = 2) => {{
      if (value === null || value === undefined || Number.isNaN(value)) return 'N/D';
      return Number(value).toLocaleString('es-ES', {{
        minimumFractionDigits: digits,
        maximumFractionDigits: digits
      }});
    }};

    const uniqueSorted = (field, predicate = () => true) => {{
      return [...new Set(rawData.filter(predicate).map(row => row[field]).filter(v => v !== null && v !== undefined && v !== ''))].sort((a, b) => String(a).localeCompare(String(b), 'es'));
    }};

    const updateOptions = () => {{
      const currentProvince = controls.province.value || 'Todas';
      const stationPredicate = row => currentProvince === 'Todas' || row.Provincia === currentProvince;

      const provinces = ['Todas', ...uniqueSorted('Provincia')];
      controls.province.innerHTML = provinces.map(v => `<option value="${{String(v).replaceAll('"', '&quot;')}}">${{v}}</option>`).join('');
      controls.province.value = provinces.includes(currentProvince) ? currentProvince : 'Todas';

      const stations = ['Todas', ...uniqueSorted('Estación', stationPredicate)];
      const currentStation = controls.station.value || 'Todas';
      controls.station.innerHTML = stations.map(v => `<option value="${{String(v).replaceAll('"', '&quot;')}}">${{v}}</option>`).join('');
      controls.station.value = stations.includes(currentStation) ? currentStation : 'Todas';

      const checkedTypes = new Set(Array.from(controls.typeContainer.querySelectorAll('input:checked')).map(cb => cb.value));
      const types = uniqueSorted('tipo_dia');
      const esPrimeraCarga = controls.typeContainer.children.length === 0;

      controls.typeContainer.innerHTML = types.map(v => {{
        const isChecked = esPrimeraCarga || checkedTypes.has(String(v));
        const checkedAttr = isChecked ? 'checked' : '';
        const safeVal = String(v).replaceAll('"', '&quot;');
        return `
          <label class="tick-label">
            <input type="checkbox" value="${{safeVal}}" ${{checkedAttr}} onchange="refresh()">
            <span class="checkmark"></span>
            ${{v}}
          </label>
        `;
      }}).join('');
    }};

    const selectedTypes = () => {{
      const checkedBoxes = controls.typeContainer.querySelectorAll('input:checked');
      return Array.from(checkedBoxes).map(cb => cb.value);
    }};

    const filteredData = () => {{
      const start = controls.dateStart.value ? new Date(controls.dateStart.value + 'T00:00:00') : null;
      const end = controls.dateEnd.value ? new Date(controls.dateEnd.value + 'T23:59:59') : null;
      const province = controls.province.value || 'Todas';
      const station = controls.station.value || 'Todas';
      const energy = controls.energy.value || 'Todas';
      const types = new Set(selectedTypes());

      return rawData.filter(row => {{
        const rowDate = new Date(row.fecha + 'T00:00:00');
        if (start && rowDate < start) return false;
        if (end && rowDate > end) return false;
        if (province !== 'Todas' && row.Provincia !== province) return false;
        if (station !== 'Todas' && row.Estación !== station) return false;
        if (energy !== 'Todas' && String(row.tipo_energia || 'Sin dato') !== energy) return false;
        
        if (types.size === 0) return false;
        if (!types.has(String(row.tipo_dia || ''))) return false;
        return true;
      }});
    }};

    const aggregateByDate = (rows, metric, agg = 'mean') => {{
      const grouped = new Map();
      rows.forEach(row => {{
        const key = row.fecha;
        const value = Number(row[metric]);
        if (Number.isNaN(value)) return;
        if (!grouped.has(key)) grouped.set(key, []);
        grouped.get(key).push(value);
      }});
      const dates = [...grouped.keys()].sort();
      const values = dates.map(date => {{
        const nums = grouped.get(date);
        if (agg === 'sum') return nums.reduce((a, b) => a + b, 0);
        if (agg === 'median') {{
          const sorted = [...nums].sort((a, b) => a - b);
          const mid = Math.floor(sorted.length / 2);
          return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
        }}
        return nums.reduce((a, b) => a + b, 0) / nums.length;
      }});
      return {{ dates, values }};
    }};

    const aggregateByField = (rows, field, metric) => {{
      const grouped = new Map();
      rows.forEach(row => {{
        const key = row[field] ?? 'Sin dato';
        const value = Number(row[metric]);
        if (Number.isNaN(value)) return;
        if (!grouped.has(key)) grouped.set(key, []);
        grouped.get(key).push(value);
      }});
      return [...grouped.entries()]
        .map(([key, nums]) => ({{ key, value: nums.reduce((a, b) => a + b, 0) / nums.length }}))
        .sort((a, b) => b.value - a.value);
    }};

    const sampleRows = rows => rows.slice(0, 12);

    const updateKpis = rows => {{
      const uniqueProvinces = new Set(rows.map(row => row.Provincia).filter(Boolean));
      const uniqueStations = new Set(rows.map(row => row.Estación).filter(Boolean));
      const uniqueEnergy = new Set(rows.map(row => row.tipo_energia).filter(Boolean));
      const avgValue = rows.length ? rows.reduce((sum, row) => sum + (Number(row.valor) || 0), 0) / rows.length : null;
      const avgTemp = rows.length ? rows.reduce((sum, row) => sum + (Number(row['Temperatura media (ºC)']) || 0), 0) / rows.length : null;
      const avgPrecip = rows.length ? rows.reduce((sum, row) => sum + (Number(row.Precipitacion_Total_Calculada) || 0), 0) / rows.length : null;
      const minDate = rows.length ? rows.reduce((min, row) => row.fecha < min ? row.fecha : min, rows[0].fecha) : null;
      const maxDate = rows.length ? rows.reduce((max, row) => row.fecha > max ? row.fecha : max, rows[0].fecha) : null;

      document.getElementById('kpiGrid').innerHTML = `
        <div class="kpi"><div class="label">Registros</div><div class="value">${{rows.length.toLocaleString('es-ES')}}</div><div class="sub">Filas filtradas</div></div>
        <div class="kpi"><div class="label">Estaciones</div><div class="value">${{uniqueStations.size.toLocaleString('es-ES')}}</div><div class="sub">Cobertura activa</div></div>
        <div class="kpi"><div class="label">Provincias</div><div class="value">${{uniqueProvinces.size.toLocaleString('es-ES')}}</div><div class="sub">Áreas visibles</div></div>
        <div class="kpi"><div class="label">Fuentes energía</div><div class="value">${{uniqueEnergy.size.toLocaleString('es-ES')}}</div><div class="sub">Eólica / hidráulica</div></div>
        <div class="kpi"><div class="label">Valor medio</div><div class="value">${{formatNumber(avgValue)}}</div><div class="sub">Promedio del subconjunto</div></div>
        <div class="kpi"><div class="label">Temp. media</div><div class="value">${{formatNumber(avgTemp)}} ºC</div><div class="sub">Promedio climático</div></div>
      `;

      document.getElementById('filterStatus').textContent = rows.length
        ? `Mostrando datos desde ${{minDate}} hasta ${{maxDate}}.`
        : 'No hay datos con los filtros seleccionados.';
    }};

    const renderLine = rows => {{
      const metric = controls.metric.value;
      const series = aggregateByDate(rows, metric, 'mean');
      document.getElementById('lineTitle').textContent = `Serie temporal de ${{labels[metric] || metric}}`;
      Plotly.newPlot('lineChart', [{{ x: series.dates, y: series.values, type: 'scatter', mode: 'lines', line: {{ color: '#2563eb', width: 2.5 }}, hovertemplate: '%{{x}}<br>%{{y:.2f}}<extra></extra>' }}], {{
        margin: {{ t: 16, r: 20, b: 40, l: 55 }},
        paper_bgcolor: 'white',
        plot_bgcolor: 'white',
        xaxis: {{ title: 'Fecha', gridcolor: '#eef2ff' }},
        yaxis: {{ title: labels[metric] || metric, gridcolor: '#eef2ff' }},
        showlegend: false
      }}, {{ displayModeBar: false, responsive: true }});
    }};

    const renderBar = rows => {{
      const field = controls.group.value;
      const topN = Number(controls.topN.value);
      const values = aggregateByField(rows, field, 'valor').slice(0, topN);
      document.getElementById('barTitle').textContent = `Top ${{topN}} ${{field.toLowerCase()}}s con mayor generación de energia`;
      Plotly.newPlot('barChart', [{{
        x: values.map(item => item.key),
        y: values.map(item => item.value),
        type: 'bar',
        marker: {{ color: '#14b8a6' }},
        hovertemplate: '%{{x}}<br>Valor medio: %{{y:.2f}}<extra></extra>'
      }}], {{
        margin: {{ t: 16, r: 20, b: 80, l: 60 }},
        paper_bgcolor: 'white',
        plot_bgcolor: 'white',
        xaxis: {{ title: '', tickangle: -35, gridcolor: '#eef2ff' }},
        yaxis: {{ title: 'Valor medio', gridcolor: '#eef2ff' }},
        showlegend: false
      }}, {{ displayModeBar: false, responsive: true }});
    }};

    const renderPie = rows => {{
      const energyBuckets = {{ 'Eólica': [], 'Hidráulica': [] }};
      const dailyEnergy = new Map();
      rows.forEach(row => {{
        const energia = String(row.tipo_energia || 'Sin dato');
        const porcentaje = Number(row.porcentaje);
        const clave = `${{row.fecha}}|${{energia}}`;
        if (!Number.isNaN(porcentaje) && !dailyEnergy.has(clave)) {{
          dailyEnergy.set(clave, {{ energia, porcentaje }});
        }}
      }});

      dailyEnergy.forEach(item => {{
        if (Object.prototype.hasOwnProperty.call(energyBuckets, item.energia)) {{
          energyBuckets[item.energia].push(item.porcentaje);
        }}
      }});

      const mediaEolica = energyBuckets['Eólica'].length ? energyBuckets['Eólica'].reduce((a, b) => a + b, 0) / energyBuckets['Eólica'].length : 0;
      const mediaHidraulica = energyBuckets['Hidráulica'].length ? energyBuckets['Hidráulica'].reduce((a, b) => a + b, 0) / energyBuckets['Hidráulica'].length : 0;
      const otros = Math.max(0, 100 - mediaEolica - mediaHidraulica);

      const minDate = controls.dateStart.value || '';
      const maxDate = controls.dateEnd.value || '';
      document.getElementById('pieTitle').textContent = 'Distribución porcentual media de generación (' + minDate + ' - ' + maxDate + ')';

      Plotly.newPlot('pieChart', [{{
        labels: ['Eólica', 'Hidráulica', 'Otros'],
        values: [mediaEolica, mediaHidraulica, otros],
        type: 'pie',
        hole: 0.38,
        sort: false,
        direction: 'clockwise',
        marker: {{ colors: ['#f97316', '#2563eb', '#9ca3af'] }},
        textinfo: 'none',
        hovertemplate: '<b>%{{label}}</b><br>%{{value:.2f}}%<extra></extra>'
      }}], {{
        margin: {{ t: 16, r: 20, b: 20, l: 20 }},
        paper_bgcolor: 'white',
        plot_bgcolor: 'white',
        showlegend: true,
        legend: {{ orientation: 'h', y: -0.15 }}
      }}, {{ displayModeBar: false, responsive: true }});
    }};

    const renderScatter = rows => {{
      const subset = rows.filter(row => row['Temperatura media (ºC)'] !== null && row.valor !== null);
      const sample = subset.length > 10000 ? subset.sort(() => 0.5 - Math.random()).slice(0, 10000) : subset;
      const traces = [];
      const groups = new Map();
      sample.forEach(row => {{
        const key = row.tipo_dia || 'Sin dato';
        if (!groups.has(key)) groups.set(key, {{ x: [], y: [] }});
        groups.get(key).x.push(Number(row['Temperatura media (ºC)']));
        groups.get(key).y.push(Number(row.valor));
      }});
      sample.length && [...groups.entries()].forEach(([key, coords], index) => {{
        const palette = ['#2563eb', '#f97316', '#14b8a6', '#8b5cf6', '#ef4444'];
        traces.push({{
          x: coords.x,
          y: coords.y,
          mode: 'markers',
          type: 'scatter',
          name: key,
          marker: {{ size: 6, opacity: 0.42, color: palette[index % palette.length] }}
        }});
      }});
      Plotly.newPlot('scatterChart', traces, {{
        margin: {{ t: 16, r: 20, b: 50, l: 60 }},
        paper_bgcolor: 'white',
        plot_bgcolor: 'white',
        xaxis: {{ title: 'Temperatura media (ºC)', gridcolor: '#eef2ff' }},
        yaxis: {{ title: 'Valor', gridcolor: '#eef2ff' }},
        legend: {{ orientation: 'h', y: -0.2 }}
      }}, {{ displayModeBar: false, responsive: true }});
    }};

    const renderBox = rows => {{
      const groups = new Map();
      rows.forEach(row => {{
        const key = row.tipo_dia || 'Sin dato';
        const value = Number(row.valor);
        if (Number.isNaN(value)) return;
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(value);
      }});
      const traces = [...groups.entries()].map(([key, values], index) => ({{
        y: values,
        type: 'box',
        name: key,
        boxpoints: 'outliers',
        marker: {{ color: ['#2563eb', '#f97316', '#14b8a6', '#8b5cf6', '#ef4444'][index % 5] }}
      }}));
      Plotly.newPlot('boxChart', traces, {{
        margin: {{ t: 16, r: 20, b: 50, l: 60 }},
        paper_bgcolor: 'white',
        plot_bgcolor: 'white',
        yaxis: {{ title: 'Valor', gridcolor: '#eef2ff' }},
        xaxis: {{ title: '' }}
      }}, {{ displayModeBar: false, responsive: true }});
    }};

    // NUEVA FUNCIÓN INTERACTIVA EN JAVASCRIPT: Cálculo matemático del Heatmap de Correlación
    const renderHeatmap = rows => {{
      const vars = ['valor', 'porcentaje', 'Temperatura media (ºC)', 'HDD', 'CDD', 'Amplitud_Termica', 'Precipitacion_Total_Calculada'];
      const textLabels = ['Valor Gen.', 'Mix %', 'Temp. Media', 'HDD', 'CDD', 'Amp. Térmica', 'Precip. Total'];
      
      // 1. Extraer series numéricas válidas limpiando nulos
      const dataMatrix = vars.map(v => rows.map(r => Number(r[v])).filter(num => !Number.isNaN(num)));
      const n = dataMatrix[0] ? dataMatrix[0].length : 0;
      
      const zValues = [];
      
      // Función auxiliar para calcular el coeficiente de correlación de Pearson
      const pearsonCorr = (x, y) => {{
        let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0, sumY2 = 0, count = 0;
        for (let i = 0; i < x.length; i++) {{
          if (!Number.isNaN(x[i]) && !Number.isNaN(y[i])) {{
            sumX += x[i]; sumY += y[i]; sumXY += x[i] * y[i];
            sumX2 += x[i] * x[i]; sumY2 += y[i] * y[i];
            count++;
          }}
        }}
        if (count === 0) return 0;
        const num = (count * sumXY) - (sumX * sumY);
        const den = Math.sqrt(((count * sumX2) - (sumX * sumX)) * ((count * sumY2) - (sumY * sumY)));
        return den === 0 ? 0 : num / den;
      }};

      // 2. Construir la matriz cruzada bidimensional
      for (let i = 0; i < vars.length; i++) {{
        const rowCorr = [];
        for (let j = 0; j < vars.length; j++) {{
          const valX = rows.map(r => Number(r[vars[i]]));
          const valY = rows.map(r => Number(r[vars[j]]));
          rowCorr.push(n > 1 ? pearsonCorr(valX, valY) : 0);
        }}
        zValues.push(rowCorr);
      }}

      // 3. Pintar la matriz simétrica mediante Plotly
      Plotly.newPlot('heatmapChart', [{{
        z: zValues,
        x: textLabels,
        y: textLabels,
        type: 'heatmap',
        colorscale: 'RdBu',
        zmin: -1,
        zmax: 1,
        showscale: true,
        hovertemplate: '%{{x}} vs %{{y}}<br>Correlación: %{{z:.3f}}<extra></extra>'
      }}], {{
        margin: {{ t: 16, r: 20, b: 50, l: 85 }},
        paper_bgcolor: 'white',
        plot_bgcolor: 'white',
        xaxis: {{ tickangle: -25 }}
      }}, {{ displayModeBar: false, responsive: true }});
    }};

    const renderTable = rows => {{
      const preview = sampleRows(rows);
      document.getElementById('sampleTable').innerHTML = preview.map(row => `
        <tr>
          <td>${{row.fecha ?? ''}}</td>
          <td>${{row.Provincia ?? ''}}</td>
          <td>${{row['Estación'] ?? ''}}</td>
          <td>${{row.tipo_energia ?? ''}}</td>
          <td>${{row.tipo_dia ?? ''}}</td>
          <td>${{formatNumber(row.valor)}}</td>
          <td>${{formatNumber(row['Temperatura media (ºC)'])}}</td>
          <td>${{formatNumber(row.HDD)}}</td>
          <td>${{formatNumber(row.CDD)}}</td>
          <td>${{formatNumber(row.Amplitud_Termica)}}</td>
          <td>${{formatNumber(row.Precipitacion_Total_Calculada)}}</td>
        </tr>
      `).join('');
    }};

    const refresh = () => {{
      if (controls.typeContainer.children.length === 0) {{
         updateOptions();
      }}
      const rows = filteredData();
      document.getElementById('topNLabel').textContent = controls.topN.value;
      updateKpis(rows);
      renderLine(rows);
      renderBar(rows);
      renderPie(rows);
      renderScatter(rows);
      renderBox(rows);
      renderHeatmap(rows); // Ejecución sincronizada con los filtros en vivo
      renderTable(rows);
    }};

    ['change', 'input'].forEach(eventName => {{
      controls.province.addEventListener(eventName, () => {{ updateOptions(); refresh(); }});
      controls.station.addEventListener(eventName, refresh);
      controls.energy.addEventListener(eventName, refresh);
      controls.dateStart.addEventListener(eventName, refresh);
      controls.dateEnd.addEventListener(eventName, refresh);
      controls.metric.addEventListener(eventName, refresh);
      controls.group.addEventListener(eventName, refresh);
      controls.topN.addEventListener(eventName, refresh);
    }});

    if (rawData.length > 0) {{
      const dates = rawData.map(row => row.fecha).filter(Boolean).sort();
      controls.dateStart.value = dates[0];
      controls.dateEnd.value = dates[dates.length - 1];
    }}
    refresh();
  </script>
</body>
</html>
"""


def generar_dashboard() -> Path:
    df = cargar_dataframe()
    html = construir_html(df)
    html_path = localizar_parquet_consolidado().parent / "dashboard_df_consolidado.html"
    html_path.write_text(html, encoding="utf-8")

    print(f"Dashboard generado en: {html_path}")
    if display is not None and HTML is not None and IFrame is not None:
        display(HTML(f'<p>Dashboard generado en <a href="{html_path.as_uri()}" target="_blank">{html_path.name}</a></p>'))
        display(IFrame(src=html_path.as_uri(), width="100%", height="1200px"))

    return html_path


if __name__ == "__main__":
    generar_dashboard()