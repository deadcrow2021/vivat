import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class RestaurantBot:
    def __init__(self, token: str):
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CallbackQueryHandler(self.button_handler))


    async def send_order_to_restaurant(self, order_data: dict, restaurant_chat_id: str):
        """Отправка заказа в чат ресторана с кнопками статусов"""
        
        # Формируем текст сообщения
        message_text = order_data['message']
        
        # Создаем клавиатуру с кнопками
        keyboard = [
            [
                InlineKeyboardButton("В работе", callback_data=f"status_inprogress_{order_data['order_id']}"),
                InlineKeyboardButton("В доставке", callback_data=f"status_delivery_{order_data['order_id']}"),
            ],
            [
                InlineKeyboardButton("Завершен", callback_data=f"status_complete_{order_data['order_id']}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем сообщение
        await self.application.bot.send_message(
            chat_id=restaurant_chat_id,
            text=message_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        # Разбираем callback_data
        data_parts = query.data.split('_')
        action = data_parts[0]  # status
        status = data_parts[1]  # inprogress/delivery/complete
        order_id = data_parts[2]  # ID заказа
        
        # Обновляем статус в БД
        success = await self.update_order_status(order_id, status)
        
        if success:
            # Обновляем сообщение с новым статусом
            new_text = query.message.text + f"\n\n<b>Статус: {self.get_status_text(status)}</b>"
            
            # Убираем кнопки после изменения статуса или обновляем их
            await query.edit_message_text(
                text=new_text,
                parse_mode='HTML',
                reply_markup=None  # Убираем кнопки после выбора
            )
            
            # Или если хотите оставить кнопки, но отметить выбранную:
            await self.update_buttons(query, order_id, status)


    async def update_order_status(self, order_id: str, new_status: str) -> bool:
        """Обновление статуса заказа в БД"""
        try:
            # Здесь ваша логика обновления статуса в базе данных
            # Пример:
            # await database.orders.update_one(
            #     {"order_id": order_id},
            #     {"$set": {"status": new_status}}
            # )
            
            # Временная заглушка
            print(f"Updating order {order_id} to status {new_status}")
            return True
            
        except Exception as e:
            logging.error(f"Error updating order status: {e}")
            return False
    
    

    def get_status_text(self, status: str) -> str:
        """Получение текстового представления статуса"""
        status_map = {
            'inprogress': '🔄 В работе',
            'delivery': '🚚 В доставке', 
            'complete': '✅ Завершен'
        }
        return status_map.get(status, status)
    
    async def update_buttons(self, query: Update, order_id: str, current_status: str):
        """Обновление кнопок (альтернативный вариант - оставляем кнопки)"""
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ В работе" if current_status == 'inprogress' else "В работе",
                    callback_data=f"status_inprogress_{order_id}" if current_status != 'inprogress' else None
                ),
                InlineKeyboardButton(
                    "✅ В доставке" if current_status == 'delivery' else "В доставке", 
                    callback_data=f"status_delivery_{order_id}" if current_status != 'delivery' else None
                ),
            ],
            [
                InlineKeyboardButton(
                    "✅ Завершен" if current_status == 'complete' else "Завершен",
                    callback_data=f"status_complete_{order_id}" if current_status != 'complete' else None
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_reply_markup(reply_markup=reply_markup)

    def run(self):
        """Запуск бота"""
        self.application.run_polling()


class OrderService:
    def __init__(self, bot: RestaurantBot):
        self.bot = bot
        # Здесь храним соответствие ресторан -> chat_id
        self.restaurant_chats = {
            'restaurant_1': '-1004903129172',  # -4903129172
        }

    async def create_order(self, order_data: dict):
        """Метод создания заказа"""
        restaurant_chat_id = self.restaurant_chats.get(order_data['restaurant_id'])

        if restaurant_chat_id:
            # Отправляем заказ в чат ресторана
            await self.bot.send_order_to_restaurant(order_data, restaurant_chat_id)


# Пример использования
if __name__ == "__main__":
    bot = RestaurantBot("zxcasdqwe") ###
    order_service = OrderService(bot)
    order_data = {
        'restaurant_id': 123,
        'order_id': 123456,
        'message': 'Заказ на питсу 4 сыра мазерати',
    }
    order_service.create_order(order_data)
    bot.run()
