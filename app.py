import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Файл для хранения данных о песнях
SONGS_FILE = 'data.json'

def allowed_file(filename):
    """Проверяет, разрешён ли формат файла"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_songs():
    """Загружает данные о песнях из JSON-файла"""
    if os.path.exists(SONGS_FILE):
        with open(SONGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'genres': {}, 'uploaded_songs': []}

def save_songs(data):
    """Сохраняет данные о песнях в JSON-файл"""
    with open(SONGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_songs_by_genre(genre):
    """Получает песни для указанного жанра"""
    data = load_songs()
    return data['genres'].get(genre, [])

@app.route('/')
def home():
    artists = [
        {'name': 'The Beatles', 'songs': ['Yesterday', 'Let It Be']},
        {'name': 'Queen', 'songs': ['Bohemian Rhapsody', 'We Will Rock You']},
        {'name': 'Michael Jackson', 'songs': ['Billie Jean', 'Thriller']}
    ]
    return render_template('home.html', artists=artists)

@app.route('/genres')
def genres():
    genres_list = [
        {'name': 'Рок', 'description': 'Мощные гитарные риффы и энергичные ритмы'},
        {'name': 'Джаз', 'description': 'Импровизация и сложные гармонии'},
        {'name': 'Классика', 'description': 'Вечные произведения великих композиторов'},
        {'name': 'Поп', 'description': 'Лёгкие запоминающиеся мелодии'},
        {'name': 'Хип-хоп', 'description': 'Ритмичный речитатив и биты'}
    ]
    return render_template('genres.html', genres=genres_list)

@app.route('/listen_examples/<genre>')
def listen_examples(genre):
    songs = get_songs_by_genre(genre)
    return render_template('listen_examples.html', genre=genre, songs=songs)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    error = None
    data = load_songs()

    if request.method == 'POST':
        # Проверка наличия файла в запросе
        if 'song_file' not in request.files:
            error = 'Файл не выбран'
        else:
            file = request.files['song_file']
            # Если пользователь не выбрал файл, браузер отправляет пустой файл
            if file.filename == '':
                error = 'Файл не выбран'
            elif file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Создаём запись о песне
                new_song = {
                    'title': request.form['title'],
                    'artist': request.form['artist'],
                    'filename': filename
                }

                # Добавляем в список загруженных песен
                data['uploaded_songs'].append(new_song)

                # Сохраняем данные
                save_songs(data)

                flash('Песня успешно загружена!', 'success')
                return redirect(url_for('upload'))
            else:
                error = 'Разрешены только файлы MP3'

    # Получаем список загруженных песен для отображения
    songs = data['uploaded_songs']
    return render_template('upload.html', error=error, songs=songs)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Обработчик ошибок 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)