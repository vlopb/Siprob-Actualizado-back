# myapp/views.py
import os
import uuid
import imghdr
from PIL import Image
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime

@method_decorator(csrf_exempt, name='dispatch')
class FileUploadView(View):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'file': openapi.Schema(type=openapi.TYPE_FILE),
            },
            required=['file'],
        ),
        tags=["Files"],
        operation_summary="Allows to upload a file on the server",
        responses={200: 'Successful file upload'},
    )

    def post(self, request, *args, **kwargs):
        # Reading uploaded file
        file = request.FILES.get('file')
        media_directory='public/'
        if request.POST.get('discriminator')is not None:            
            media_directory = 'public/'+request.POST.get('discriminator')
        if not os.path.exists(media_directory):
                os.makedirs(media_directory)
        if file:
            if request.POST.get('detainee')is not None:
                detainee_name = request.POST.get('detainee')        
            else:
                detainee_name = f"{uuid.uuid4().hex[:10]}"
            current_datetime = datetime.now().strftime('%Y%m%d%H%M%S')        
            _, file_extension = os.path.splitext(file.name)
            new_filename = f"{detainee_name}_{current_datetime}{file_extension}" 

            # Check if the file is an image based on its content type
            if imghdr.what(file):
                # Reset the file cursor after reading it
                file.seek(0)                
                original_file_path = os.path.join(media_directory, new_filename)                
                with open(original_file_path, 'wb') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                # Generate and save a thumbnail
                thumbnail_filename = f"thumbnail_{new_filename}"
                thumbnail_file_path = os.path.join(media_directory, thumbnail_filename)
                # Open the original image using Pillow
                with Image.open(original_file_path) as img:
                    # Resize the image to create a thumbnail
                    thumbnail_size = (200,200)  # Adjust the size as needed
                    img.thumbnail(thumbnail_size)                    
                    # Save the thumbnail
                    img.save(thumbnail_file_path)                          
            else:
                # File is not an image
                original_file_path = os.path.join(media_directory, new_filename)                
                with open(original_file_path, 'wb') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

            if request.POST.get('discriminator')is not None:            
                    response_path = media_directory+'/'+new_filename
            else:                                  
                response_path = 'public/'+new_filename

            return JsonResponse({'status': 'success', 
                                'data':{'path': response_path, 'fileName': new_filename}})   
        else:
            return JsonResponse({'status': 'error', 'message': 'No file provided'})
        
class FileServeView(View):
    def get(self, request, filename, *args, **kwargs):
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response

