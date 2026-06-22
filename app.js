const stages = [
  {
    label: "Healthy plant",
    tone: "green",
    risk: 18,
    risk30: 24,
    risk60: 31,
    gas: "0.8% LEL",
    permit: "No hot work",
    maintenance: "Routine",
    shift: "Stable",
    workers: 9,
    action: "Continue monitoring normal operations.",
    copilot: "Safe right now. Permit and gas state are within limits.",
    checks: [
      ["Permit state", "Clear"],
      ["Methane", "0.8% LEL"],
      ["Zone access", "Authorized"],
      ["PPE confidence", "98%"]
    ],
    reasoning: [
      "Sentinel Agent confirms the plant twin is synchronized across sensors, permits, and worker state.",
      "Hazard Correlation Agent sees no overlapping high-risk conditions in Zone C."
    ],
    violations: []
  },
  {
    label: "Gas rising",
    tone: "yellow",
    risk: 43,
    risk30: 58,
    risk60: 67,
    gas: "2.9% LEL",
    permit: "No hot work",
    maintenance: "Routine",
    shift: "Stable",
    workers: 9,
    action: "Dispatch field safety officer to verify methane sensor and ventilation status.",
    copilot: "Caution. Methane is rising. Verify ventilation before starting new work.",
    checks: [
      ["Permit state", "Clear"],
      ["Methane", "2.9% LEL"],
      ["Zone access", "Authorized"],
      ["PPE confidence", "97%"]
    ],
    reasoning: [
      "SCADA stream reports a sustained methane increase in Zone C.",
      "Prediction Agent projects threshold breach risk inside the next hour if the trend continues."
    ],
    violations: []
  },
  {
    label: "Maintenance active",
    tone: "orange",
    risk: 63,
    risk30: 84,
    risk60: 92,
    gas: "4.6% LEL",
    permit: "Hot work active",
    maintenance: "Boiler 7 repair",
    shift: "Handover in 12 min",
    workers: 12,
    action: "Pause hot work, isolate Boiler 7, and hold shift handover until Zone C is cleared.",
    copilot: "Unsafe. Hot work overlaps with rising methane in Zone C.",
    checks: [
      ["Permit state", "Hot work active"],
      ["Methane", "4.6% LEL"],
      ["Zone access", "12 workers"],
      ["PPE confidence", "94%"]
    ],
    reasoning: [
      "Permit Intelligence Agent detects hot work authorization overlapping with elevated methane.",
      "Knowledge Graph links Boiler 7, Zone C, Methane Sensor C-04, and active maintenance job WO-712.",
      "Historical incident similarity model finds 3 prior events with gas rise plus maintenance plus handover."
    ],
    violations: [
      ["OISD hot work control", "Combustible gas condition conflicts with active hot work permit."],
      ["Factory Act safe workplace duty", "Compound hazard requires preventive action before exposure continues."]
    ]
  },
  {
    label: "Compound hazard",
    tone: "red",
    risk: 86,
    risk30: 94,
    risk60: 97,
    gas: "6.2% LEL",
    permit: "Hot work active",
    maintenance: "Boiler 7 repair",
    shift: "Handover now",
    workers: 14,
    action: "Evacuate Zone C, suspend hot work permit, alert emergency response, and preserve evidence.",
    copilot: "Unsafe. Methane exceeds safe hot work conditions under OISD guidance. Do not weld.",
    checks: [
      ["Permit state", "Suspend"],
      ["Methane", "6.2% LEL"],
      ["Zone access", "Evacuate"],
      ["PPE confidence", "91%"]
    ],
    reasoning: [
      "Risk escalation detected. Hot work permit active in Zone C while methane concentration is increasing.",
      "Shift handover is in progress, raising coordination risk and weakening command continuity.",
      "Emergency Commander Agent recommends evacuation and incident evidence preservation."
    ],
    violations: [
      ["OISD hot work control", "Hot work cannot continue under elevated combustible gas readings."],
      ["DGMS hazardous area procedure", "Worker exposure must be controlled when atmospheric risk escalates."],
      ["Factory Act emergency preparedness", "Preventive evacuation and documented response are required."]
    ]
  }
];

let stageIndex = 0;
let workflowTriggered = false;

