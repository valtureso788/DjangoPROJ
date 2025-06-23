// Основные функции JavaScript для Task Manager

// Функция для инициализации всплывающих подсказок Bootstrap
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Функция для инициализации всплывающих окон Bootstrap
function initPopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Функция для автоматического скрытия уведомлений
function initAlertDismiss() {
    const alertList = document.querySelectorAll('.alert');
    alertList.forEach(function (alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // Скрывать через 5 секунд
    });
}

// Функция для подтверждения удаления
function confirmDelete(event, message) {
    if (!confirm(message || 'Вы уверены, что хотите удалить этот элемент?')) {
        event.preventDefault();
        return false;
    }
    return true;
}

// Функция для обновления прогресс-бара
function updateProgressBar(elementId, value) {
    const progressBar = document.getElementById(elementId);
    if (progressBar) {
        progressBar.style.width = value + '%';
        progressBar.setAttribute('aria-valuenow', value);
        progressBar.textContent = value + '%';
    }
}

// Функция для фильтрации задач по статусу
function filterTasksByStatus(status) {
    const tasks = document.querySelectorAll('.task-item');
    tasks.forEach(task => {
        if (status === 'all' || task.dataset.status === status) {
            task.style.display = 'block';
        } else {
            task.style.display = 'none';
        }
    });
}

// Функция для фильтрации задач по приоритету
function filterTasksByPriority(priority) {
    const tasks = document.querySelectorAll('.task-item');
    tasks.forEach(task => {
        if (priority === 'all' || task.dataset.priority === priority) {
            task.style.display = 'block';
        } else {
            task.style.display = 'none';
        }
    });
}

// Инициализация всех компонентов при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initTooltips();
    initPopovers();
    initAlertDismiss();
    
    // Добавляем обработчики для кнопок удаления
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            confirmDelete(event, 'Вы уверены, что хотите удалить этот элемент? Это действие нельзя отменить.');
        });
    });
});
