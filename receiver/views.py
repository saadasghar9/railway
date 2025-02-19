from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .fetch_text import fetch_and_save_text
from django.http import HttpResponse

def home(request):
    return HttpResponse("Django server is running!")

@csrf_exempt
@require_http_methods(["POST"])
def receive_text(request):
    try:
        # Decode the request body
        data = request.body.decode('utf-8')
        print("Received data:", data)  # For debugging, remove in production

        # Try to parse JSON
        if not data:  # Check if data is empty
            return JsonResponse({"status": "error", "message": "No data received in request body"}, status=400)
        
        body = json.loads(data)
        user_text = body.get('text', '')

        with open("received_text.txt", "a", encoding="utf-8") as file:
            file.write(user_text + "\n")

        return JsonResponse({"status": "success", "message": "Text received!"})
    except json.JSONDecodeError as e:
        print("JSON Decoding Error:", str(e))  # Log the specific JSON error
        return JsonResponse({"status": "error", "message": f"Invalid JSON: {str(e)}"}, status=400)
    except Exception as e:
        print("General Error:", str(e))  # Log any other exceptions
        return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def fetch_text_view(request):
    try:
        data = request.body.decode('utf-8')
        body = json.loads(data)
        url = body.get('url', '')
        if url:
            result = fetch_and_save_text(url)
            return HttpResponse(json.dumps({"status": "success", "message": result}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"status": "error", "message": "URL not provided"}), content_type="application/json", status=400)
    except json.JSONDecodeError:
        return HttpResponse(json.dumps({"status": "error", "message": "Invalid JSON"}), content_type="application/json", status=400)
    except Exception as e:
        return HttpResponse(json.dumps({"status": "error", "message": str(e)}), content_type="application/json", status=500)
# from django.views.decorators.csrf import csrf_exempt
# from django.http import HttpResponse, JsonResponse
# from django.views.decorators.http import require_http_methods
# import json

# def home(request):
#     return HttpResponse("Django server is running!")
# @csrf_exempt
# @require_http_methods(["POST"])
# def receive_text(request):
#     try:
#         body = json.loads(request.body.decode('utf-8'))
#         user_text = body.get('text', '')
        
#         with open("received_text.txt", "a", encoding="utf-8") as file:
#             file.write(user_text + "\n")
        
#         return JsonResponse({"status": "success", "message": "Text received!"})
#     except json.JSONDecodeError:
#         return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)