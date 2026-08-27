let globalCharts = {};
let ALL_MODELS = [];               
let SELECTED_KEYS = new Set();     

const STUDENT_BACKBONE_ORDER = ["mobilenet_v3_large", "efficientnet_b0", "resnet18", "shufflenet_v2_x1_0", "densenet121", "efficientnet_b3"];

function refPct(v) {
    return (v === undefined || v === null) ? '—' : (v * 100).toFixed(2) + '%';
}

function checkboxHtml(m, idPrefix = 'cb', titleText = null, refLineOverride = null) {
    const checked = SELECTED_KEYS.has(m.key) ? 'checked' : '';
    const cbmTag = m.is_cbm ? '<span class="tag-cbm">CBM</span>' : '';
    const ref = m.ref_metrics || {};
    const refLine = refLineOverride !== null ? refLineOverride : (ref.f1 !== undefined
        ? `F1 luận văn: ${refPct(ref.f1)} · ${m.size}`
        : `${m.size}`);
    const title = titleText !== null ? titleText : m.backbone_label;
    return `
        <label class="model-option ${checked ? 'selected' : ''}" for="${idPrefix}_${m.key}" data-key="${m.key}">
            <input class="model-option-checkbox" type="checkbox" value="${m.key}" id="${idPrefix}_${m.key}" ${checked}>
            <span class="model-option-check"><i class="bi bi-check-lg"></i></span>
            <span class="model-option-body">
                <span class="model-option-title">${title}${cbmTag}</span>
                <span class="ref-metric">${refLine}</span>
            </span>
        </label>`;
}


function refreshUIState() {
    // Quét toàn bộ checkbox hiện có trên màn hình
    document.querySelectorAll('.model-option-checkbox').forEach(cb => {
        const isSelected = SELECTED_KEYS.has(cb.value);
        cb.checked = isSelected; // Ép tick ẩn
        
        const row = cb.closest('.model-option');
        if (row) {
            // Ép sáng hoặc tắt viền Vàng Kim theo đúng bộ nhớ
            if (isSelected) {
                row.classList.add('selected');
            } else {
                row.classList.remove('selected');
            }
        }
    });

    // Cập nhật số đếm góc phải
    const el = document.getElementById('selectionCount');
    if (el) {
        const n = SELECTED_KEYS.size;
        el.textContent = n === 0 ? 'Chưa chọn mô hình nào' : `Đã chọn ${n} mô hình`;
        el.classList.toggle('has-selection', n > 0);
    }
}

// Xử lý khi user click vào một mô hình
function syncCheckboxChange(e) {
    if (e.target.type !== 'checkbox') return;
    
    const modelKey = e.target.value;
    const isChecked = e.target.checked;

    // Chỉ lưu vào bộ nhớ chung
    if (isChecked) {
        SELECTED_KEYS.add(modelKey);
    } else {
        SELECTED_KEYS.delete(modelKey);
    }

    // Gọi hàm quét và đồng bộ lại toàn bộ UI
    refreshUIState();
}

function renderStageView() {
    const groups = {};
    ALL_MODELS.forEach(m => {
        if (!groups[m.group]) groups[m.group] = { label: m.group_label, order: m.group_order, items: [], isRef: m.group === 'teacher' };
        groups[m.group].items.push(m);
    });
    const ordered = Object.values(groups).sort((a, b) => a.order - b.order);

    const container = document.getElementById('dynamicModelContainer');
    container.innerHTML = ordered.map(g => `
        <div class="stage-section ${g.isRef ? 'is-reference' : ''}">
            <div class="stage-section-header">${g.isRef ? '<i class="bi bi-signpost me-1"></i>' : ''}${g.label}</div>
            <div class="stage-section-body">
                ${g.items.map(m => checkboxHtml(m)).join('')}
            </div>
        </div>
    `).join('');

    container.addEventListener('change', syncCheckboxChange);
}

