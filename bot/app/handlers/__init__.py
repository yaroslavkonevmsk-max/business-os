from aiogram import Router
from app.handlers import commands, text_messages, callbacks, documents, expenses, clients, bank, settings, mini_app

__all__ = [
    "commands", "text_messages", "callbacks", "documents",
    "expenses", "clients", "bank", "settings", "mini_app",
]
