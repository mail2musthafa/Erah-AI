// State
let vecA = { x: 3.0, y: 2.0 };
let vecB = { x: 1.0, y: 4.0 };
let draggingVec = null;
let completedExercises = new Set();

const canvas = document.getElementById("vectorCanvas");
const ctx = canvas.getContext("2d");
const width = canvas.width;
const height = canvas.height;
const origin = { x: width / 2, y: height / 2 };
const scale = 40; // 40px per 1 unit

// Initialize Tab switching
document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
        btn.classList.add("active");
        const tabId = "tab-" + btn.getAttribute("data-tab");
        const target = document.getElementById(tabId);
        if (target) target.classList.add("active");
        if (btn.getAttribute("data-tab") === "math-breakdown") {
            renderMathBreakdown();
        }
    });
});

// Inputs
const axInput = document.getElementById("ax");
const ayInput = document.getElementById("ay");
const bxInput = document.getElementById("bx");
const byInput = document.getElementById("by");

function updateFromInputs() {
    vecA.x = parseFloat(axInput.value) || 0;
    vecA.y = parseFloat(ayInput.value) || 0;
    vecB.x = parseFloat(bxInput.value) || 0;
    vecB.y = parseFloat(byInput.value) || 0;
    renderAll();
}

[axInput, ayInput, bxInput, byInput].forEach(inp => {
    inp.addEventListener("input", updateFromInputs);
});

function setVectors(ax, ay, bx, by) {
    axInput.value = ax;
    ayInput.value = ay;
    bxInput.value = bx;
    byInput.value = by;
    updateFromInputs();
}

// Math Calculations
function computeMetrics(a, b) {
    const dot = a.x * b.x + a.y * b.y;
    const normA = Math.sqrt(a.x * a.x + a.y * a.y);
    const normB = Math.sqrt(b.x * b.x + b.y * b.y);
    const cosSim = (normA === 0 || normB === 0) ? 0 : Math.max(-1, Math.min(1, dot / (normA * normB)));
    const angleRad = Math.acos(cosSim);
    const angleDeg = (angleRad * 180) / Math.PI;
    const eucDist = Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2);

    return { dot, normA, normB, cosSim, angleDeg, eucDist };
}

// Update DOM Metrics
function updateMetricsUI(m) {
    document.getElementById("val-dot").innerText = m.dot.toFixed(2);
    document.getElementById("val-cos").innerText = m.cosSim.toFixed(3);
    document.getElementById("val-angle").innerText = m.angleDeg.toFixed(1) + "°";
    document.getElementById("val-euc").innerText = m.eucDist.toFixed(2);
    document.getElementById("val-norm-a").innerText = m.normA.toFixed(2);
    document.getElementById("val-norm-b").innerText = m.normB.toFixed(2);
}

// Canvas Drawing
function toCanvasX(x) { return origin.x + x * scale; }
function toCanvasY(y) { return origin.y - y * scale; }
function toMathX(cx) { return (cx - origin.x) / scale; }
function toMathY(cy) { return (origin.y - cy) / scale; }

function drawGrid() {
    ctx.clearRect(0, 0, width, height);

    // Minor Grid Lines
    ctx.strokeStyle = "#131C2E";
    ctx.lineWidth = 1;
    for (let x = 0; x <= width; x += scale) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, height); ctx.stroke();
    }
    for (let y = 0; y <= height; y += scale) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke();
    }

    // Axes
    ctx.strokeStyle = "#334155";
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(0, origin.y); ctx.lineTo(width, origin.y); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(origin.x, 0); ctx.lineTo(origin.x, height); ctx.stroke();

    // Unit Circle (Radius 1)
    ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.arc(origin.x, origin.y, scale, 0, 2 * Math.PI);
    ctx.stroke();
    ctx.setLineDash([]);
}

function drawVector(vec, color, label) {
    const endX = toCanvasX(vec.x);
    const endY = toCanvasY(vec.y);

    // Vector line
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = 3;

    ctx.beginPath();
    ctx.moveTo(origin.x, origin.y);
    ctx.lineTo(endX, endY);
    ctx.stroke();

    // Arrowhead
    const angle = Math.atan2(origin.y - endY, endX - origin.x);
    const headLen = 12;
    ctx.beginPath();
    ctx.moveTo(endX, endY);
    ctx.lineTo(
        endX - headLen * Math.cos(angle - Math.PI / 6),
        endY + headLen * Math.sin(angle - Math.PI / 6)
    );
    ctx.lineTo(
        endX - headLen * Math.cos(angle + Math.PI / 6),
        endY + headLen * Math.sin(angle + Math.PI / 6)
    );
    ctx.closePath();
    ctx.fill();

    // Handle handle circle for dragging
    ctx.beginPath();
    ctx.arc(endX, endY, 6, 0, 2 * Math.PI);
    ctx.fill();

    // Label
    ctx.font = "600 13px 'JetBrains Mono', monospace";
    ctx.fillText(`${label} (${vec.x.toFixed(1)}, ${vec.y.toFixed(1)})`, endX + 10, endY - 10);
}

