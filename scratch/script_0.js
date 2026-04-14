
      console.log("[Duma] Bloque de script detectado y ejecutándose (etapa inicial).");
      
      /**
       * [Duma] Core Dashboard Engine
       */
      const el = (id) => document.getElementById(id);
      let datePicker = null;
      let plotlyData = null;
      let currentGranularity = 'hour';
      let filterMapping = {};
      let allSucursalesList = [];

      /**
       * 1. Theme Module
       */
      function initTheme() {
          const savedTheme = localStorage.getItem('duma-theme');
          const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          const theme = savedTheme || (prefersDark ? 'dark' : 'light');
          document.documentElement.setAttribute('data-theme', theme);
          updateThemeIcon(theme);
          updatePlotlyTheme(theme);
      }

      function toggleTheme() {
          const currentTheme = document.documentElement.getAttribute('data-theme');
          const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
          document.documentElement.setAttribute('data-theme', newTheme);
          localStorage.setItem('duma-theme', newTheme);
          updateThemeIcon(newTheme);
          updatePlotlyTheme(newTheme);
      }

      function updateThemeIcon(theme) {
          const toggleBtn = el('themeToggle');
          if (toggleBtn) {
              toggleBtn.querySelector('span').textContent = theme === 'dark' ? '☀️' : '🌙';
              toggleBtn.title = theme === 'dark' ? 'Modo claro' : 'Modo oscuro';
          }
      }

      function updatePlotlyTheme(theme) {
          const isDark = theme === 'dark';
          const style = {
              paper_bgcolor: 'transparent',
              plot_bgcolor: 'transparent',
              font: { family: 'Inter, sans-serif', color: isDark ? '#e2e8f0' : '#1e293b' },
              'xaxis.gridcolor': isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
              'yaxis.gridcolor': isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
              'xaxis.tickfont.color': isDark ? '#e2e8f0' : '#1e293b',
              'yaxis.tickfont.color': isDark ? '#e2e8f0' : '#1e293b'
          };
          if (el('sensePlot')) Plotly.relayout('sensePlot', style);
          if (el('availPlot')) Plotly.relayout('availPlot', style);
      }

      /**
       * 2. UI Utilities
       */
      function setStatus(kind, text) {
          const pill = el("statusPill");
          if (!pill) return;
          pill.className = `pill ${kind}`;
          pill.textContent = text;
      }

      function mdToHtml(md) {
          return md ? marked.parse(md) : '';
      }


      /**
       * 3. Duma Chat Module
       */
      const chatWidget = {
          threadId: null,
          isOpen: false,
          isTyping: false,

          init() {
              el("chatBubbleBtn")?.addEventListener("click", () => this.toggle());
              el("chatCloseBtn")?.addEventListener("click", () => this.toggle());
              el("chatClearBtn")?.addEventListener("click", () => this.clearChat());
              el("chatSendBtn")?.addEventListener("click", () => this.handleSend());
              el("chatInput")?.addEventListener("keypress", (e) => { if (e.key === "Enter") this.handleSend(); });
              this.threadId = localStorage.getItem("duma_thread_id") || null;
              
              const handle = el('chatResizeHandle');
              const win = el('chatWindow');
              if (handle && win) {
                  let startX, startY, startW, startH;
                  handle.addEventListener('mousedown', (e) => {
                      startX = e.clientX; startY = e.clientY;
                      startW = parseInt(getComputedStyle(win).width, 10);
                      startH = parseInt(getComputedStyle(win).height, 10);
                      const moveH = (me) => {
                          win.style.width  = Math.max(300, startW + (startX - me.clientX)) + 'px';
                          win.style.height = Math.max(400, startH + (startY - me.clientY)) + 'px';
                      };
                      const upH = () => {
                          document.removeEventListener('mousemove', moveH);
                          document.removeEventListener('mouseup', upH);
                      };
                      document.addEventListener('mousemove', moveH);
                      document.addEventListener('mouseup', upH);
                  });
              }
          },

          toggle() { this.isOpen ? this.close() : this.open(); },
          open() { el("chatWindow").style.display = "flex"; this.isOpen = true; },
          close() { el("chatWindow").style.display = "none"; this.isOpen = false; },

          async handleSend() {
              const input = el("chatInput");
              const text = input?.value.trim();
              if (!text || this.isTyping) return;
              input.value = "";
              this.addMessage("user", text);
              this.showTyping(true);

              try {
                  const res = await fetch("chat/", {
                      method: "POST", headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ input: text, thread_id: this.threadId })
                  }).then(r => r.json());
                  this.showTyping(false);
                  if (res.thread_id) { this.threadId = res.thread_id; localStorage.setItem("duma_thread_id", res.thread_id); }
                  if (res.message) this.addMessage("bot", res.message, res.images);
              } catch (e) {
                  this.showTyping(false);
                  this.addMessage("bot", "⚠️ Error de conexión.");
              }
          },

          addMessage(role, text, images = []) {
              const container = el("chatMsgs");
              if (!container) return;
              const msg = document.createElement("div");
              msg.className = `msg ${role}`;
              if (role === "bot") {
                  msg.innerHTML = mdToHtml(text);
                  images?.forEach(url => {
                      const btn = document.createElement("div");
                      btn.className = "chat-plot-btn"; btn.innerHTML = `<span>📊 Ver gráfica</span>`;
                      btn.onclick = () => window.openFullScreen(url.replace('sandbox:', ''), "Análisis de Datos");
                      msg.appendChild(btn);
                  });
              } else {
                  msg.textContent = text;
              }
              container.appendChild(msg);
              container.scrollTop = container.scrollHeight;
          },

          showTyping(show) {
              this.isTyping = show;
              const existing = document.querySelector(".typing-wrapper");
              if (existing) existing.remove();
              if (show) {
                  const wrapper = document.createElement("div");
                  wrapper.className = "typing-wrapper";
                  wrapper.innerHTML = `<div class="msg bot typing"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>`;
                  el("chatMsgs")?.appendChild(wrapper);
              }
          },
          clearChat() {
              if (!confirm("¿Deseas reiniciar la conversación?")) return;
              this.threadId = null;
              localStorage.removeItem("duma_thread_id");
              el("chatMsgs").innerHTML = `<div class="msg bot">¡Hola! He reiniciado mi memoria. ¿En qué puedo ayudarte?</div>`;
          }
      };

      /**
       * 4. Data & Filter Module
       */
      async function loadFilters() {
          const ciudadSel = el("filterCiudad");
          const sucSel = el("filterSucursal");
          if (!ciudadSel || !sucSel) return;
          try {
              const res = await fetch("/api/sense/filters").then(r => r.json());
              if (res.status === "success" && res.data) {
                  filterMapping = res.data.mapping || {};
                  allSucursalesList = res.data.sucursales || [];
                  ciudadSel.innerHTML = '<option value="All">Todas las ciudades</option>';
                  res.data.ciudades?.forEach(c => {
                      const opt = document.createElement("option");
                      opt.value = c; opt.textContent = c;
                      ciudadSel.appendChild(opt);
                  });
                  updateBranchSelect("All");
                  console.log("[Duma] Filtros inicializados.");
              }
          } catch (e) { console.error("[Duma] Error filtros:", e); }
      }

      function updateBranchSelect(cityName) {
          const sucSel = el("filterSucursal");
          if (!sucSel) return;
          sucSel.innerHTML = '<option value="All">Todas las sucursales</option>';
          const branches = (cityName === "All") ? allSucursalesList : (filterMapping[cityName] || []);
          branches.forEach(s => {
              const opt = document.createElement("option");
              opt.value = s; opt.textContent = s;
              sucSel.appendChild(opt);
          });
      }

      async function fetchSenseData() {
          const dates = datePicker.selectedDates;
          const from_day = dates.length >= 2 ? flatpickr.formatDate(dates[0], "Y-m-d") : "2025-10-01";
          const to_day   = dates.length >= 2 ? flatpickr.formatDate(dates[1], "Y-m-d") : new Date().toISOString().split('T')[0];
          const ciudad = el("filterCiudad").value;
          const sucursal = el("filterSucursal").value;
          const grid = el("cvGrid");
          const btn = el("btnConsultarRango");

          if (btn) { btn.textContent = "Consultando..."; btn.disabled = true; btn.classList.add("busy"); }
          setStatus("busy", "Analizando...");
          if (el("kpiContainer")) el("kpiContainer").style.display = "none";
          if (grid) grid.innerHTML = '<div style="width:100%; text-align:center; padding: 40px; color: var(--brand);"><strong>Consultando Databricks...</strong></div>';

          try {
              const res = await fetch("/api/sense/chart-data", {
                  method: "POST", headers: {"Content-Type": "application/json"},
                  body: JSON.stringify({from_day, to_day, ciudad, sucursal, granularity: currentGranularity})
              }).then(r => r.json());

              if (res.data?.labels?.length > 0) {
                  plotlyData = res.data;
                  grid.innerHTML = `
                      <div class="card" id="mainChartCard">
                          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                              <h3 style="margin: 0; font-weight: 800; font-size: 18px; color: var(--text);">Monitoreo de Corriente (Amperes)</h3>
                              <button class="btn-fs-toggle" id="btnToggleFS">⛶ Pantalla Completa</button>
                          </div>
                          <div id="sensePlot" style="height: 400px; width: 100%;"></div>
                      </div>
                      <div class="card" id="availChartCard" style="display: none;">
                          <h3 style="margin: 0 0 20px 0; font-weight: 800; font-size: 18px; color: var(--text);">Disponibilidad %</h3>
                          <div id="availPlot" style="height: 350px; width: 100%;"></div>
                      </div>
                  `;
                  if (res.data.kpis) {
                      el("kpiContainer").style.display = "grid";
                      el("kpi-availability").textContent = res.data.kpis.availability;
                      el("kpi-load").textContent = res.data.kpis.avg_load;
                      if (res.data.kpis.daily_availability) {
                          el("availChartCard").style.display = "block";
                          renderAvailabilityChart(res.data.kpis.daily_availability);
                      }
                  }
                  renderPlotlyChart(res.data);
                  el("btnToggleFS")?.addEventListener("click", toggleFullscreenChart);
                  triggerAIAnalysis(res.data, ciudad, sucursal, from_day, to_day);
                  setStatus("ok", "Listo");
              } else {
                  grid.innerHTML = '<div style="width:100%; text-align:center; padding: 40px; color: gray;">No hay datos para esta selección.</div>';
                  setStatus("ok", "Sin datos");
              }
          } catch(e) { setStatus("err", "Error"); }
          finally { if (btn) { btn.textContent = "Consultar Rango"; btn.disabled = false; btn.classList.remove("busy"); } }
      }

      /**
       * 5. Visualization Module
       */
      function renderPlotlyChart(data) {
          const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
          const traces = data.datasets.map(ds => ({
              x: data.labels, y: ds.data, name: ds.label, type: 'scatter', mode: 'lines',
              line: { color: ds.borderColor, width: 2.5, shape: 'spline' }, connectgaps: true
          }));
          const style = {
              paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
              margin: { t: 10, r: 10, b: 40, l: 40 },
              font: { family: 'Inter, sans-serif', color: isDark ? '#e2e8f0' : '#1e293b' },
              xaxis: { gridcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)', zeroline: false, tickfont: { color: isDark ? '#e2e8f0' : '#1e293b' } },
              yaxis: { title: { text: "amperes", font: { size: 10 } }, gridcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)', zeroline: false, tickfont: { color: isDark ? '#e2e8f0' : '#1e293b' } },
              legend: { orientation: 'h', y: -0.2 }
          };
          Plotly.newPlot('sensePlot', traces, style, { responsive: true, displayModeBar: false });
      }

      function renderAvailabilityChart(dailyData) {
          const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
          const trace = {
              x: dailyData.map(d => d.date), y: dailyData.map(d => d.value), type: 'bar',
              marker: { color: dailyData.map(v => v.value >= 90 ? '#4ade80' : (v.value >= 70 ? '#facc15' : '#f87171')) }
          };
          const style = {
              paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
              margin: { t: 10, r: 10, b: 40, l: 40 },
              font: { family: 'Inter, sans-serif', color: isDark ? '#e2e8f0' : '#1e293b' },
              xaxis: { gridcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)', tickfont: { size: 9, color: isDark ? '#e2e8f0' : '#1e293b' } },
              yaxis: { range: [0, 105], title: { text: "% Uptime", font: { size: 10 } }, tickfont: { size: 9, color: isDark ? '#e2e8f0' : '#1e293b' } }
          };
          Plotly.newPlot('availPlot', [trace], style, { responsive: true, displayModeBar: false });
      }

      function toggleFullscreenChart() {
          const card = el("mainChartCard");
          const plot = el("sensePlot");
          if (!card || !plot) return;
          const isFS = card.classList.toggle('fs-overlay');
          plot.style.height = isFS ? 'calc(100vh - 120px)' : '400px';
          document.body.style.overflow = isFS ? 'hidden' : 'auto';
          Plotly.Plots.resize(plot);
      }

      window.openFullScreen = (url, title) => {
          const backdrop = document.createElement("div");
          backdrop.className = "modal-backdrop";
          backdrop.innerHTML = `
              <div class="modal-header"><div class="modal-title">${title}</div><button class="btn-icon-close" onclick="this.closest('.modal-backdrop').remove()">✕</button></div>
              <div class="modal-content"><img src="${url}" style="width:100%; height:100%; object-fit:contain; background:white;"></div>
          `;
          document.body.appendChild(backdrop);
      };

      /**
       * 6. AI & PDF Functions
       */
      async function triggerAIAnalysis(data, ciudad, sucursal, from, to) {
          const content = el("aiContent");
          if (!content) return;
          el("aiAnalysisContainer").style.display = "block";
          content.innerHTML = `<div class="ai-loading"><div class="ai-pulse"></div><div style="font-weight:700; color:var(--brand);">DUMA analizando equipos críticos...</div></div>`;
          try {
              const summary = `Sucursal: ${sucursal} (${ciudad}). Periodo: ${from} a ${to}. Uptime: ${data.kpis.availability}. Carga: ${data.kpis.avg_load}. Desbalance: ${data.kpis.imbalance}.`;
              const res = await fetch("/api/sense/ai-analysis", {
                  method: "POST", headers: {"Content-Type": "application/json"},
                  body: JSON.stringify({ summary })
              }).then(r => r.json());
              content.innerHTML = mdToHtml(res.report || "No se pudo generar el análisis.");
          } catch(e) { content.innerHTML = "<p>Error al conectar con la IA.</p>"; }
      }

      window.exportDashboardToPDF = async function() {
          const btn = document.querySelector(".btn-pdf");
          if (!btn) return;
          const original = btn.innerHTML;
          btn.innerHTML = "<span>⏳</span> Generando..."; btn.disabled = true;
          try {
              const sucursal = el("filterSucursal").value;
              const jsPDF = window.jspdf?.jsPDF || window.jsPDF;
              const doc = new jsPDF({ orientation: 'p', unit: 'in', format: 'letter' });
              await Plotly.relayout('sensePlot', { 'font.color': '#000', 'xaxis.tickfont.color': '#000', 'yaxis.tickfont.color': '#000' });
              const img1 = await Plotly.toImage('sensePlot', { format: 'png', width: 1200, height: 600, scale: 2 });
              await Plotly.relayout('availPlot', { 'font.color': '#000', 'xaxis.tickfont.color': '#000', 'yaxis.tickfont.color': '#000' });
              const img2 = await Plotly.toImage('availPlot', { format: 'png', width: 1200, height: 500, scale: 2 });
              updatePlotlyTheme(document.documentElement.getAttribute('data-theme'));
              doc.setFont("helvetica", "bold").setFontSize(22).text("Reporte Operativo - Duma AI", 0.5, 0.85);
              doc.setFontSize(10).setTextColor(100).text(`Sucursal: ${sucursal}`, 8, 0.85, { align: 'right' });
              doc.addImage(img1, 'PNG', 0.5, 1.5, 7.5, 3.5);
              doc.addPage().addImage(img2, 'PNG', 0.5, 1, 7.5, 3);
              const lines = doc.splitTextToSize(el("aiContent")?.innerText || "", 7.5);
              doc.text(lines, 0.5, 4.8);
              doc.save(`Reporte_Duma_${sucursal}.pdf`);
          } catch(e) { alert("Error: " + e.message); }
          finally { btn.innerHTML = original; btn.disabled = false; }
      };

      /**
       * 7. Dashboard Initialization
       */
      function initDashboard() {
          initTheme();
          chatWidget.init();
          datePicker = flatpickr("#filterDate", {
              mode: "range", dateFormat: "Y-m-d", appendTo: document.body,
              defaultDate: ["2025-10-01", new Date().toISOString().split('T')[0]]
          });
          el('themeToggle')?.addEventListener('click', toggleTheme);
          el('brandToggle')?.addEventListener('click', () => el('sidebar').classList.toggle('collapsed'));
          el('filterCiudad')?.addEventListener('change', (e) => updateBranchSelect(e.target.value));
          el('btnConsultarRango')?.addEventListener('click', fetchSenseData);
          loadFilters();
      }

      document.addEventListener('DOMContentLoaded', initDashboard);
    