document.addEventListener(
    "DOMContentLoaded",
    async () => {

        showPage("dashboard");
const dashboardDate =
    document.getElementById("dashboardCurrentDate");

if (dashboardDate) {
    dashboardDate.textContent =
        new Intl.DateTimeFormat(
            "fr-FR",
            {
                weekday: "long",
                day: "2-digit",
                month: "long",
                year: "numeric"
            }
        ).format(new Date());
}
        await loadDashboard();

        loadUsers();
        loadEmployees();
        loadDocuments();
        loadClients();
        loadStock();
        loadMaintenance();
        loadAlerts();
        loadAgenda();

        initCalendar();

    }
);
function showPage(pageName) {

    document.querySelectorAll(".page").forEach(page => {
        page.classList.remove("active");
    });

    document.querySelectorAll("#sidebar nav a").forEach(link => {
        link.classList.remove("active");
    });

    const selectedPage = document.getElementById(`page-${pageName}`);

    if (!selectedPage) {
        console.error("Page introuvable :", pageName);
        return;
    }

    selectedPage.classList.add("active");

    const selectedLink = document.getElementById(`nav-${pageName}`);

    if (selectedLink) {
        selectedLink.classList.add("active");
    }

    const titles = {
        dashboard: "Tableau de bord",
        employees: "Gestion des employés",
        documents: "Gestion documentaire",
        clients: "Gestion des clients",
        stock: "Stock aéronautique",
        maintenance: "Gestion de la maintenance",
        agenda: "Agenda",
        ocr: "OCR",
        signatures: "Signatures",
        users: "Gestion des utilisateurs",
        alerts: "Centre des alertes"
    };

    const title = document.getElementById("page-title");

    if (title) {
        title.textContent = titles[pageName] || "AeroDoc";
    }
    if (pageName === "alerts") {
    loadAlerts();
}
}
/* =====================================================
   TABLEAU DE BORD
===================================================== */

const dashboardCharts = {
    compliance: null,
    qualifications: null,
    topParts: null,
    stock: null
};

function setDashboardValue(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value ?? 0;
    }
}

function destroyDashboardChart(chartName) {
    if (dashboardCharts[chartName]) {
        dashboardCharts[chartName].destroy();
        dashboardCharts[chartName] = null;
    }
}

function createEmptyChartMessage(canvasId, message) {
    const canvas = document.getElementById(canvasId);

    if (!canvas) {
        return;
    }

    const parent = canvas.parentElement;
    let emptyMessage = parent.querySelector(".chart-empty-message");

    if (!emptyMessage) {
        emptyMessage = document.createElement("div");
        emptyMessage.className = "chart-empty-message";
        parent.appendChild(emptyMessage);
    }

    emptyMessage.textContent = message;
    emptyMessage.style.display = "flex";
    canvas.style.display = "none";
}

function showChartCanvas(canvasId) {
    const canvas = document.getElementById(canvasId);

    if (!canvas) {
        return;
    }

    canvas.style.display = "block";

    const emptyMessage =
        canvas.parentElement.querySelector(".chart-empty-message");

    if (emptyMessage) {
        emptyMessage.style.display = "none";
    }
}

async function loadDashboard() {
    try {
        const response = await fetch("/api/dashboard/");

        if (!response.ok) {
            throw new Error(
                `Erreur HTTP ${response.status}`
            );
        }

        const data = await response.json();

        /* KPI principaux */

        setDashboardValue(
            "kpiEmployees",
            data.total_employes
        );

        setDashboardValue(
            "kpiDocuments",
            data.total_documents
        );

        setDashboardValue(
            "kpiClients",
            data.total_clients
        );

        setDashboardValue(
            "kpiMaintenance",
            data.total_maintenances
        );

        setDashboardValue(
            "kpiAlerts",
            data.active_alerts
        );

        /* KPI avancés */

        setDashboardValue(
            "kpiStock",
            data.stock_total
        );

        setDashboardValue(
            "kpiCriticalParts",
            data.pieces_critiques
        );

        setDashboardValue(
            "kpiOutParts",
            data.pieces_rupture
        );

        setDashboardValue(
            "kpiValidDocs",
            data.valid_documents
        );

        setDashboardValue(
            "kpiRenewDocs",
            data.renew_documents
        );

        setDashboardValue(
            "topAlertCount",
            data.active_alerts
        );

        renderComplianceChart(data);
        renderQualificationsChart(data);
        renderTopPartsChart(data);
        renderStockChart(data);

    } catch (error) {
        console.error(
            "Impossible de charger le tableau de bord :",
            error
        );
    }
}


