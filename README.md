# Спринт №5 Социальная сеть блогеров. Раздел тесты.

## Описание
В данном спринте были добавлены тесты к уже написано приложению Posts.
В работе использовалась библиотека Unittest, входяшую в состав библиотеки Django.
Были написаны тесты для Models, URLs, Views и Form. 

## Настройка и запуск
Склонировать проект:
```
git clone https://github.com/maksim-moryakov/hw02_community.git
```

Устанавить виртуальное окружение:
```
python -m venv venv
```
Активировать виртуальное окружение:
```
source venv/Scripts/activate
```
> Для деактивации виртуального окружения:
>
>``` 
>deactivate
>```

Обнавить пакетный менеджер pip и устанавить зависимости:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Применяем миграции:
```
python yatube/manage.py makemigrations
python yatube/manage.py migrate
```

Файлы с изобразениями и стилями расспологаются по ссылке: 
```
https://code.s3.yandex.net/Python-dev/web_hw02_community_with_text_01_06_22.zip
```
Их необходимо разместить в дериктории static

Для запуска тестов, необходимо активировать виртуальное окружение, перейти в папку /yatube и в консоле выполнить комманду:
```
 python manage.py test
```

## Используемые технологии
- Python 3.9
- Django 2.2.19
- pytz 2022.7.1
- sqlparse 0.4.3

## Автор
- Моряков Максим
- Email: maksim.moryakov@gmail.com 
