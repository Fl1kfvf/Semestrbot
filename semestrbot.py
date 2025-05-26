import logging
import random
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

KINOPOISK_API = 'FT1VJ4S-S1NMHXZ-M3ETEXB-BQ6A3DQ'  # API токен кинопоиска
BOT_TOKEN = '7907006203:AAHS8z6Uxc-qDo-O3RMO-5hLYq2jFH7o0sk'  # API токен тг-бота

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    "Приветственное сообщение"
    await update.message.reply_text(
        "Кино-бот\n\n"
        "Доступные команды:\n"
        "/search <название> - Поиск фильма\n"
        "/top - Топ-10 IMDB\n"
        "/random - Случайный фильм\n"
        "/help - Помощь"
    )

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    "Поиск фильма на Кинопоиске"
    if not context.args:
        await update.message.reply_text("Укажите название фильма после команды /search")
        return

    query = ' '.join(context.args)
    try:
        headers = {
            'X-API-KEY': "FT1VJ4S-S1NMHXZ-M3ETEXB-BQ6A3DQ",
            'Content-Type': 'application/json'
        }
        response = requests.get(
            f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={query}',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['films']:
                film = data['films'][0]
                msg = (
                    f"{film.get('nameRu', film.get('nameEn', 'Без названия'))}\n"
                    f"Год: {film.get('year', 'неизвестен')}\n"
                    f"Рейтинг: {film.get('rating', 'нет данных')}"
                )
            else:
                msg = "Фильм не найден на Кинопоиске"
        else:
            msg = f"Ошибка API: {response.status_code}"
            
        await update.message.reply_text(msg)
    except Exception as e:
        logger.error(f"Ошибка поиска: {e}")
        await update.message.reply_text("Ошибка при поиске фильма")

async def get_imdb_top(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Новый парсинг топа IMDB"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(
            'https://www.imdb.com/chart/top/',
            headers=headers
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        
        movies = []
        for item in soup.select('li.ipc-metadata-list-summary-item'):
            title = item.select_one('h3.ipc-title__text').text.split('. ')[1]
            year = item.select_one('span.sc-14dd939d-6.kHVqMR').text
            rating = item.select_one('span.ipc-rating-star').text.split()[0]
            movies.append(f"{title} ({year}) - ★{rating}")
        
        if movies:
            await update.message.reply_text("Топ-10 IMDB:\n\n" + "\n".join(movies[:10]))
        else:
            await update.message.reply_text("Не удалось получить топ фильмов")
    except Exception as e:
        logger.error(f"Ошибка IMDB: {e}")
        await update.message.reply_text("Ошибка при получении топа")

async def get_random_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    "Случайный фильм из топ-250 Кинопоиска"
    try:
        headers = {
            'X-API-KEY': "FT1VJ4S-S1NMHXZ-M3ETEXB-BQ6A3DQ",
            'Content-Type': 'application/json'
        }
        response = requests.get(
            'https://kinopoiskapiunofficial.tech/api/v2.2/films/top?type=TOP_250_BEST_FILMS&page=1',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['films']:
                film = random.choice(data['films'])
                msg = (
                    f"Случайный фильм:\n\n"
                    f"{film.get('nameRu', film.get('nameEn', 'Без названия'))}\n"
                    f"Год: {film.get('year', 'неизвестен')}\n"
                    f"Рейтинг: {film.get('rating', 'нет данных')}"
                )
            else:
                msg = "Не найдены фильмы в топе"
        else:
            msg = f"Ошибка API: {response.status_code}"
            
        await update.message.reply_text(msg)
    except Exception as e:
        logger.error(f"Ошибка случайного фильма: {e}")
        await update.message.reply_text("Ошибка при выборе фильма")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    "Помощь по командам"
    await update.message.reply_text(
        "Доступные команды:\n\n"
        "/search <название> - Поиск фильма\n"
        "/top - Топ-10 IMDB\n"
        "/random - Случайный фильм из топ-250\n"
        "/help - Эта справка"
    )

def main() -> None:
    "Запуск бота"
    application = Application.builder().token("7907006203:AAHS8z6Uxc-qDo-O3RMO-5hLYq2jFH7o0sk").build()
    
    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_movie))
    application.add_handler(CommandHandler("top", get_imdb_top))
    application.add_handler(CommandHandler("random", get_random_movie))
    
    logger.info("Бот запущен")
    application.run_polling()

if __name__ == '__main__':
    main()
