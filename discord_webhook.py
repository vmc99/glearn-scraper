from discord_webhooks import DiscordWebhooks
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('keys.env')

load_dotenv(dotenv_path=dotenv_path)


webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

def send_msg(class_name,link,status,date,start_time,end_time):

    WEBHOOK_URL = webhook_url 

    webhook = DiscordWebhooks(WEBHOOK_URL)
    

    if(status=="fetched"):

      webhook.set_content(title='Zoom Class',
                          description="Here's your Link :zap:")

      # Appends a field
      webhook.add_field(name='Class', value=class_name)
      webhook.add_field(name='Zoom link', value=link)
      webhook.add_field(name='Date', value=date)
      webhook.add_field(name='Start time', value=start_time)
      webhook.add_field(name='End time', value=end_time)
    


    elif(status=="noclass"):
      webhook.set_content(title='Zoom Class',
                          description="Class Link Not Found! Assuming no class :sunglasses:")

      # Appends a field
      webhook.add_field(name='Class', value=class_name)
      webhook.add_field(name='Date', value=date)
      webhook.add_field(name='Start time', value=start_time)
      webhook.add_field(name='End time', value=end_time)




    elif(status=="G-learn down"):
      webhook.set_content(title='G-learn Is Not Responding',
                          description="Link bot failed to fetch :boom:")

      # Appends a field
      webhook.add_field(name='Status', value=status)



    # Attaches a footer
    webhook.set_footer(text='-- Zoom Links')


    webhook.send()

    print("Sent message to discord")