function renderJourneyView() {
    const select = document.getElementById('journeyBackboneSelect');
    const journeyContainer = document.getElementById('journeyModelContainer');

    // Chỉ gắn lắng nghe sự kiện ĐÚNG 1 LẦN để không bị lag/xung đột
    journeyContainer.addEventListener('change', syncCheckboxChange);

    const backbonesPresent = [...new Set(ALL_MODELS.filter(m => m.group !== 'teacher').map(m => m.backbone))]
        .sort((a, b) => STUDENT_BACKBONE_ORDER.indexOf(a) - STUDENT_BACKBONE_ORDER.indexOf(b));

    select.innerHTML = backbonesPresent.map(bb => {
        const label = ALL_MODELS.find(m => m.backbone === bb)?.backbone_label || bb;
        return `<option value="${bb}">${label}</option>`;
    }).join('');

    const renderList = () => {
        const bb = select.value;
        const items = ALL_MODELS
            .filter(m => m.backbone === bb && m.group !== 'teacher')
            .sort((a, b) => a.group_order - b.group_order);
        journeyContainer.innerHTML = `<div class="stage-section-body">${items.map(m => {
            const ref = m.ref_metrics || {};
            const refLine = ref.f1 !== undefined ? `F1: ${refPct(ref.f1)} · Acc: ${refPct(ref.acc)} · ${m.size}` : m.size;
            return checkboxHtml(m, 'cbj', m.group_label, refLine);
        }).join('')}</div>`;
        
        // Khi vẽ lại HTML, phải gọi quét UI để thắp sáng các thẻ đã lưu
        refreshUIState();
    };

    select.addEventListener('change', renderList);
    renderList();
}

document.getElementById('btnViewStage').addEventListener('click', () => setView('stage'));
document.getElementById('btnViewJourney').addEventListener('click', () => setView('journey'));

function setView(view) {
    document.getElementById('btnViewStage').classList.toggle('active', view === 'stage');
    document.getElementById('btnViewJourney').classList.toggle('active', view === 'journey');
    document.getElementById('stageViewPanel').classList.toggle('d-none', view !== 'stage');
    document.getElementById('journeyViewPanel').classList.toggle('d-none', view !== 'journey');
    
    // Ép quét đồng bộ lại mỗi khi người dùng chuyển Tab
    refreshUIState();
}

const toggleSelectionBtn = document.getElementById('toggleSelectionBtn');
toggleSelectionBtn.addEventListener('click', () => {
    document.body.classList.toggle('selection-collapsed');
    const collapsed = document.body.classList.contains('selection-collapsed');
    toggleSelectionBtn.querySelector('i').className = collapsed ? 'bi bi-chevron-right' : 'bi bi-chevron-left';
    toggleSelectionBtn.title = collapsed ? 'Hiện bảng chọn' : 'Ẩn bảng chọn';
});

window.onload = async () => {
    try {
        const res = await fetch('http://localhost:8000/models');
        ALL_MODELS = await res.json();
        renderStageView();
        renderJourneyView();
        refreshUIState();
    } catch (err) {
        document.getElementById('dynamicModelContainer').innerHTML = '<span class="text-danger small">Lỗi kết nối Backend.</span>';
    }
};

const fileSourceInput = document.getElementById('fileSourceInput');
fileSourceInput.addEventListener('change', function (e) {
    if (e.target.files[0]) {
        const imgUrl = URL.createObjectURL(e.target.files[0]);
        document.getElementById('imagePreview').src = imgUrl;
        document.getElementById('imagePreview').style.display = 'block';
        document.getElementById('uploadPlaceholder').style.display = 'none';
        document.getElementById('heroImage').src = imgUrl;
        document.getElementById('heroImageContainer').classList.add('has-image');
    }
});

Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.1)';

function buildConceptSummary(conceptsObj) {
    const top3 = Object.entries(conceptsObj).slice(0, 3);
    if (top3.length === 0) return '';
    const describe = (score) => {
        if (score >= 0.8) return 'thể hiện rất rõ';
        if (score >= 0.6) return 'thể hiện khá rõ';
        if (score >= 0.4) return 'có dấu hiệu xuất hiện';
        return 'ít có dấu hiệu xuất hiện';
    };
    const parts = top3.map(([name, score]) =>
        `<strong>${name}</strong> (${describe(score)}, ${(score * 100).toFixed(1)}%)`
    );
    if (parts.length === 1) return `Mô hình đưa ra quyết định chủ yếu dựa trên đặc trưng ${parts[0]}.`;
    if (parts.length === 2) return `Mô hình đưa ra quyết định chủ yếu dựa trên hai đặc trưng: ${parts[0]} và ${parts[1]}.`;
    return `Mô hình đưa ra quyết định chủ yếu dựa trên các đặc trưng: ${parts[0]}, ${parts[1]} và ${parts[2]}.`;
}

