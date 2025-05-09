from django.shortcuts import render, get_object_or_404
from .models import JobOffer
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from .location_search import load_locations, search_locations, normalize_string

def job_list(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    jobs = JobOffer.objects.all()
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(company__icontains=query)
        )
    if location:
        jobs = jobs.filter(location__icontains=location)
    paginator = Paginator(jobs, 10)  # Show 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'jobs': page_obj.object_list,
        'query': query,
        'location': location,
        'page_obj': page_obj,
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, pk):
    job = get_object_or_404(JobOffer, pk=pk)
    return render(request, 'jobs/job_detail.html', {'job': job})

@require_GET
@csrf_exempt
def location_search(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'results': []})
    locations = load_locations()
    # Ensure all locations have normalized field
    for loc in locations:
        if 'normalized' not in loc:
            loc['normalized'] = normalize_string(loc['label'])
    matches = search_locations(query, locations)
    return JsonResponse({'results': matches[:10]})


# from django.http import StreamingHttpResponse

# def stream_view(request):
#     def content():
#         yield "<html><body>"
#         for i in range(5):
#             yield f"<p>Chunk {i}</p>"
#         yield "</body></html>"
#     return StreamingHttpResponse(content(), content_type="text/html")

# This is useful for large or long-running responses, but note that template 
# rendering is not natively streamable — streaming is best for simple or manually constructed HTML.
