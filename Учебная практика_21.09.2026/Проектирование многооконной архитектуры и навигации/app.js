// ============================================================
// Задание 1: Проектирование многооконной архитектуры и навигации
//
// Реализует:
//   - Два экрана: главная форма (список партнёров) и экран партнёра
//   - Переключение экранов без перезагрузки страницы
//   - Загрузка и отображение карточек партнёров с сервера
//   - Навигация: кнопка «Добавить партнёра», двойной клик по карточке,
//     кнопка «Назад»
// ============================================================

const API_PARTNERS = "api/partners";

// ── DOM-элементы ──────────────────────────────────────────────────────────
const mainWindow    = document.getElementById("main-window");
const partnerWindow = document.getElementById("partner-window");
const partnerTitle  = document.getElementById("partner-title");
const cardsEl       = document.getElementById("cards");
const statusEl      = document.getElementById("status");
const refreshBtn    = document.getElementById("refresh-btn");
const addBtn        = document.getElementById("add-btn");
const backBtn       = document.getElementById("back-btn");

// ============================================================
// Переключение экранов
// ============================================================
function showWindow(win) {
    document.querySelectorAll(".window").forEach(w => w.classList.remove("active"));
    win.classList.add("active");
    document.title = win === mainWindow
        ? "CRM: Реестр партнеров"
        : partnerTitle.textContent;
}

// ============================================================
// Главная форма: загрузка и отрисовка карточек партнёров
// ============================================================
function inferRole(companyName) {
    if (companyName.startsWith("ИП ")) return "Индивидуальный предприниматель";
    return "Директор";
}

function renderPartners(partners) {
    cardsEl.innerHTML = "";

    if (partners.length === 0) {
        const msg = document.createElement("div");
        msg.className = "empty-message";
        msg.textContent = "Партнеры не найдены";
        cardsEl.appendChild(msg);
        return;
    }

    for (const partner of partners) {
        const card = document.createElement("div");
        card.className = "card";

        const info = document.createElement("div");
        info.className = "card-info";

        const title = document.createElement("div");
        title.className = "card-title";
        title.textContent = partner.company_name;

        const role = document.createElement("div");
        role.className = "card-role";
        role.textContent = inferRole(partner.company_name);

        const phone = document.createElement("div");
        phone.className = "card-phone";
        phone.textContent = partner.phone || "—";

        const rating = document.createElement("div");
        rating.className = "card-rating";
        rating.textContent = "Рейтинг: " + (partner.rating === null ? "—" : partner.rating);

        info.append(title, role, phone, rating);

        const discount = document.createElement("div");
        discount.className = "card-discount";
        discount.textContent = partner.discount_percent + "%";

        card.append(info, discount);

        // Двойной клик — переход на экран партнёра
        card.addEventListener("dblclick", () => openPartnerScreen(partner));

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

// ============================================================
// Навигация: открытие второго экрана
// ============================================================
function openPartnerScreen(partner) {
    partnerTitle.textContent = "CRM: Карточка партнера [Редактирование]";
    showWindow(partnerWindow);
}

function openAddScreen() {
    partnerTitle.textContent = "CRM: Карточка партнера [Добавление]";
    showWindow(partnerWindow);
}

// ============================================================
// Инициализация
// ============================================================
addBtn.addEventListener("click", openAddScreen);
refreshBtn.addEventListener("click", loadPartners);
backBtn.addEventListener("click", () => showWindow(mainWindow));

loadPartners();
