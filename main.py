import config as cfg
import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message
import google.generativeai as genai

genai.configure(api_key=cfg.API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

app = Client("comment_comments", api_id=cfg.API_ID, api_hash=cfg.API_HASH, phone_number=cfg.PHONE)

discussion_chat_id = None

async def generate_comment(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Ошибка генерации: {e}"

@app.on_message(filters.text)
async def handle_comment(client: Client, message: Message):
    global discussion_chat_id

    if message.chat.username != cfg.target_channel.lstrip('@') and message.chat.id != discussion_chat_id:
        return  # слушаем только группу обсуждения

    # Определить discussion-группу, если ещё не знаем
    if discussion_chat_id is None:
        channel = await client.get_chat(cfg.target_channel)
        if not channel.linked_chat:
            print("❌ У канала нет группы обсуждения.")
            return
        discussion_chat_id = channel.linked_chat.id
        print(f"✅ Обнаружена группа обсуждения: {discussion_chat_id}")

    if message.from_user and message.from_user.is_self:
        return  # не отвечаем на свои же комменты

    if not message.reply_to_message:
        return  # это не комментарий

    # Проверим, ответили ли мы уже на это сообщение
    async for m in client.get_chat_history(message.chat.id, offset_id=message.id, reverse=True):
        if m.reply_to_message and m.reply_to_message.id == message.id and m.from_user and m.from_user.is_self:
            return  # уже ответили

    await asyncio.sleep(random.randint(20, 30))

    comment = await generate_comment(message.text)
    try:
        await message.reply(comment)
        print(f"💬 Ответил на комментарий {message.id}: {comment}")
    except Exception as e:
        print(f"❌ Ошибка при ответе: {e}")

if __name__ == "__main__":
    print("💬 Бот комментариев внутри обсуждений запущен...")
    app.run()