document.getElementById('evaluationForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const selectedModelKeys = Array.from(SELECTED_KEYS);
    if (selectedModelKeys.length === 0) return alert("Vui lòng chọn ít nhất 1 mô hình!");
    if (!fileSourceInput.files[0]) return alert("Vui lòng tải ảnh lên!");

    const executeBtn = document.getElementById('executeBtn');
    executeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>ĐANG XỬ LÝ...';
    executeBtn.disabled = true;

    document.body.classList.add('has-results');
    toggleSelectionBtn.classList.remove('d-none');
    document.getElementById('resultsEmptyState').style.display = 'none';
    document.getElementById('chartsRow').style.display = 'flex';

    const nonCbmContainer = document.getElementById('nonCbmGridRender');
    const cbmContainer = document.getElementById('cbmGridRender');
    nonCbmContainer.innerHTML = '';
    cbmContainer.innerHTML = '';

    const fileBlob = fileSourceInput.files[0];
    let chartLabels = [], confidenceDataset = [], timeDataset = [];

    for (const modelKey of selectedModelKeys) {
        const formPayload = new FormData();
        formPayload.append('model_key', modelKey);
        formPayload.append('file', fileBlob);

        try {
            const res = await fetch('http://localhost:8000/predict', { method: 'POST', body: formPayload });
            const data = await res.json();

            const isCBM = data.concepts !== null;
            const confPercent = (data.confidence * 100).toFixed(1);

            chartLabels.push(data.model_name);
            confidenceDataset.push(parseFloat(confPercent));
            timeDataset.push(Math.round(data.inference_time_ms));

            let softLabelsHtml = '';
            data.top_3.forEach(item => {
                softLabelsHtml += `
                <div class="d-flex justify-content-between mb-2 pb-2 border-bottom" style="border-color: rgba(255,255,255,0.05) !important;">
                    <span class="small text-truncate pe-2" style="max-width: 80%; color: #cbd5e1;">${item.label}</span>
                    <span class="small fw-bold text-white">${(item.prob * 100).toFixed(1)}%</span>
                </div>
            `;
            });

            let conceptBlockHtml = '';
            if (isCBM) {
                const summaryText = buildConceptSummary(data.concepts);
                conceptBlockHtml = `
                    <h6 class="fw-bold text-success small mb-2 mt-0"><i class="bi bi-diagram-3 me-1"></i>DIỄN GIẢI KHÁI NIỆM (CBM)</h6>
                    <div class="concept-summary"><i class="bi bi-lightbulb me-1"></i>${summaryText}</div>
                    <div class="concept-list">`;
                for (const [conceptName, conceptScore] of Object.entries(data.concepts)) {
                    const scorePercent = (conceptScore * 100).toFixed(1);
                    const barColor = conceptScore > 0.6 ? 'bg-success' : 'bg-warning';
                    conceptBlockHtml += `
                    <div class="concept-item">
                        <span class="concept-text pe-2" title="${conceptName}">${conceptName}</span>
                        <div>
                            <div class="d-flex justify-content-between align-items-end mb-1">
                                <span style="font-size: 0.65rem; color: transparent;">-</span>
                                <span class="badge ${barColor} text-dark">${scorePercent}%</span>
                            </div>
                            <div class="progress progress-slim">
                                <div class="progress-bar ${barColor}" style="width: ${scorePercent}%"></div>
                            </div>
                        </div>
                    </div>
                `;
                }
                conceptBlockHtml += `</div>`;
            }

            const ref = data.ref_metrics || {};
            const refBadgeHtml = ref.f1 !== undefined
                ? `<div class="ref-compare mb-2"><i class="bi bi-journal-bookmark me-1"></i>Theo luận văn: F1 ${(ref.f1 * 100).toFixed(2)}% · Acc ${(ref.acc * 100).toFixed(2)}%</div>`
                : '';
            
            const stagePillHtml = `<div class="stage-pill mt-0">${data.group_label || ''}</div>`;
            const sizeTimeBadgesHtml = `
                <div class="d-flex gap-2 mb-2 flex-wrap">
                    <span class="badge bg-secondary bg-opacity-25 text-light border border-secondary"><i class="bi bi-hdd me-1"></i>${data.metrics.size}</span>
                    <span class="badge bg-info bg-opacity-25 text-info border border-info"><i class="bi bi-lightning-charge me-1"></i>${data.inference_time_ms.toFixed(0)} ms</span>
                </div>`;

            if (isCBM) {
                cbmContainer.innerHTML += `
                <div class="model-card-wide">
                    <div class="model-card-left">
                        ${stagePillHtml}
                        <h6 class="fw-bold text-white mt-1 mb-2" title="${data.model_name}">${data.model_name}</h6>
                        ${refBadgeHtml}
                        ${sizeTimeBadgesHtml}
                        <div class="p-3 rounded mb-3" style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.05);">
                            <span class="text-uppercase text-muted d-block" style="font-size: 0.7rem;">Kết quả phân loại</span>
                            <span class="d-block mt-1 mb-2 fw-bold fs-5 text-uppercase ${data.confidence > 0.8 ? 'text-success' : 'text-warning'}">${data.prediction}</span>
                            <span class="badge bg-primary px-2 py-1 small">Tự tin: ${confPercent}%</span>
                        </div>
                        <h6 class="fw-bold text-info small mb-3"><i class="bi bi-bar-chart me-1"></i>TOP 3 PHÂN PHỐI</h6>
                        <div>${softLabelsHtml}</div>
                    </div>
                    <div class="model-card-right">
                        ${conceptBlockHtml}
                    </div>
                </div>`;
            } else {
                nonCbmContainer.innerHTML += `
                <div class="model-card-compact">
                    <div>
                        ${stagePillHtml}
                        <h6 title="${data.model_name}" class="mt-1">${data.model_name}</h6>
                        ${refBadgeHtml}
                        ${sizeTimeBadgesHtml}
                    </div>
                    <div class="mt-auto-wrapper">
                        <div class="result-box">
                            <span class="text-uppercase text-muted d-block" style="font-size: 0.65rem;">Kết quả phân loại</span>
                            <span class="pred-label ${data.confidence > 0.8 ? 'text-success' : 'text-warning'}">${data.prediction}</span>
                            <span class="badge bg-primary px-2 py-1 small">Tự tin: ${confPercent}%</span>
                        </div>
                        <div>${data.top_3.map(item => `
                            <div class="top3-row">
                                <span class="text-truncate pe-2" style="max-width:75%;">${item.label}</span>
                                <span class="fw-bold text-white">${(item.prob * 100).toFixed(1)}%</span>
                            </div>`).join('')}
                        </div>
                    </div>
                </div>`;
            }
        } catch (err) {
            console.error(err);
            nonCbmContainer.innerHTML += `<div class="alert alert-danger bg-danger text-white border-0 small"><i class="bi bi-exclamation-triangle me-1"></i>Lỗi API mô hình.</div>`;
        }
    }

    renderCharts(chartLabels, confidenceDataset, timeDataset);

    executeBtn.innerHTML = '<i class="bi bi-play-fill me-1"></i>Phân Tích Đối Chứng';
    executeBtn.disabled = false;
});

function renderCharts(labels, confData, timeData) {
    if (globalCharts['conf']) globalCharts['conf'].destroy();
    if (globalCharts['time']) globalCharts['time'].destroy();

    const barSlot = 42;
    const dynamicHeight = Math.max(220, labels.length * barSlot);
    document.querySelectorAll('.chart-canvas').forEach(el => el.style.height = dynamicHeight + 'px');

    const ctxConf = document.getElementById('confChart').getContext('2d');
    globalCharts['conf'] = new Chart(ctxConf, {
        type: 'bar',
        data: { labels: labels, datasets: [{ data: confData, backgroundColor: 'rgba(197, 168, 92, 0.85)', borderColor: '#e6c875', borderWidth: 1, borderRadius: 4 }] },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { max: 100 } } }
    });

    const ctxTime = document.getElementById('timeChart').getContext('2d');
    globalCharts['time'] = new Chart(ctxTime, {
        type: 'bar',
        data: { labels: labels, datasets: [{ data: timeData, backgroundColor: 'rgba(16, 185, 129, 0.85)', borderColor: '#34d399', borderWidth: 1, borderRadius: 4 }] },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });
}