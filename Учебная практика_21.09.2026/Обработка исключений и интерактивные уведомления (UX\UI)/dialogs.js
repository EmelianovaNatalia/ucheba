/**
 * dialogs.js — модуль интерактивных диалоговых окон (MessageBox)
 *
 * Три типа диалогов:
 *   "error"   — сообщение об ошибке        (✖)
 *   "warning" — предупреждение с подтверждением (⚠)
 *   "info"    — информационное сообщение    (ℹ)
 *
 * Использование:
 *   // Простое сообщение об ошибке:
 *   showDialog("error", "Ошибка", "Не удалось сохранить данные.");
 *
 *   // Информационное сообщение с действием после закрытия:
 *   showDialog("info", "Успешно", "Партнер добавлен.", () => {
 *       loadPartners();
 *   });
 *
 *   // Предупреждение с кнопкой «Отмена»:
 *   showDialog("warning", "Внимание",
 *       "Изменения не сохранены. Продолжить?",
 *       () => { showWindow(mainWindow); }
 *   );
 *
 * Подключение в HTML:
 *   <link rel="stylesheet" href="dialogs.css">
 *   <script src="dialogs.js"></script>
 */

// ── Ссылки на DOM-элементы диалога ────────────────────────────────────────
const overlay       = document.getElementById("dialog-overlay");
const dialogTitle   = document.getElementById("dialog-title");
const dialogIcon    = document.getElementById("dialog-icon");
const dialogMessage = document.getElementById("dialog-message");
const dialogOk      = document.getElementById("dialog-ok");
const dialogCancel  = document.getElementById("dialog-cancel");

// ── Иконки для каждого типа диалога ───────────────────────────────────────
const DIALOG_ICONS = {
    error:   "✖",   // красный крестик — ошибка
    warning: "⚠",   // жёлтый знак    — предупреждение
    info:    "ℹ",   // синий знак     — информация
};

/**
 * Показывает диалоговое окно.
 *
 * @param {"error"|"warning"|"info"} type  — тип диалога
 * @param {string} title                   — заголовок окна
 * @param {string} message                 — текст сообщения (поддерживает \n)
 * @param {Function|null} [onConfirm]      — колбэк при нажатии «ОК»;
 *                                           если передан — показывается кнопка «Отмена»
 */
function showDialog(type, title, message, onConfirm = null) {
    dialogIcon.textContent    = DIALOG_ICONS[type] || "ℹ";
    dialogTitle.textContent   = title;
    dialogMessage.textContent = message;

    // Кнопка «Отмена» — только для диалогов с подтверждением
    if (onConfirm) {
        dialogCancel.classList.remove("hidden");
        dialogCancel.onclick = () => { overlay.classList.add("hidden"); };
    } else {
        dialogCancel.classList.add("hidden");
    }

    dialogOk.onclick = () => {
        overlay.classList.add("hidden");
        if (onConfirm) onConfirm();
    };

    overlay.classList.remove("hidden");
}

/**
 * Закрывает диалог программно (без действий).
 */
function closeDialog() {
    overlay.classList.add("hidden");
}
