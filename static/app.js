document.addEventListener(
    "DOMContentLoaded",
    async () => {

        showPage("dashboard");

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
        users: "Gestion des utilisateurs"
    };

    const title = document.getElementById("page-title");

    if (title) {
        title.textContent = titles[pageName] || "AeroDoc";
    }
}
async function loadDashboard(){

    const r =
        await fetch(
            "/api/dashboard/"
        );

    const d =
        await r.json();

    if(document.getElementById("kpiEmployees"))
        document.getElementById(
            "kpiEmployees"
        ).innerText =
            d.total_employes || 0;

    if(document.getElementById("kpiDocuments"))
        document.getElementById(
            "kpiDocuments"
        ).innerText =
            d.total_documents || 0;

    if(document.getElementById("kpiClients"))
        document.getElementById(
            "kpiClients"
        ).innerText =
            d.total_clients || 0;

    if(document.getElementById("kpiMaintenance"))
        document.getElementById(
            "kpiMaintenance"
        ).innerText =
            d.total_maintenances || 0;

    if(document.getElementById("kpiAlerts"))
        document.getElementById(
            "kpiAlerts"
        ).innerText =
            d.active_alerts || 0;
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
async function loadAlerts(){

    const r =
        await fetch(
            "/api/alerts/"
        );

    const data =
        await r.json();

    let html="";

    data.forEach(a=>{

        html += `
        <tr>

            <td>${a.niveau}</td>

            <td>${a.titre}</td>

            <td>${a.message}</td>

        </tr>
        `;

    });

    const body =
        document.getElementById(
            "alertsTableBody"
        );

    if(body){

        body.innerHTML = html;

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
