// ============================================================
// Задание 2: Разработка формы добавления/редактирования партнера
//
// Реализует:
//   - Все поля формы партнёра (тип, название, директор, email,
//     телефон, адрес, ИНН, рейтинг)
//   - ComboBox типов партнёров (загружается из API)
//   - Два режима: [Добавление] и [Редактирование]
//   - Отслеживание несохранённых изменений (formDirty)
//   - Предупреждение при нажатии «Назад» с несохранёнными данными
//   - Базовая валидация обязательных полей
//   - Сохранение отправляет данные на сервер (INSERT / UPDATE)
// ============================================================

const API_TYPES  = "api/partner-types";
const API_ADD    = "api/partners/add";
const API_UPDATE = "api/partners/update";

// ── DOM-элементы ──────────────────────────────────────────────────────────
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
// Загрузка типов партнёров в ComboBox
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
// Определение режима по URL-параметру:
//   ?mode=add              — добавление нового партнёра
//   ?mode=edit&id=<number> — редактирование существующего
// ============================================================
function initMode() {
    const params = new URLSearchParams(window.location.search);
    const mode   = params.get("mode");
    const id     = params.get("id");

    if (mode === "edit" && id) {
        editTitle.textContent = "CRM: Карточка партнера [Редактирование]";
        document.title        = "CRM: Карточка партнера [Редактирование]";
        fieldId.value = id;
        loadPartnerData(id);
    } else {
        editTitle.textContent = "CRM: Карточка партнера [Добавление]";
        document.title        = "CRM: Карточка партнера [Добавление]";
        fieldId.value = "";
        partnerForm.reset();
        resetDirty();
    }

    loadPartnerTypes();
}

async function loadPartnerData(id) {
    try {
        const resp = await fetch("api/partners/" + id);
        if (!resp.ok) throw new Error("HTTP " + resp.status);
        const p = await resp.json();

        fieldName.value     = p.company_name || "";
        fieldDirector.value = p.director     || "";
        fieldEmail.value    = p.email        || "";
        fieldPhone.value    = p.phone        || "";
        fieldAddress.value  = p.address      || "";
        fieldInn.value      = p.inn          || "";
        fieldRating.value   = p.rating !== null ? p.rating : "";

        resetDirty();

        loadPartnerTypes().then(() => {
            fieldType.value = p.partner_type_id || "";
        });
    } catch (err) {
        console.error("Не удалось загрузить данные партнёра:", err.message);
    }
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
        history.back();

    } catch (err) {
        alert("Сервер недоступен.\n" + err.message);
    }
});

// ============================================================
// Кнопка «Назад»
// ============================================================
backBtn.addEventListener("click", () => {
    if (formDirty) {
        const confirmed = confirm(
            "Вы внесли изменения, которые не были сохранены.\n" +
            "При возврате они будут потеряны. Продолжить?"
        );
        if (confirmed) {
            resetDirty();
            history.back();
        }
    } else {
        history.back();
    }
});

// ============================================================
// Инициализация
// ============================================================
initMode();
