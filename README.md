Знакомство с GitHub

# Football Legacy — CI/CD

[![Deploy static site](https://github.com/Serfit88/Football/actions/workflows/deploy.yml/badge.svg)](https://github.com/Serfit88/Football/actions/workflows/deploy.yml)

Статический футбольный сайт. Для локального просмотра откройте index.html.

Лабораторная работа №6: проверки HTML, локальных ресурсов, структуры CSS и синтаксиса JavaScript перед публикацией на GitHub Pages.

- Workflow: `.github/workflows/deploy.yml`.
- Проверки: `python3 scripts/validate_site.py`, `node --check main.js`.
- Тесты контроля качества: `python3 -m unittest discover -s tests -v`.
- Упаковка сайта: `python3 scripts/build_site.py`.
- Условия запуска: push в main, pull request в main, ручной запуск. Для pull request выполняются только проверки.
- Для первой публикации в Settings → Pages выберите источник **GitHub Actions**. Наличие workflow само по себе не включает Pages.
- Подробности: [LAB6.md](LAB6.md).