const els = {
  canvas: document.querySelector("#plantCanvas"),
  scenarioLabel: document.querySelector("#scenarioLabel"),
  mapCallout: document.querySelector("#mapCallout"),
  riskNow: document.querySelector("#riskNow"),
  riskTrend: document.querySelector("#riskTrend"),
  risk30: document.querySelector("#risk30"),
  risk60: document.querySelector("#risk60"),
  recommendedAction: document.querySelector("#recommendedAction"),
  workflowBtn: document.querySelector("#workflowBtn"),
  signalGrid: document.querySelector("#signalGrid"),
  reasoningList: document.querySelector("#reasoningList"),
  violationList: document.querySelector("#violationList"),
  stepBtn: document.querySelector("#stepBtn"),
  resetBtn: document.querySelector("#resetBtn"),
  copilotAnswer: document.querySelector("#copilotAnswer"),
  fieldChecks: document.querySelector("#fieldChecks"),
  execRisk: document.querySelector("#execRisk"),
  execCompliance: document.querySelector("#execCompliance"),
  execTrend: document.querySelector("#execTrend"),
  execViolations: document.querySelector("#execViolations"),
  bars: document.querySelector("#bars"),
  auditItems: document.querySelector("#auditItems")
};

const ctx = els.canvas.getContext("2d");

function toneColor(tone) {
  return {
    green: "#15803d",
    yellow: "#c78408",
    orange: "#d85f12",
    red: "#c92323"
  }[tone];
}

function drawPlant(stage) {
  const { width, height } = els.canvas;
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#eaf0e8";
  ctx.fillRect(0, 0, width, height);

  ctx.strokeStyle = "#cfd8cf";
  ctx.lineWidth = 2;
  for (let x = 80; x < width; x += 120) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();
  }
  for (let y = 80; y < height; y += 110) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.stroke();
  }

  const zones = [
    { name: "A", x: 70, y: 90, w: 250, h: 160, color: "#15803d" },
    { name: "B", x: 365, y: 70, w: 250, h: 185, color: "#15803d" },
    { name: "C", x: 660, y: 115, w: 295, h: 230, color: toneColor(stage.tone) },
    { name: "D", x: 110, y: 340, w: 330, h: 190, color: "#15803d" },
    { name: "E", x: 505, y: 395, w: 390, h: 165, color: stage.tone === "red" ? "#d85f12" : "#15803d" }
  ];

  zones.forEach(zone => {
    ctx.fillStyle = zone.color + "26";
    ctx.strokeStyle = zone.color;
    ctx.lineWidth = zone.name === "C" ? 5 : 3;
    ctx.beginPath();
    roundRect(zone.x, zone.y, zone.w, zone.h, 18);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = "#17211c";
    ctx.font = "800 32px system-ui";
    ctx.fillText(`Zone ${zone.name}`, zone.x + 22, zone.y + 48);
  });

  drawPipe(185, 250, 790, 250);
  drawPipe(790, 250, 790, 430);
  drawTank(780, 208, "Boiler 7");
  drawTank(235, 414, "Compressor");
  drawWorkers(stage.workers, stage.tone);

  if (stage.tone !== "green") {
    ctx.fillStyle = toneColor(stage.tone) + "33";
    ctx.beginPath();
    ctx.arc(800, 235, stage.tone === "red" ? 135 : 92, 0, Math.PI * 2);
    ctx.fill();
  }
}

function roundRect(x, y, w, h, r) {
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
}

function drawPipe(x1, y1, x2, y2) {
  ctx.strokeStyle = "#4b6475";
  ctx.lineWidth = 18;
  ctx.lineCap = "round";
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.stroke();
  ctx.strokeStyle = "#d7e1df";
  ctx.lineWidth = 3;
  ctx.stroke();
}

function drawTank(x, y, label) {
  ctx.fillStyle = "#f8faf8";
  ctx.strokeStyle = "#4b6475";
  ctx.lineWidth = 4;
  ctx.beginPath();
  roundRect(x - 65, y - 50, 130, 100, 12);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = "#17211c";
  ctx.font = "800 19px system-ui";
  ctx.textAlign = "center";
  ctx.fillText(label, x, y + 8);
  ctx.textAlign = "left";
}