function drawAngleArc(a, b, m) {
    if (m.normA === 0 || m.normB === 0) return;
    const angleA = Math.atan2(a.y, a.x);
    const angleB = Math.atan2(b.y, b.x);

    ctx.strokeStyle = "#F59E0B";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(origin.x, origin.y, 35, -angleA, -angleB, angleA < angleB);
    ctx.stroke();

    // Label Theta
    ctx.fillStyle = "#F59E0B";
    ctx.font = "12px 'Plus Jakarta Sans', sans-serif";
    ctx.fillText(`θ = ${m.angleDeg.toFixed(0)}°`, origin.x + 40, origin.y - 10);
}

function renderAll() {
    drawGrid();
    const metrics = computeMetrics(vecA, vecB);
    drawAngleArc(vecA, vecB, metrics);
    drawVector(vecA, "#3B82F6", "A");
    drawVector(vecB, "#A855F7", "B");
    updateMetricsUI(metrics);
}

// Mouse dragging on canvas
canvas.addEventListener("mousedown", (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    const distA = Math.hypot(mx - toCanvasX(vecA.x), my - toCanvasY(vecA.y));
    const distB = Math.hypot(mx - toCanvasX(vecB.x), my - toCanvasY(vecB.y));

    if (distA < 20) draggingVec = "A";
    else if (distB < 20) draggingVec = "B";
});

window.addEventListener("mousemove", (e) => {
    if (!draggingVec) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    const rawX = Math.round(toMathX(mx) * 2) / 2;
    const rawY = Math.round(toMathY(my) * 2) / 2;

    const clampedX = Math.max(-5, Math.min(5, rawX));
    const clampedY = Math.max(-5, Math.min(5, rawY));

    if (draggingVec === "A") {
        vecA.x = clampedX; vecA.y = clampedY;
        axInput.value = clampedX; ayInput.value = clampedY;
    } else {
        vecB.x = clampedX; vecB.y = clampedY;
        bxInput.value = clampedX; byInput.value = clampedY;
    }
    renderAll();
});

window.addEventListener("mouseup", () => { draggingVec = null; });

