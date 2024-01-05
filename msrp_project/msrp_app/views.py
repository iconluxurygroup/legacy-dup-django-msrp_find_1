import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from msrp_app.models import ScrapingTask
from msrp_app.main_logic import main
from msrp_app.classes_and_utility import *
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import asyncio
#!from channels.db import database_sync_to_async
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
import uuid,datetime
import logging

user_ip_mapping = {
    "192.168.120.191": "Nik, Server",
    "192.168.120.111": "Nik, Main",
    "192.168.120.242" : "Meyer, Ethernet",
    "192.168.120.77" : "Meyer, WIFI",
    "192.168.120.196" : "Kate, Ethernet",
    "192.168.120.89" : "Kate, WIFI",
    "192.168.120.200":"Herbie, Ethernet",
    "192.168.120.204":"Olivia G, Ethernet",
    "192.168.120.97" : "Vlad",
    "192.168.120.198" : "Lily",
}

def get_user_info(ip):
    user_name = user_ip_mapping.get(ip)
    return user_name

def show_ip(request):
    user_ip = request.META.get('REMOTE_ADDR', None)
    logger = logging.getLogger('user_ips')
    logger.info(f'User with IP {user_ip} accessed the site.')
    context = {'user_ip': user_ip}

    user_name = get_user_info(user_ip)

    if user_name:
        context['user_name'] = user_name
        
        print(f'{user_name} accessed the site with {user_ip} IP ')
        return user_ip, user_name
    else:
        return user_ip, None


# global flag
process_running = False

from asgiref.sync import sync_to_async
from django.conf import settings
from django.http import FileResponse
import os

def download(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, f'{file_name}')
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'attachment; filename={file_name}'
            return response
    print('file not found')

def submit_task(request):
    global process_running
    global context
    user = show_ip(request)
    userName = user[1]
    userIP = user[0]
    signTime = datetime.datetime.now()
    print(userName)
    if userName:
        with open(os.path.join(settings.MEDIA_ROOT, 'user_log.txt'), "a") as f:
            f.write(f'{userName} signed on at {signTime} with {userIP}\n')
    else:
        with open(os.path.join(settings.MEDIA_ROOT, 'user_log.txt'), "a") as f:
            f.write(f'Unknown user signed on at {signTime} with {userIP}\n')
    if request.method == 'POST' and not process_running:
        process_running = True
        input_file = request.FILES['file_upload']
        search_column = excel_column_to_number(request.POST['column'])
        
        # Get the keyword and keyword column from the request
        brand_column = excel_column_to_number(request.POST.get('keywordColumn', ''))
        destination_column = excel_column_to_number(request.POST.get('msrpColumn', ''))
        start_row = request.POST.get('startRow', '')

        
        
        

        fs = FileSystemStorage()
        filename = fs.save(input_file.name, input_file)
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        
        start_time = datetime.datetime.now()
        context = {
        'start_time': start_time,
        # ...other context variables...
        }
        if userName:
            with open(os.path.join(settings.MEDIA_ROOT, 'user_log.txt'), "a") as f:
                f.write(f'{userName} started proccess at {start_time}\n')
        else:
            with open(os.path.join(settings.MEDIA_ROOT, 'user_log.txt'), "a") as f:
                f.write(f'Unknown user started proccess at {start_time} with {userIP}\n')
        # Run your main function here
        # If the keyword and keyword column inputs are not both provided, pass them as None
        
        main(file_path, search_column, brand_column, destination_column, int(start_row))
        # Generate the download URL
        download_url = reverse('msrp_app:download', kwargs={'file_name': file_path})
        
        # Return the download URL in a JSON response
        #return JsonResponse({'download_url': download_url})
        process_running = False
        return render(request, 'msrp_app/complete.html', {'download_url': download_url})
    if process_running:
        #return JsonResponse({'status': 'process already running'})
        return render(request, 'msrp_app/busy.html', context)
    return render(request, 'msrp_app/submit_task.html')

def excel_column_to_number(column):
    """
    Convert an Excel column letter (e.g., 'A', 'B', ..., 'AA', etc.)
    into its corresponding zero-based column number. 'A' is 0, 'B' is 1, etc.
    """
    number = 0
    print(column, type(column))
    for index,char in enumerate(column.upper()):
        if not 'A' <= char <= 'Z':
            raise ValueError("Invalid column letter: {}".format(char))
        
        
        number += (26**(len(column)-index-1))*((ord(char) - ord('A'))+1)
    return int(number-1)



from django.conf import settings
from django.http import HttpResponse
import os

def content(request):  
   with open(os.path.join('nik/', 'update.txt')) as f:
       c = f.read()
       return HttpResponse(c)
 