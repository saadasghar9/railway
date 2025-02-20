from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .fetch_text import fetch_and_save_text
from textblob import TextBlob
import spacy
from django.http import HttpResponse

def home(request):
    return HttpResponse("Django server is running!")



# Load spaCy's English model once at startup
nlp = spacy.load("en_core_web_sm")

def home(request):
    return JsonResponse({"status": "success", "message": "Django server is running!"})

def analyze_text(text):
    try:
        # TextBlob for sentiment and top words
        blob = TextBlob(text)
        word_counts = {word: count for word, count in blob.word_counts.items() if len(word) > 3}  # Filter short words
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]  # Top 5 by frequency
        
        # spaCy for entity recognition
        doc = nlp(text)
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        
        return {
            'sentiment': {
                'score': blob.sentiment.polarity,    # -1.0 to 1.0
                'magnitude': blob.sentiment.subjectivity  # 0.0 to 1.0
            },
            'top_words': [word for word, count in top_words],
            'entities': entities
        }
    except Exception as e:
        raise Exception(f"Analysis error: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def receive_text(request):
    try:
        data = request.body.decode('utf-8')
        if not data:
            return JsonResponse({"status": "error", "message": "No data received"}, status=400)

        body = json.loads(data)
        user_text = body.get('text', '')

        if not user_text:
            return JsonResponse({"status": "error", "message": "Text field is empty"}, status=400)

        with open("received_text.txt", "a", encoding="utf-8") as file:
            file.write(user_text + "\n")

        analysis = analyze_text(user_text)

        return JsonResponse({
            "status": "success",
            "message": "Text received and analyzed",
            "text": user_text,
            "analysis": analysis
        })
    except json.JSONDecodeError as e:
        print(f"JSON Decoding Error: {str(e)}")
        return JsonResponse({"status": "error", "message": f"Invalid JSON: {str(e)}"}, status=400)
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def fetch_text_view(request):
    try:
        data = request.body.decode('utf-8')
        if not data:
            return JsonResponse({"status": "error", "message": "No data received"}, status=400)

        body = json.loads(data)
        url = body.get('url', '')

        if not url:
            return JsonResponse({"status": "error", "message": "URL not provided"}, status=400)

        extracted_text = fetch_and_save_text(url)
        if not extracted_text:
            return JsonResponse({"status": "error", "message": "No text extracted from URL"}, status=400)

        analysis = analyze_text(extracted_text)

        return JsonResponse({
            "status": "success",
            "message": "URL processed and analyzed",
            "url": url,
            "extracted_text": extracted_text,
            "analysis": analysis
        })
    except json.JSONDecodeError as e:
        print(f"JSON Decoding Error: {str(e)}")
        return JsonResponse({"status": "error", "message": f"Invalid JSON: {str(e)}"}, status=400)
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"}, status=500)