// Step-by-Step Math Breakdown Renderer
function renderMathBreakdown() {
    const m = computeMetrics(vecA, vecB);
    const container = document.getElementById("mathSteps");

    container.innerHTML = `
        <!-- Step 1: Vectors -->
        <div class="math-step-block">
            <div class="math-step-title">Step 1: Define the Input Vectors in 2D Space</div>
            <div class="formula-display">
                Vector A = [${vecA.x.toFixed(1)}, ${vecA.y.toFixed(1)}]<br>
                Vector B = [${vecB.x.toFixed(1)}, ${vecB.y.toFixed(1)}]
            </div>
            <p class="math-explanation">
                In an LLM or embedding model, these vectors have 768 to 4096 dimensions instead of 2. But the exact same math applies!
            </p>
        </div>

        <!-- Step 2: Dot Product -->
        <div class="math-step-block">
            <div class="math-step-title">Step 2: Calculate the Dot Product (A · B)</div>
            <div class="formula-display">
                A · B = (Ax × Bx) + (Ay × By)<br>
                A · B = (${vecA.x.toFixed(1)} × ${vecB.x.toFixed(1)}) + (${vecA.y.toFixed(1)} × ${vecB.y.toFixed(1)})<br>
                A · B = ${(vecA.x * vecB.x).toFixed(2)} + ${(vecA.y * vecB.y).toFixed(2)} = <strong>${m.dot.toFixed(2)}</strong>
            </div>
            <p class="math-explanation">
                The dot product multiplies corresponding coordinates. A higher positive value means the vectors point in a similar direction.
            </p>
        </div>

        <!-- Step 3: L2 Norms -->
        <div class="math-step-block">
            <div class="math-step-title">Step 3: Calculate Vector Magnitudes (L2 Norms)</div>
            <div class="formula-display">
                ||A|| = √(Ax² + Ay²) = √(${vecA.x.toFixed(1)}² + ${vecA.y.toFixed(1)}²) = √${(vecA.x**2 + vecA.y**2).toFixed(2)} = <strong>${m.normA.toFixed(2)}</strong><br>
                ||B|| = √(Bx² + By²) = √(${vecB.x.toFixed(1)}² + ${vecB.y.toFixed(1)}²) = √${(vecB.x**2 + vecB.y**2).toFixed(2)} = <strong>${m.normB.toFixed(2)}</strong>
            </div>
            <p class="math-explanation">
                The L2 Norm is the geometric length of the vector from the origin (0, 0).
            </p>
        </div>

        <!-- Step 4: Cosine Similarity -->
        <div class="math-step-block">
            <div class="math-step-title">Step 4: Compute Cosine Similarity (cos θ)</div>
            <div class="formula-display">
                cos(θ) = (A · B) / (||A|| × ||B||)<br>
                cos(θ) = ${m.dot.toFixed(2)} / (${m.normA.toFixed(2)} × ${m.normB.toFixed(2)})<br>
                cos(θ) = ${m.dot.toFixed(2)} / ${(m.normA * m.normB).toFixed(2)} = <strong style="color: #06B6D4;">${m.cosSim.toFixed(3)}</strong>
            </div>
            <p class="math-explanation">
                By dividing by vector magnitudes, we eliminate vector length differences. 
                Angle θ = arccos(${m.cosSim.toFixed(3)}) = <strong>${m.angleDeg.toFixed(1)}°</strong>.
            </p>
        </div>

        <!-- Step 5: Euclidean Distance -->
        <div class="math-step-block">
            <div class="math-step-title">Step 5: Compute Euclidean Distance (Straight-line Distance)</div>
            <div class="formula-display">
                d(A, B) = √((Ax - Bx)² + (Ay - By)²)<br>
                d(A, B) = √(${vecA.x.toFixed(1)} - ${vecB.x.toFixed(1)})² + (${vecA.y.toFixed(1)} - ${vecB.y.toFixed(1)})² = <strong>${m.eucDist.toFixed(2)}</strong>
            </div>
        </div>
    `;
}

// Real-World Text Similarity Engine
function setTextPreset(type) {
    const textA = document.getElementById("textA");
    const textB = document.getElementById("textB");

    if (type === "billing") {
        textA.value = "How can I request a refund for my subscription charge?";
        textB.value = "Please issue an invoice and refund receipt for my payment.";
    } else if (type === "cross") {
        textA.value = "How can I request a refund for my billing charge?";
        textB.value = "The backend PostgreSQL database failed with timeout connection error.";
    } else if (type === "tech") {
        textA.value = "Database connection timed out with internal server error 500.";
        textB.value = "The backend API server crashed and WebSocket disconnected.";
    } else if (type === "sales") {
        textA.value = "What is the enterprise pricing for 50 team member seats?";
        textB.value = "Can we get an annual enterprise discount quote for our team?";
    }
    computeTextSim();
}