function drawWorkers(count, tone) {
  const positions = [
    [700, 170], [742, 184], [836, 182], [888, 222], [756, 286], [865, 300],
    [688, 295], [915, 292], [780, 215], [825, 258], [722, 235], [905, 165],
    [812, 326], [952, 250]
  ];
  positions.slice(0, count).forEach(([x, y], index) => {
    ctx.fillStyle = index > 11 ? "#c92323" : toneColor(tone);
    ctx.beginPath();
    ctx.arc(x, y, 11, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#fff";
    ctx.beginPath();
    ctx.arc(x, y - 2, 3, 0, Math.PI * 2);
    ctx.fill();
  });
}

function render() {
  const stage = stages[stageIndex];
  drawPlant(stage);
  els.scenarioLabel.textContent = stage.label;
  els.scenarioLabel.className = `state-chip ${stage.tone}`;
  els.mapCallout.innerHTML = `<strong>Zone C</strong><span>Risk ${stage.risk}</span>`;
  els.riskNow.textContent = stage.risk;
  els.risk30.textContent = stage.risk30;
  els.risk60.textContent = stage.risk60;
  els.riskTrend.textContent = `+${stage.risk30 - stage.risk} in 30 min`;
  els.recommendedAction.textContent = workflowTriggered ? "Emergency workflow active: response teams notified and evidence package sealed." : stage.action;
  els.workflowBtn.disabled = stage.risk < 80 || workflowTriggered;
  els.workflowBtn.textContent = workflowTriggered ? "Workflow active" : "Trigger emergency workflow";
  els.copilotAnswer.textContent = stage.copilot;

  els.signalGrid.innerHTML = [
    ["Methane", stage.gas],
    ["Permit", stage.permit],
    ["Maintenance", stage.maintenance],
    ["Shift", stage.shift],
    ["Workers", String(stage.workers)],
    ["Risk Score", String(stage.risk)]
  ].map(([label, value]) => `<div class="signal"><span>${label}</span><strong>${value}</strong></div>`).join("");

  els.reasoningList.innerHTML = stage.reasoning.map(item => `<li>${item}</li>`).join("");
  els.violationList.innerHTML = stage.violations.length
    ? stage.violations.map(([rule, text]) => `<div class="violation"><strong>${rule}</strong><p>${text}</p></div>`).join("")
    : `<div class="signal"><span>No active violations</span><strong>Compliant</strong></div>`;

  els.fieldChecks.innerHTML = stage.checks.map(([label, value]) => `<div class="check"><strong>${label}</strong><span>${value}</span></div>`).join("");
  els.execRisk.textContent = stage.risk;
  els.execCompliance.textContent = `${Math.max(62, 98 - stage.violations.length * 11 - stageIndex * 3)}%`;
  els.execTrend.textContent = stageIndex >= 2 ? "+28%" : "-12%";
  els.execViolations.textContent = stage.violations.length;
  els.bars.innerHTML = [14, 21, 18, 28, stage.risk, stage.risk30, stage.risk60, Math.min(99, stage.risk60 + 5)]
    .map(value => `<div class="bar" style="height:${value * 2.25}px;background:${value > 80 ? "#c92323" : value > 60 ? "#d85f12" : value > 40 ? "#c78408" : "#087f8c"}"></div>`)
    .join("");

  const audit = [
    ["Sensor logs", `Methane Sensor C-04: ${stage.gas}`],
    ["Permit evidence", stage.permit],
    ["CCTV snapshot", `${stage.workers} workers identified in Zone C`],
    ["Agent trace", `${stage.reasoning.length} reasoning events recorded`],
    ["Regulation references", `${stage.violations.length || 0} mapped references`],
    ["Workflow record", workflowTriggered ? "Emergency response triggered" : "No emergency action triggered"]
  ];
  els.auditItems.innerHTML = audit.map(([title, text]) => `<div class="audit-item"><strong>${title}</strong><span>${text}</span></div>`).join("");
}

document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab, .view").forEach(el => el.classList.remove("active"));
    tab.classList.add("active");
    document.querySelector(`#${tab.dataset.view}`).classList.add("active");
  });
});

els.stepBtn.addEventListener("click", () => {
  stageIndex = Math.min(stages.length - 1, stageIndex + 1);
  render();
});

els.resetBtn.addEventListener("click", () => {
  stageIndex = 0;
  workflowTriggered = false;
  render();
});

els.workflowBtn.addEventListener("click", () => {
  workflowTriggered = true;
  render();
});

render();
