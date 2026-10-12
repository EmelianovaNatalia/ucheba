const API_PARTNERS = "api/partners";

const mainWindow    = document.getElementById("main-window");
const historyWindow = document.getElementById("history-window");
const historyTitle  = document.getElementById("history-title");
const cardsEl       = document.getElementById("cards");
const statusEl      = document.getElementById("status");
const historyBody   = document.getElementById("history-body");
const historyEmpty  = document.getElementById("history-empty");
const historyTable  = document.getElementById("history-table");

document.getElementById("refresh-btn").addEventListener("click", loadPartners);
document.getElementById("back-btn").addEventListener("click", () => showWindow(mainWindow));
document.getElementById("history-btn").addEventListener("click", () => {
    if (!selectedPartner) { alert("Выберите партнёра из списка"); return; }
    openHistory(selectedPartner);
});

let selectedPartner = null;

function showWindow(win) {
    document.querySelectorAll(".window").forEach(w => w.classList.remove("active"));
    win.classList.add("active");
}

function inferRole(name) {
    return name.startsWith("ИП ") ? "Индивидуальный предприниматель" : "Директор";
}

function renderPartners(partners) {
    cardsEl.innerHTML = "";
    selectedPartner = null;
    if (!partners.length) {
        cardsEl.innerHTML = '<div class="empty-message">Партнёры не найдены</div>';
        return;
    }
    for (const p of partners) {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `
            <div class="card-info">
                <div class="card-title">${p.company_name}</div>
                <div class="card-role">${inferRole(p.company_name)}</div>
                <div class="card-phone">${p.phone || "—"}</div>
                <div class="card-rating">Рейтинг: ${p.rating ?? "—"}</div>
            </div>
            <div class="card-discount">${p.discount_percent}%</div>`;
        card.addEventListener("click", () => {
            document.querySelectorAll(".card").forEach(c => c.classList.remove("selected"));
            card.classList.add("selected");
            selectedPartner = p;
        });
        card.addEventListener("dblclick", () => openHistory(p));
        cardsEl.appendChild(card);
    }
}

async function loadPartners() {
    statusEl.textContent = "Загрузка данных...";
    try {
        const resp = await fetch(API_PARTNERS);
        if (!resp.ok) throw new Error("HTTP " + resp.status);
        const partners = await resp.json();
        renderPartners(partners);
        statusEl.textContent = "Данные обновлены: " + partners.length + " партнер(ов)";
    } catch (err) {
        statusEl.textContent = "Ошибка загрузки: " + err.message;
    }
}

async function openHistory(partner) {
    historyTitle.textContent = "CRM: История реализации продукции — " + partner.company_name;
    document.title = historyTitle.textContent;
    historyBody.innerHTML = "<tr><td colspan='3'>Загрузка...</td></tr>";
    historyTable.style.display = "table";
    historyEmpty.style.display = "none";
    showWindow(historyWindow);

    try {
        const resp = await fetch(`api/partners/${partner.partner_id}/history`);
        if (!resp.ok) throw new Error("HTTP " + resp.status);
        const rows = await resp.json();
        if (!rows.length) {
            historyTable.style.display = "none";
            historyEmpty.style.display = "block";
            return;
        }
        historyBody.innerHTML = rows.map(r => `
            <tr>
                <td>${r.product_name}</td>
                <td>${r.quantity}</td>
                <td>${r.sale_date}</td>
            </tr>`).join("");
    } catch (err) {
        historyBody.innerHTML = `<tr><td colspan='3'>Ошибка: ${err.message}</td></tr>`;
    }
}

loadPartners();