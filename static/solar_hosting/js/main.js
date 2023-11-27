// Определение переменной purchaseUrl
var purchaseUrl = "{% url 'solar_hosting:purchase_domain' %}";

// Определение функции showPurchaseWarning
function showPurchaseWarning(event, url) {
    event.preventDefault();

    // Проверка, авторизован ли пользователь
    var isAuthenticated = "{% if user.is_authenticated %}true{% else %}false{% endif %}";

    if (isAuthenticated === "true") {
        // Пользователь авторизован, перейдите на purchase_domain
        window.location.href = purchaseUrl;
    } else {
        // Пользователь не авторизован, покажите сообщение с ссылкой на вход и регистрацию
        var message = "Для совершения покупок войдите или зарегистрируйтесь.\n\n" +
            "Если у вас нет аккаунта, вы можете зарегистрироваться либо войти по этой ссылке: ВАША_ССЫЛКА_НА_РЕГИСТРАЦИЮ";

        // Показать сообщение с ссылкой для входа и регистрации
        alert(message);

        // Обработка закрытия сообщения
        var closeButton = document.querySelector('.alert button[data-bs-dismiss="alert"]');
        closeButton.addEventListener('click', function () {
            // Отключить закрытие сообщения при нажатии на кнопку
            closeButton.setAttribute('data-bs-dismiss', '');
        });
    }
}

// Остальной код файла main.js
document.addEventListener('DOMContentLoaded', function () {
    var purchaseButton = document.getElementById('purchaseButton');
    if (purchaseButton) {
        purchaseButton.addEventListener('click', function (event) {
            console.log('Button clicked');
            showPurchaseWarning(event, purchaseUrl);
        });
    }
});