/* =====================================================
   GRAPHIQUE DOCUMENTS
===================================================== */

function renderComplianceChart(data) {
    const canvas =
        document.getElementById("chartCompliance");

    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    destroyDashboardChart("compliance");
    showChartCanvas("chartCompliance");

    dashboardCharts.compliance =
        new Chart(canvas, {
            type: "doughnut",

            data: {
                labels: [
                    "Valides",
                    "À renouveler",
                    "Expirés"
                ],

                datasets: [{
                    data: [
                        Number(data.valid_documents || 0),
                        Number(data.renew_documents || 0),
                        Number(data.expired_documents || 0)
                    ],

                    backgroundColor: [
                        "#22C55E",
                        "#F59E0B",
                        "#EF4444"
                    ],

                    borderColor: "#FFFFFF",
                    borderWidth: 4,
                    hoverOffset: 8
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "67%",

                plugins: {
                    legend: {
                        position: "bottom",

                        labels: {
                            usePointStyle: true,
                            pointStyle: "circle",
                            padding: 20,
                            font: {
                                size: 13
                            }
                        }
                    },

                    tooltip: {
                        callbacks: {
                            label(context) {
                                return `${context.label} : ${context.raw}`;
                            }
                        }
                    }
                }
            }
        });
}


/* =====================================================
   GRAPHIQUE QUALIFICATIONS
===================================================== */

function renderQualificationsChart(data) {
    const canvas =
        document.getElementById("chartQualifications");

    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    const qualifications =
        Array.isArray(data.qualifications)
            ? data.qualifications
            : [];

    destroyDashboardChart("qualifications");

    if (qualifications.length === 0) {
        createEmptyChartMessage(
            "chartQualifications",
            "Aucune qualification enregistrée."
        );
        return;
    }

    showChartCanvas("chartQualifications");

    dashboardCharts.qualifications =
        new Chart(canvas, {
            type: "bar",

            data: {
                labels: qualifications.map(
                    item =>
                        item.nom_qualification ||
                        "Non renseignée"
                ),

                datasets: [{
                    label: "Nombre d’employés",

                    data: qualifications.map(
                        item => Number(item.total || 0)
                    ),

                    backgroundColor: "#7C3AED",
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                scales: {
                    y: {
                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        },

                        grid: {
                            color: "#EEF2F7"
                        }
                    },

                    x: {
                        grid: {
                            display: false
                        }
                    }
                },

                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
}


/* =====================================================
   GRAPHIQUE PIÈCES UTILISÉES
===================================================== */

function renderTopPartsChart(data) {
    const canvas =
        document.getElementById("chartTopParts");

    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    const parts =
        Array.isArray(data.top_pieces)
            ? data.top_pieces.slice(0, 7)
            : [];

    destroyDashboardChart("topParts");

    if (parts.length === 0) {
        createEmptyChartMessage(
            "chartTopParts",
            "Aucune utilisation de pièce validée."
        );
        return;
    }

    showChartCanvas("chartTopParts");

    dashboardCharts.topParts =
        new Chart(canvas, {
            type: "bar",

            data: {
                labels: parts.map(
                    item =>
                        item.designation ||
                        "Pièce inconnue"
                ),

                datasets: [{
                    label: "Quantité utilisée",

                    data: parts.map(
                        item => Number(item.total || 0)
                    ),

                    backgroundColor: "#185FA5",
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },

            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,

                scales: {
                    x: {
                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        },

                        grid: {
                            color: "#EEF2F7"
                        }
                    },

                    y: {
                        grid: {
                            display: false
                        }
                    }
                },

                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
}


/* =====================================================
   GRAPHIQUE STOCK ET MAINTENANCE
===================================================== */

function renderStockChart(data) {
    const canvas =
        document.getElementById("chartStock");

    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    destroyDashboardChart("stock");
    showChartCanvas("chartStock");

    dashboardCharts.stock =
        new Chart(canvas, {
            type: "bar",

            data: {
                labels: [
                    "Stock total",
                    "Pièces critiques",
                    "Ruptures",
                    "Maintenances planifiées",
                    "Maintenances en cours"
                ],

                datasets: [{
                    label: "Valeur",

                    data: [
                        Number(data.stock_total || 0),
                        Number(data.pieces_critiques || 0),
                        Number(data.pieces_rupture || 0),
                        Number(data.maint_planifiees || 0),
                        Number(data.maint_en_cours || 0)
                    ],

                    backgroundColor: [
                        "#185FA5",
                        "#F59E0B",
                        "#EF4444",
                        "#7C3AED",
                        "#06B6D4"
                    ],

                    borderRadius: 9,
                    borderSkipped: false
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                scales: {
                    y: {
                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        },

                        grid: {
                            color: "#EEF2F7"
                        }
                    },

                    x: {
                        grid: {
                            display: false
                        },

                        ticks: {
                            maxRotation: 30,
                            minRotation: 0
                        }
                    }
                },

                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
}
async function loadUsers(){

    const r =
        await fetch(
            "/api/users/"
        );

    const data =
        await r.json();

    let html = "";

    data.forEach(u=>{

        html += `
        <tr>

            <td>${u.nom || ''}</td>

            <td>${u.prenom || ''}</td>

            <td>${u.login}</td>

            <td>${u.role}</td>

            <td>${u.statut}</td>

        </tr>
        `;

    });

    const body =
        document.getElementById(
            "usersTableBody"
        );

    if(body){

        body.innerHTML = html;

    }
}
async function loadEmployees(){

    const r =
        await fetch(
            "/api/employees/"
        );

    const data =
        await r.json();

    let html="";

    data.forEach(e=>{

        html += `
        <tr>

            <td>${e.matricule}</td>

            <td>${e.nom}</td>

            <td>${e.prenom}</td>

            <td>${e.fonction}</td>

            <td>${e.statut}</td>

        </tr>
        `;

    });

    const body =
        document.getElementById(
            "employeesTableBody"
        );

    if(body){

        body.innerHTML = html;

    }
}
async function loadDocuments(){

    const r =
        await fetch(
            "/api/documents/"
        );

    const data =
        await r.json();

    let html="";

    data.forEach(d=>{

        html += `
        <tr>

            <td>${d.nom_fichier}</td>

            <td>${d.type_document}</td>

            <td>${d.statut}</td>

            <td>${d.date_expiration || ''}</td>

        </tr>
        `;

    });

    const body =
        document.getElementById(
            "documentsTableBody"
        );

    if(body){

        body.innerHTML = html;

    }
}
async function loadClients(){

    const r =
        await fetch(
            "/api/clients/"
        );

    const data =
        await r.json();

    let html="";

    data.forEach(c=>{

        html += `
        <tr>

            <td>${c.nom_societe}</td>

            <td>${c.contact_principal}</td>

            <td>${c.telephone}</td>

            <td>${c.email}</td>

            <td>${c.type_aeronef}</td>

        </tr>
        `;

    });

    const body =
        document.getElementById(
            "clientsTableBody"
        );

    if(body){

        body.innerHTML = html;

    }
}
async function loadStock(){

    const r =
        await fetch(
            "/api/stock/pieces"
        );

    const data =
        await r.json();

    let html="";

    data.forEach(p=>{

        html += `
        <tr>

            <td>${p.reference_piece}</td>

            <td>${p.designation}</td>

            <td>${p.categorie}</td>

            <td>${p.quantite_stock}</td>

            <td>${p.stock_alerte}</td>

        </tr>
        `;

    });

    const body =
        document.getElementById(
            "stockTableBody"
        );

    if(body){

        body.innerHTML = html;

    }
}
async function loadMaintenance(){

    const r =
        await fetch(
            "/api/maintenance/"
        );

    const data =
        await r.json();

    let html="";

    data.forEach(m=>{

        html += `
        <tr>

            <td>${m.reference_fiche}</td>

            <td>${m.type_aeronef}</td>

            <td>${m.immatriculation}</td>

            <td>${m.type_maintenance}</td>

            <td>${m.statut}</td>

        </tr>
        `;

    });

    const body =
        document.getElementById(
            "maintenanceTableBody"
        );

    if(body){

        body.innerHTML = html;

    }
}
let allAlerts = [];


function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function normalizeAlertLevel(level) {
    return String(level || "INFO").toUpperCase();
}


function normalizeAlertStatus(status) {
    return String(status || "OUVERTE").toUpperCase();
}


function formatAlertDate(value) {
    if (!value) {
        return "Date non renseignée";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return new Intl.DateTimeFormat(
        "fr-FR",
        {
            day: "2-digit",
            month: "short",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        }
    ).format(date);
}


function getAlertIcon(level) {
    const icons = {
        CRITIQUE: "fa-circle-exclamation",
        ATTENTION: "fa-triangle-exclamation",
        INFO: "fa-circle-info"
    };

    return icons[level] || "fa-bell";
}


function updateAlertCounters(alerts) {
    const opened = alerts.filter(
        alert =>
            normalizeAlertStatus(alert.statut) === "OUVERTE"
    );

    const critical = opened.filter(
        alert =>
            normalizeAlertLevel(alert.niveau) === "CRITIQUE"
    ).length;

    const warning = opened.filter(
        alert =>
            normalizeAlertLevel(alert.niveau) === "ATTENTION"
    ).length;

    const info = opened.filter(
        alert =>
            normalizeAlertLevel(alert.niveau) === "INFO"
    ).length;

    setDashboardValue("criticalAlertsCount", critical);
    setDashboardValue("warningAlertsCount", warning);
    setDashboardValue("infoAlertsCount", info);
    setDashboardValue("openAlertsCount", opened.length);

    setDashboardValue("topAlertCount", opened.length);
    setDashboardValue("sidebarAlertCount", opened.length);
    setDashboardValue("kpiAlerts", opened.length);

    const topButton =
        document.getElementById("topAlertButton");

    if (topButton) {
        topButton.classList.toggle(
            "has-alerts",
            opened.length > 0
        );
    }
}


function renderAlerts(alerts) {
    const container =
        document.getElementById("alertsList");

    if (!container) {
        return;
    }

    if (!alerts.length) {
        container.innerHTML = `
            <div class="alerts-empty">
                <div class="alerts-empty-icon">
                    <i class="fa-solid fa-circle-check"></i>
                </div>

                <h3>Aucune alerte trouvée</h3>

                <p>
                    Aucun élément ne correspond aux filtres sélectionnés.
                </p>
            </div>
        `;

        return;
    }

    container.innerHTML = alerts
        .map(alert => {
            const level =
                normalizeAlertLevel(alert.niveau);

            const status =
                normalizeAlertStatus(alert.statut);

            return `
                <article
                    class="alert-item alert-${level.toLowerCase()}"
                    data-level="${escapeHtml(level)}"
                    data-status="${escapeHtml(status)}"
                >
                    <div class="alert-item-icon">
                        <i class="fa-solid ${getAlertIcon(level)}"></i>
                    </div>

                    <div class="alert-item-content">

                        <div class="alert-item-header">
                            <div>
                                <span class="alert-level-badge">
                                    ${escapeHtml(level)}
                                </span>

                                <span class="alert-status-badge status-${status.toLowerCase()}">
                                    ${escapeHtml(status)}
                                </span>
                            </div>

                            <time>
                                <i class="fa-regular fa-clock"></i>
                                ${escapeHtml(
                                    formatAlertDate(
                                        alert.date_creation
                                    )
                                )}
                            </time>
                        </div>

                        <h3>
                            ${escapeHtml(
                                alert.titre || "Alerte"
                            )}
                        </h3>

                        <p>
                            ${escapeHtml(
                                alert.message ||
                                "Aucun détail disponible."
                            )}
                        </p>

                    </div>
                </article>
            `;
        })
        .join("");
}


function filterAlerts() {
    const searchValue =
        document
            .getElementById("alertSearchInput")
            ?.value
            .trim()
            .toLowerCase() || "";

    const levelValue =
        document
            .getElementById("alertLevelFilter")
            ?.value || "";

    const statusValue =
        document
            .getElementById("alertStatusFilter")
            ?.value || "";

    const filtered = allAlerts.filter(alert => {
        const level =
            normalizeAlertLevel(alert.niveau);

        const status =
            normalizeAlertStatus(alert.statut);

        const searchableText = `
            ${alert.titre || ""}
            ${alert.message || ""}
            ${level}
            ${status}
        `.toLowerCase();

        const matchesSearch =
            !searchValue ||
            searchableText.includes(searchValue);

        const matchesLevel =
            !levelValue ||
            level === levelValue;

        const matchesStatus =
            !statusValue ||
            status === statusValue;

        return (
            matchesSearch &&
            matchesLevel &&
            matchesStatus
        );
    });

    renderAlerts(filtered);
}


async function loadAlerts() {
    const container =
        document.getElementById("alertsList");

    if (container) {
        container.innerHTML = `
            <div class="alerts-loading">
                <i class="fa-solid fa-spinner fa-spin"></i>
                Chargement des alertes...
            </div>
        `;
    }

    try {
        const response = await fetch("/api/alerts/");

        if (!response.ok) {
            throw new Error(
                `Erreur HTTP ${response.status}`
            );
        }

        const data = await response.json();

        allAlerts = Array.isArray(data)
            ? data
            : [];

        updateAlertCounters(allAlerts);
        renderAlerts(allAlerts);

        const body =
            document.getElementById("alertsTableBody");

        if (body) {
            body.innerHTML = allAlerts
                .map(alert => `
                    <tr>
                        <td>${escapeHtml(alert.niveau)}</td>
                        <td>${escapeHtml(alert.titre)}</td>
                        <td>${escapeHtml(alert.message)}</td>
                    </tr>
                `)
                .join("");
        }

    } catch (error) {
        console.error(
            "Erreur de chargement des alertes :",
            error
        );

        if (container) {
            container.innerHTML = `
                <div class="alerts-error">
                    <i class="fa-solid fa-triangle-exclamation"></i>

                    <div>
                        <h3>Impossible de charger les alertes</h3>

                        <p>
                            Vérifie la route
                            <code>/api/alerts/</code>
                            et la console du serveur Flask.
                        </p>
                    </div>
                </div>
            `;
        }
    }
}
async function loadAgenda(){

    const r =
        await fetch(
            "/api/agenda/"
        );

    const data =
        await r.json();

    let html="";

    data.forEach(e=>{

        html += `
        <tr>

            <td>${e.date_debut}</td>

            <td>${e.titre}</td>

            <td>${e.categorie}</td>

            <td>${e.statut}</td>

        </tr>
        `;

    });

    const body =
        document.getElementById(
            "agendaTableBody"
        );

    if(body){

        body.innerHTML = html;

    }
}
async function initCalendar(){

    const calendarEl =
        document.getElementById(
            "calendar"
        );

    if(!calendarEl)
        return;

    const r =
        await fetch(
            "/api/agenda/calendar"
        );

    const events =
        await r.json();

    const calendar =
        new FullCalendar.Calendar(
            calendarEl,
            {

                initialView:
                    "dayGridMonth",

                locale:
                    "fr",

                events:
                    events

            }
        );

    calendar.render();
}
function openModal(id){

    document
    .getElementById(id)
    .style.display =
        "flex";

}

function closeModal(id){

    document
    .getElementById(id)
    .style.display =
        "none";

}
async function saveClient(){

    const form =
        document.getElementById(
            "clientForm"
        );

    const data =
        new FormData(form);

    const r = await fetch(

        "/api/clients/add",

        {
            method:"POST",
            body:data
        }

    );

    const res =
        await r.json();

    if(res.success){

        alert(
            "Client ajouté"
        );

        loadClients();

        closeModal(
            "clientModal"
        );

    }
}
async function saveEmployee(){

    const form =
        document.getElementById(
            "employeeForm"
        );

    const data =
        new FormData(form);

    const r = await fetch(

        "/api/employees/add",

        {
            method:"POST",
            body:data
        }

    );

    const res =
        await r.json();

    if(res.success){

        alert(
            "Employé ajouté"
        );

        loadEmployees();

        closeModal(
            "employeeModal"
        );

    }
}
async function saveDocument(){

    const form =
        document.getElementById(
            "documentForm"
        );

    const data =
        new FormData(form);

    const r = await fetch(

        "/api/documents/add",

        {
            method:"POST",
            body:data
        }

    );

    const res =
        await r.json();

    if(res.success){

        alert(
            "Document ajouté"
        );

        loadDocuments();

        closeModal(
            "documentModal"
        );

    }
}
async function savePiece(){

    const form =
        document.getElementById(
            "pieceForm"
        );

    const data =
        new FormData(form);

    const r = await fetch(

        "/api/stock/piece/add",

        {
            method:"POST",
            body:data
        }

    );

    const res =
        await r.json();

    if(res.success){

        alert(
            "Pièce ajoutée"
        );

        loadStock();

        closeModal(
            "pieceModal"
        );

    }
}
async function saveMaintenance(){

    const form =
        document.getElementById(
            "maintenanceForm"
        );

    const data =
        new FormData(form);

    const r = await fetch(

        "/api/maintenance/add",

        {
            method:"POST",
            body:data
        }

    );

    const res =
        await r.json();

    if(res.success){

        alert(
            "Maintenance créée"
        );

        loadMaintenance();

        loadAgenda();

        closeModal(
            "maintenanceModal"
        );

    }
}
async function saveAgenda(){

    const form =
        document.getElementById(
            "agendaForm"
        );

    const data =
        new FormData(form);

    const r = await fetch(

        "/api/agenda/add",

        {
            method:"POST",
            body:data
        }

    );

    const res =
        await r.json();

    if(res.success){

        alert(
            "Événement créé"
        );

        loadAgenda();

        initCalendar();

        closeModal(
            "agendaModal"
        );

    }
}
async function saveUser(){

    const form =
        document.getElementById(
            "userForm"
        );

    const data =
        new FormData(form);

    const r = await fetch(

        "/api/users/add",

        {
            method:"POST",
            body:data
        }

    );

    const res =
        await r.json();

    if(res.success){

        alert(
            "Utilisateur créé"
        );

        loadUsers();

        closeModal(
            "userModal"
        );

    }
}
async function uploadOCR(){

    const fileInput =
        document.getElementById(
            "ocrFile"
        );

    const data =
        new FormData();

    data.append(
        "file",
        fileInput.files[0]
    );

    const r = await fetch(

        "/api/ocr/analyse",

        {
            method:"POST",
            body:data
        }

    );

    const res =
        await r.json();

    document.getElementById(
        "ocrResult"
    ).innerHTML = `

        <h3>Résultat OCR</h3>

        <p>
            <b>Matricule :</b>
            ${res.matricule || ''}
        </p>

        <p>
            <b>Licence :</b>
            ${res.licence || ''}
        </p>

        <p>
            <b>Expiration :</b>
            ${res.expiration || ''}
        </p>

        <textarea
        style="width:100%;height:250px">
${res.texte || ''}
        </textarea>

    `;
}
async function signDocument(){

    const data = {

        id_document:
            document.getElementById(
                "signDocumentId"
            ).value,

        nom_signataire:
            document.getElementById(
                "signataireNom"
            ).value,

        fonction_signataire:
            document.getElementById(
                "signataireFonction"
            ).value,

        signature_base64:
            signaturePad
            .toDataURL()

    };

    const r = await fetch(

        "/api/signatures/document/sign",

        {

            method:"POST",

            headers:{
                "Content-Type":
                "application/json"
            },

            body:
                JSON.stringify(data)

        }

    );

    const res =
        await r.json();

    if(res.success){

        alert(
            "Document signé"
        );

        closeModal(
            "signatureModal"
        );

        loadDocuments();

    }
}
