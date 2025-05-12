import logging
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import College

logger = logging.getLogger(__name__)

def college_list(request):
    # Get filter parameters with default empty strings
    category = request.GET.get('category', '')
    state = request.GET.get('state', '')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-ranking')  # Default sort by ranking descending
    
    # Clean up parameters - convert "None" string to empty string
    category = '' if category in ['None', 'all'] else category.lower()
    state = '' if state in ['None', 'all'] else state.upper()
    search = '' if search == 'None' else search
    
    # Map frontend category names to database values
    category_mapping = {
        'engineering': 'eng',
        'eng': 'eng',
        'medical': 'medical',
        'dental': 'dental',
        'pharmacy': 'pharmacy',
        'law': 'law',
        'management': 'management',
        'architecture': 'architecture'
    }
    
    # Convert frontend category to database category
    if category:
        category = category_mapping.get(category, category)
    
    logger.debug(f"Filtering colleges with params - category: {category}, state: {state}, search: {search}, sort: {sort}")
    
    # Start with all colleges
    colleges = College.objects.all()
    
    # Apply category filter
    if category:
        logger.debug(f"Filtering by category: {category}")
        colleges = colleges.filter(category=category)
    
    # Apply state filter
    if state:
        logger.debug(f"Filtering by state: {state}")
        colleges = colleges.filter(state=state)
    
    # Apply search filter
    if search:
        logger.debug(f"Searching for: {search}")
        colleges = colleges.filter(
            Q(name__icontains=search) |
            Q(courses_offered__icontains=search)
        )
    
    # Get total count before sorting
    total_count = colleges.count()
    
    # Apply sorting - convert 'rank' to 'ranking' in sort field
    if sort.endswith('rank'):
        sort = ('-' if sort.startswith('-') else '') + 'ranking'
    colleges = colleges.order_by(sort)
    
    logger.debug(f"Total colleges after filtering: {total_count}")
    
    # Pagination
    paginator = Paginator(colleges, 12)  # Show 12 colleges per page
    page = request.GET.get('page')
    colleges = paginator.get_page(page)
    
    # Convert 'ranking' back to 'rank' for template context
    template_sort = sort
    if sort.endswith('ranking'):
        template_sort = ('-' if sort.startswith('-') else '') + 'rank'
    
    context = {
        'colleges': colleges,
        'category': category,
        'state': state,
        'search': search,
        'sort': template_sort,
        'total_colleges': total_count,
        'categories': College.CATEGORIES,
        'states': College.STATES,
    }
    
    return render(request, 'colleges/college_list.html', context)

def college_detail(request, pk):
    college = get_object_or_404(College, pk=pk)
    context = {
        'college': college,
    }
    return render(request, 'colleges/college_detail.html', context)
