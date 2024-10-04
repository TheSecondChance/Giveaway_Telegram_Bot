import json, telebot
from giveaway.bot import bot
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def hook(request):

    body = request.body.decode('utf-8')

    if not body:
        return JsonResponse({'error': 'Request body is empty...'})

    body_data = json.loads(body)
    update = telebot.types.Update.de_json(body_data)
    bot.process_new_updates([update])
    return JsonResponse({"status": "200"}, safe=False)


# TELEGRAM_BOT_WEBHOOK_URL = "https://bcd68b0417f6aeef18b0fe38d16faa40.serveo.net/account/web-hook"

# webhook_url = f'{TELEGRAM_BOT_WEBHOOK_URL}'
# bot.remove_webhook()
# bot.set_webhook(url=webhook_url)
