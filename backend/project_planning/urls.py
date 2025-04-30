from django.urls import path
from . import views

urlpatterns = [
    # External Project APIs
    path('create-external-project-request/', views.create_external_project_request, name='create-external-project-request'),
    path('create-external-project-details/', views.create_external_project_details, name='create-external-project-details'),
    path('add-external-project-labor/', views.add_external_project_labor, name='add-external-project-labor'),
    path('add-external-project-equipment/', views.add_external_project_equipment, name='add-external-project-equipment'),
    path('add-external-project-warranty/', views.add_external_project_warranty, name='add-external-project-warranty'),
    
    # Internal Project APIs
    path('create-internal-project/', views.create_internal_project, name='create-internal-project'),
    path('add-internal-project-labor/', views.add_internal_project_labor, name='add-internal-project-labor'),
    path('internal-details/<str:project_request_id>/', views.update_internal_project_details, name='update-internal-project-details'),
    
    # Data Retrieval APIs
    path('get-approval-ids/', views.get_approval_ids, name='get-approval-ids'),
    path('get-order-ids/', views.get_order_ids, name='get-order-ids'),
    path('get-external-project-request-ids/', views.get_external_project_request_ids, name='get-external-project-request-ids'),
    path('get-external-project-ids/', views.get_external_project_ids, name='get-external-project-ids'),
    path('get-employee-ids/', views.get_employee_ids, name='get-employee-ids'),
    path('get-equipment-ids/', views.get_equipment_ids, name='get-equipment-ids'),
    path('get-internal-project-request-ids/', views.get_internal_project_request_ids, name='get-internal-project-request-ids'),
    path('get-internal-project-ids/', views.get_internal_project_ids, name='get-internal-project-ids'),
    path('get-department-ids/', views.get_department_ids, name='get-department-ids'),
    path('get-project-status-values/', views.get_project_status_values, name='get-project-status-values'),
    path('external-details/<str:project_request_id>/', views.update_external_project_details, name='update-external-project-details'),
    path('get-internal-project-status-values/', views.get_internal_project_status_values, name='get-internal-project-status-values'),
    path('add-external-project-cost-management/', views.add_external_project_cost_management, name='add-external-project-cost-management'),
    path('get-bom-ids-from-cost-management/', views.get_bom_ids_from_cost_management, name='get-bom-ids-from-cost-management'),
    path('get-budget-approval-ids-from-cost-management/', views.get_budget_approval_ids_from_cost_management, name='get-budget-approval-ids-from-cost-management'),
    
    # New Project Lists APIs
    path('get-external-project-requests-list/', views.get_external_project_requests_list, name='get-external-project-requests-list'),
    path('get-internal-project-requests-list/', views.get_internal_project_requests_list, name='get-internal-project-requests-list'),
    path('get-external-approval-ids/', views.get_external_approval_ids, name='get-external-approval-ids'),
    path('get-internal-approval-ids/', views.get_internal_approval_ids, name='get-internal-approval-ids'),
]