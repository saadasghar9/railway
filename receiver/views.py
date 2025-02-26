from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .fetch_text import fetch_and_save_text
from textblob import TextBlob
import spacy
import nltk
import os

# Set NLTK data path to a writable directory on Railway
nltk_data_path = os.path.join(os.getenv('HOME', '/app'), 'nltk_data')
nltk.data.path.append(nltk_data_path)

# Download NLTK data if missing
for package in ['punkt', 'brown']:
    try:
        nltk.data.find(f'tokenizers/{package}' if package == 'punkt' else f'corpora/{package}')
    except LookupError:
        nltk.download(package, download_dir=nltk_data_path, quiet=True)


from django.http import HttpResponse

def home(request):
    return HttpResponse("Django server is running!")



# Load spaCy's English model once at startup


def home(request):
    return JsonResponse({"status": "success", "message": "Django server is running!"})

def analyze_text(text):
    nlp = spacy.load("en_core_web_sm")
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

        # Generate a URL for the visualization
        visualization_url = f"{request.scheme}://{request.get_host()}/api/visualize/?text={user_text}"

        return JsonResponse({
            "status": "success",
            "message": "Text received and analyzed",
            "text": user_text,
            "analysis": analysis,
            "visualization_url": visualization_url  # Add this for frontend to fetch visualization
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

        if not url.startswith("http"):
            return JsonResponse({"status": "error", "message": "Invalid URL provided"}, status=400)

        extracted_text = fetch_and_save_text(url)
        if not extracted_text:
            return JsonResponse({"status": "error", "message": "No text extracted from URL"}, status=400)

        analysis = analyze_text(extracted_text)

        return JsonResponse({
            "status": "success",
            "message": "URL processed and analyzed",
            "url": url,
            "extracted_text": extracted_text,
            "analysis": analysis,
            "visualization_data": {"text": extracted_text}  # Data for POST to visualize
        })
    except json.JSONDecodeError as e:
        print(f"JSON Decoding Error: {str(e)}")
        return JsonResponse({"status": "error", "message": f"Invalid JSON: {str(e)}"}, status=400)
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"}, status=500)
@csrf_exempt  # Allow POST requests without CSRF for simplicity (adjust for security in production)
def visualize_entities(request):
    if request.method == 'GET':
        text = request.GET.get('text', '')
        if not text:
            return JsonResponse({"status": "error", "message": "No text provided"}, status=400)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            text = data.get('text', '')
            if not text:
                return JsonResponse({"status": "error", "message": "No text provided in POST body"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON in POST body"}, status=400)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    doc = nlp(text)
    html = spacy.displacy.render(doc, style="ent", page=True)
    return HttpResponse(html, content_type="text/html")