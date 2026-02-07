/**
 * Theme toggle: light / dark.
 * Сохраняет выбор в localStorage, применяет при загрузке.
 */

(function () {
    'use strict';

    var KEY = 'theme';

    function getTheme() {
        try {
            return localStorage.getItem(KEY) || 'light';
        } catch {
            return 'light';
        }
    }

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        try {
            localStorage.setItem(KEY, theme);
        } catch (_) {}
    }

    function toggleTheme() {
        var current = getTheme();
        var next = current === 'light' ? 'dark' : 'light';
        setTheme(next);
    }

    // Применяем сохранённую тему сразу (до отрисовки)
    setTheme(getTheme());

    // Глобально для кнопки
    window.toggleTheme = toggleTheme;
    window.getTheme = getTheme;
})();
