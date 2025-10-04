# Команды для загрузки в GitLab

## 1. Установка Git (если не установлен)
Скачайте и установите Git с https://git-scm.com/download/windows

## 2. Инициализация репозитория
```bash
cd server
git init
```

## 3. Добавление файлов
```bash
git add .
```

## 4. Первый коммит
```bash
git commit -m "Initial commit: Dofamine Server setup"
```

## 5. Добавление удаленного репозитория
Замените YOUR_USERNAME и YOUR_REPO_NAME на ваши данные:
```bash
git remote add origin https://gitlab.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

## 6. Загрузка в GitLab
```bash
git push -u origin main
```

## 7. Если ветка называется master вместо main:
```bash
git branch -M main
git push -u origin main
```

## 8. Проверка статуса
```bash
git status
```

## 9. Просмотр удаленных репозиториев
```bash
git remote -v
```