function computeTextSim() {
    const s1 = document.getElementById("textA").value.trim();
    const s2 = document.getElementById("textB").value.trim();

    // Simple Tokenizer + Bag of Words
    const words1 = s1.toLowerCase().replace(/[^\w\s]/g, "").split(/\s+/).filter(Boolean);
    const words2 = s2.toLowerCase().replace(/[^\w\s]/g, "").split(/\s+/).filter(Boolean);

    const vocab = Array.from(new Set([...words1, ...words2]));

    // Term Frequency Vectors
    const v1 = vocab.map(w => words1.filter(x => x === w).length);
    const v2 = vocab.map(w => words2.filter(x => x === w).length);

    // Cosine similarity
    let dot = 0, n1 = 0, n2 = 0;
    for (let i = 0; i < vocab.length; i++) {
        dot += v1[i] * v2[i];
        n1 += v1[i] * v1[i];
        n2 += v2[i] * v2[i];
    }
    const norm1 = Math.sqrt(n1);
    const norm2 = Math.sqrt(n2);
    const sim = (norm1 === 0 || norm2 === 0) ? 0 : dot / (norm1 * norm2);

    const sharedWords = vocab.filter((w, i) => v1[i] > 0 && v2[i] > 0);

    const area = document.getElementById("textResultsArea");
    area.innerHTML = `
        <div class="result-card-box">
            <h3 style="margin-bottom: 12px; font-size: 16px; color: #818CF8;">Text Embedding & Vector Similarity Result</h3>
            <div style="display: flex; gap: 24px; align-items: center; margin-bottom: 16px;">
                <div>
                    <div style="font-size: 12px; color: #94A3B8;">Cosine Similarity Score</div>
                    <div style="font-size: 32px; font-weight: 800; font-family: var(--font-mono); color: ${sim > 0.4 ? '#10B981' : sim > 0.1 ? '#F59E0B' : '#EF4444'};">
                        ${sim.toFixed(4)}
                    </div>
                </div>
                <div style="border-left: 1px solid rgba(255,255,255,0.1); padding-left: 20px;">
                    <div style="font-size: 13px; color: #F8FAFC;">
                        ${sim > 0.4 ? '✅ <strong>High Semantic Match:</strong> Both queries share the same core intent!' :
                          sim > 0.1 ? '⚠️ <strong>Partial Overlap:</strong> Sentences share minor vocabulary.' :
                          '❌ <strong>Dissimilar Intents:</strong> Queries belong to completely different topics.'}
                    </div>
                    <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">
                        Shared Vocabulary: <strong>${sharedWords.length > 0 ? sharedWords.join(', ') : 'None'}</strong>
                    </div>
                </div>
            </div>
            <div style="font-size: 12px; font-family: var(--font-mono); color: #64748B; background: rgba(0,0,0,0.3); padding: 8px 12px; border-radius: 6px;">
                Vocab Dimension size = ${vocab.length} unique tokens across both sentences.
            </div>
        </div>
    `;
}

document.getElementById("btnComputeText").addEventListener("click", computeTextSim);

// Exercises Logic
function checkEx1() {
    const val = parseFloat(document.getElementById("ex1-ans").value);
    const fb = document.getElementById("ex1-fb");
    // u=[4,3], v=[2,-1] -> dot = (4*2) + (3*-1) = 8 - 3 = 5
    if (val === 5) {
        fb.className = "ex-feedback correct";
        fb.innerHTML = "✓ Correct! (4 × 2) + (3 × -1) = 8 - 3 = 5.";
        completedExercises.add(1);
    } else {
        fb.className = "ex-feedback incorrect";
        fb.innerHTML = "✗ Not quite. Multiply matching components: (4 × 2) + (3 × -1) = 8 - 3 = ?";
    }
    updateExerciseScore();
}

function checkEx2() {
    const val = parseFloat(document.getElementById("ex2-ans").value);
    const fb = document.getElementById("ex2-fb");
    // a=[3,4] -> norm = sqrt(9 + 16) = sqrt(25) = 5
    if (val === 5) {
        fb.className = "ex-feedback correct";
        fb.innerHTML = "✓ Correct! ||a|| = √(3² + 4²) = √(9 + 16) = √25 = 5.";
        completedExercises.add(2);
    } else {
        fb.className = "ex-feedback incorrect";
        fb.innerHTML = "✗ Try again. Calculate √(3² + 4²) = √(9 + 16) = ?";
    }
    updateExerciseScore();
}

function checkEx3(btn, isCorrect) {
    const fb = document.getElementById("ex3-fb");
    if (isCorrect) {
        fb.className = "ex-feedback correct";
        fb.innerHTML = "✓ Correct! Cosine Similarity = 0 means angle θ = 90° (orthogonal), indicating zero shared direction/unrelated semantic context.";
        completedExercises.add(3);
    } else {
        fb.className = "ex-feedback incorrect";
        fb.innerHTML = "✗ Incorrect. Recall that cos(90°) = 0, which corresponds to orthogonal (perpendicular) vectors.";
    }
    updateExerciseScore();
}

function checkEx4(btn, isCorrect) {
    const fb = document.getElementById("ex4-fb");
    if (isCorrect) {
        fb.className = "ex-feedback correct";
        fb.innerHTML = "✓ Correct! Length of [0, 5] is 5. Dividing each component by 5 yields unit vector [0, 1].";
        completedExercises.add(4);
    } else {
        fb.className = "ex-feedback incorrect";
        fb.innerHTML = "✗ Remember: To normalize, divide each element by the magnitude ||v|| = 5.";
    }
    updateExerciseScore();
}

function updateExerciseScore() {
    document.getElementById("exerciseScore").innerText = completedExercises.size;
}

// Initial Run
renderAll();
computeTextSim();
