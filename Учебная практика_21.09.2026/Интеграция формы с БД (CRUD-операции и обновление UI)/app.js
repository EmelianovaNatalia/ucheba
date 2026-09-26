// ============================================================
// Задание 3: Интеграция формы с БД (CRUD-операции и обновление UI)
//
// Реализует:
//   - Все возможности задания 2 (форма, валидация, formDirty)

//   - POST /api/partners/add    — добавление партнера в БД (INSERT)
//   - POST /api/partners/update — обновление данных партнера (UPDATE)
//   - Автоматическое обновление списка карточек после сохранения
//   - Скидка рассчитывается сервером через discount.py


// ============================================================

const API_PARTNERS = "api/partners";
const API_TYPES    = "api/partner-types";
const API_ADD      = "api/partners/add";
const API_UPDATE   = "api/partners/update";

// ── DOM-элементы: главная форма ───────────────────────────────────────────
const mainWindow    = document.getElementById("main-window");
const cardsEl       = document.getElementById("cards");
const statusEl      = document.getElementById("status");
const refreshBtn    = document.getElementById("refresh-btn");
const addBtn        = document.getElementById("add-btn");

// ── DOM-элементы: форма редактирования ───────────────────────────────────
const editWindow    = document.getElementById("edit-window");
const editTitle     = document.getElementById("edit-title");
const partnerForm   = document.getElementById("partner-form");
const backBtn       = document.getElementById("back-btn");
const fieldId       = document.getElementById("partner-id");
const fieldType     = document.getElementById("field-type");
const fieldName     = document.getElementById("field-name");
const fieldDirector = document.getElementById("field-director");
const fieldEmail    = document.getElementById("field-email");
const fieldPhone    = document.getElementById("field-phone");
const fieldAddress  = document.getElementById("field-address");
const fieldInn      = document.getElementById("field-inn");
const fieldRating   = document.getElementById("field-rating");

// ============================================================
// Переключение экранов
// ============================================================
function showWindow(win) {
    document.querySelectorAll(".window").forEach(w => w.classList.remove("active"));
    win.classList.add("active");
    document.title = win === mainWindow
        ? "CRM: Реестр партнеров"
        : editTitle.textContent;
}

// ============================================================
// Главная форма: загрузка и отрисовка карточек
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
        card.addEventListener("dblclick", () => openEditMode(partner));
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
// Форма: загрузка типов партнёров в ComboBox
// ============================================================
async function loadPartnerTypes() {
    try {
        const resp = await fetch(API_TYPES);
        if (!resp.ok) throw new Error("HTTP " + resp.status);
        const types = await resp.json();
        fieldType.innerHTML = '<option value="">— выберите тип —</option>';
        for (const t of types) {
            const opt = document.createElement("option");
            opt.value = t.partner_type_id;
            opt.textContent = t.type_name;
            fieldType.appendChild(opt);
        }
    } catch (err) {
        console.error("Не удалось загрузить типы партнёров:", err.message);
    }
}

// ============================================================
// Режим добавления: очищаем форму
// ============================================================
function openAddMode() {
    editTitle.textContent = "CRM: Карточка партнера [Добавление]";
    document.title        = "CRM: Карточка партнера [Добавление]";
    partnerForm.reset();
    fieldId.value = "";
    resetDirty();
    loadPartnerTypes();
    showWindow(editWindow);
}

// ============================================================
// Режим редактирования: заполняем форму данными партнёра
// ============================================================
function openEditMode(partner) {
    editTitle.textContent = "CRM: Карточка партнера [Редактирование]";
    document.title        = "CRM: Карточка партнера [Редактирование]";

    fieldId.value       = partner.partner_id;
    fieldName.value     = partner.company_name || "";
    fieldDirector.value = partner.director     || "";
    fieldEmail.value    = partner.email        || "";
    fieldPhone.value    = partner.phone        || "";
    fieldAddress.value  = partner.address      || "";
    fieldInn.value      = partner.inn          || "";
    fieldRating.value   = partner.rating !== null ? partner.rating : "";

    resetDirty();

    loadPartnerTypes().then(() => {
        fieldType.value = partner.partner_type_id || "";
    });

    showWindow(editWindow);
}

// ============================================================
// Отслеживание несохранённых изменений
// ============================================================
let formDirty = false;

function markDirty()  { formDirty = true; }
function resetDirty() { formDirty = false; }

[fieldType, fieldName, fieldDirector, fieldEmail, fieldPhone,
 fieldAddress, fieldInn, fieldRating].forEach(el => {
    el.addEventListener("input",  markDirty);
    el.addEventListener("change", markDirty);
});

// ============================================================
// Валидация формы
// ============================================================
function validateForm() {
    const errors = [];

    if (!fieldType.value) {
        errors.push("Тип партнера обязателен для заполнения.");
    }
    if (!fieldName.value.trim()) {
        errors.push("Наименование не может быть пустым.");
    }
    if (!fieldEmail.value.trim()) {
        errors.push("Email компании обязателен для заполнения.");
    }

    const ratingVal = fieldRating.value.trim();
    if (ratingVal !== "") {
        const rating = Number(ratingVal);
        if (!Number.isInteger(rating) || rating < 0) {
            errors.push(
                "Рейтинг должен быть целым числом от 0. " +
                "Пожалуйста, удалите знаки препинания и повторите попытку."
            );
        }
    }

    return errors;
}

// ============================================================
// Сохранение формы (INSERT или UPDATE)
// ============================================================
partnerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const errors = validateForm();
    if (errors.length > 0) {
        alert("Ошибка ввода:\n\n" + errors.join("\n\n"));
        return;
    }

    const data = {
        partner_type_id: parseInt(fieldType.value),
        company_name:    fieldName.value.trim(),
        director:        fieldDirector.value.trim(),
        email:           fieldEmail.value.trim(),
        phone:           fieldPhone.value.trim() || "Не указан",
        address:         fieldAddress.value.trim(),
        inn:             fieldInn.value.trim(),
        rating:          fieldRating.value.trim() !== "" ? parseInt(fieldRating.value) : 0,
    };

    const isEdit = !!fieldId.value;
    const url    = isEdit ? API_UPDATE : API_ADD;
    if (isEdit) data.partner_id = parseInt(fieldId.value);

    try {
        const resp   = await fetch(url, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify(data),
        });
        const result = await resp.json();

        if (!resp.ok) {
            alert("Ошибка сохранения:\n" + (result.error || "Проверьте подключение к базе данных."));
            return;
        }

        const action = isEdit ? "обновлён" : "добавлен";
        alert(`Партнер успешно ${action}.`);
        resetDirty();
        showWindow(mainWindow);
        loadPartners();

    } catch (err) {
        alert("Сервер недоступен.\n" + err.message);
    }
});

// ============================================================
// Кнопка «Назад»: предупреждение при несохранённых изменениях
// ============================================================
backBtn.addEventListener("click", () => {
    if (formDirty) {
        const confirmed = confirm(
            "Вы внесли изменения, которые не были сохранены.\n" +
            "При возврате они будут потеряны. Продолжить?"
        );
        if (confirmed) {
            resetDirty();
            showWindow(mainWindow);
        }
    } else {
        showWindow(mainWindow);
    }
});

// ============================================================
// Инициализация
// ============================================================
addBtn.addEventListener("click", () => {
    resetDirty();
    openAddMode();
});
refreshBtn.addEventListener("click", loadPartners);

loadPartners();
