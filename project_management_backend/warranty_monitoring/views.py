# warranty_monitoring/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import json

from .models import ExternalProjectWarranty

@login_required
@require_POST
def archive_warranties(request):
    try:
        data = json.loads(request.body)
        warranty_ids = data.get('warranty_ids', [])
        
        # Get currently archived warranties from session
        archived_warranties = request.session.get('archived_warranties', [])
        
        # Add new warranties to archived list
        newly_archived = 0
        for warranty_id in warranty_ids:
            if warranty_id not in archived_warranties:
                archived_warranties.append(warranty_id)
                newly_archived += 1
        
        # Save back to session
        request.session['archived_warranties'] = archived_warranties
        request.session.modified = True
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully archived {newly_archived} warranties'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=500)

@login_required
@require_POST
def restore_warranties(request):
    try:
        data = json.loads(request.body)
        warranty_ids = data.get('warranty_ids', [])
        
        # Get currently archived warranties from session
        archived_warranties = request.session.get('archived_warranties', [])
        
        # Remove warranties from archived list
        restored_count = 0
        for warranty_id in warranty_ids:
            if warranty_id in archived_warranties:
                archived_warranties.remove(warranty_id)
                restored_count += 1
        
        # Save back to session
        request.session['archived_warranties'] = archived_warranties
        request.session.modified = True
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully restored {restored_count} warranties'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=500)

class WarrantyListView(ListView):
    template_name = 'warranty_monitoring/warranty_list.html'
    context_object_name = 'warranties'
    model = ExternalProjectWarranty
    paginate_by = 6
    
    def get_queryset(self):
        # Get the archive filter from the query parameters
        show_archived = self.request.GET.get('archived', 'false').lower() == 'true'
        
        # Get archived warranty IDs from session
        archived_warranties = self.request.session.get('archived_warranties', [])
        
        # Start with all warranties
        queryset = ExternalProjectWarranty.objects.all()
        
        # Filter based on archived status
        if show_archived:
            if archived_warranties:
                queryset = queryset.filter(project_warranty_id__in=archived_warranties)
            else:
                # If no archived warranties, return an empty queryset
                return ExternalProjectWarranty.objects.none()
        else:
            if archived_warranties:
                queryset = queryset.exclude(project_warranty_id__in=archived_warranties)
        
        # Apply ordering
        queryset = queryset.order_by('-warranty_end_date')
        
        # Apply search filter
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(project_warranty_id__icontains=search_query) |
                Q(project__project_id__icontains=search_query)
            )
        
        # Apply time filter
        days_filter = self.request.GET.get('days', '')
        if days_filter and days_filter != 'all':
            try:
                days = int(days_filter)
                date_threshold = timezone.now().date() - timedelta(days=days)
                queryset = queryset.filter(
                    Q(warranty_start_date__gte=date_threshold) |
                    Q(warranty_end_date__gte=date_threshold)
                )
            except ValueError:
                pass
        
        # Apply status filter
        status_filter = self.request.GET.get('status', '')
        today = timezone.now().date()
        thirty_days_later = today + timedelta(days=30)
        
        if status_filter == 'active':
            queryset = queryset.filter(
                warranty_start_date__lte=today,
                warranty_end_date__gt=thirty_days_later
            )
        elif status_filter == 'expiring_soon':
            queryset = queryset.filter(
                warranty_start_date__lte=today,
                warranty_end_date__gt=today,
                warranty_end_date__lte=thirty_days_later
            )
        elif status_filter == 'expired':
            queryset = queryset.filter(warranty_end_date__lt=today)
        elif status_filter == 'not_started':
            queryset = queryset.filter(warranty_start_date__gt=today)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['days_filter'] = self.request.GET.get('days', 'all')
        context['status_filter'] = self.request.GET.get('status', 'all')
        context['show_archived'] = self.request.GET.get('archived', 'false').lower() == 'true'
        
        # For pagination display when showing archived items but there are none
        if context['show_archived'] and not context['warranties']:
            context['is_paginated'] = True
            from django.core.paginator import Paginator, Page
            paginator = Paginator([], 6)
            page = Page([], 1, paginator)
            page.paginator.num_pages = 1  # Just one empty page
            context['paginator'] = paginator
            context['page_obj'] = page
        
        return context