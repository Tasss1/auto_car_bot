from django.core.management.base import BaseCommand
from bot.telegram_bot import setup_bot


class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **options):
        self.stdout.write('🚗 Starting Telegram bot...')
        application = setup_bot()

        try:
            self.stdout.write('✅ Bot is running! Press Ctrl+C to stop')
            application.run_polling()
        except KeyboardInterrupt:
            self.stdout.write('👋 Bot stopped by user')