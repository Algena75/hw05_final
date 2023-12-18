# Yatube
Социальная сеть Yatube
### Описание
Социальная сеть для блогеров. Реализована возможность подписки на авторов, комментирования постов.
### Технологии
Python 3.9

Django==3.2.16

Bootstrap

Sorl-Thumbnail

SQLite
### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/algena75/hw05_final.git

cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env

source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
### Авторы
Когорта 19+, Наумов А.Г.
