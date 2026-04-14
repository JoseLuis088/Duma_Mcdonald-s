content = open("static/index.html", "r", encoding="utf-8").read()

# Fix 1: Add cvGrid div before <script>
old1 = '</button>\n            </div>\n          </div>\n\n    <script>'
new1 = '</button>\n            </div>\n          </div>\n\n          <!-- Chart output container -->\n          <div id="cvGrid" style="margin-top: 16px; min-height: 60px;"></div>\n\n    <script>'
content = content.replace(old1, new1, 1)

# Fix 2: Fix flatpickr init to use setDate so selectedDates is populated
old2 = '// Initialize flatpickr\n      const datePicker = flatpickr("#filterDate", {\n        mode: "range",\n        dateFormat: "Y-m-d",\n        appendTo: document.body,\n        disableMobile: true,\n        defaultDate: ["2025-10-01", todayISO()]\n      });'
new2 = '// Initialize flatpickr\n      const datePicker = flatpickr("#filterDate", {\n        mode: "range",\n        dateFormat: "Y-m-d",\n        appendTo: document.body,\n        disableMobile: true\n      });\n      // setDate populates selectedDates so the query works on first load\n      datePicker.setDate(["2025-10-01", todayISO()], false);'
content = content.replace(old2, new2, 1)

open("static/index.html", "w", encoding="utf-8").write(content)
print("Done. Verifying cvGrid:", "cvGrid" in content)
print("Verifying setDate:", "setDate" in content)
