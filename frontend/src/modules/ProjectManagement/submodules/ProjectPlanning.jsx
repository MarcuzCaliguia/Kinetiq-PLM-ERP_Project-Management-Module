import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/ProjectPlanning.css";

const ProjectPlanningDashboard = () => {
  // State for active view/form
  const [activeView, setActiveView] = useState("dashboard");
  const [selectedProjectType, setSelectedProjectType] = useState("external");
  const [editMode, setEditMode] = useState(false);
  const [editId, setEditId] = useState(null);
  const [message, setMessage] = useState({ text: "", type: "" });
  
  // Data lists for dropdowns
  const [approvalIds, setApprovalIds] = useState([]);
  const [orderIds, setOrderIds] = useState([]);
  const [projectRequestIds, setProjectRequestIds] = useState([]);
  const [projectIds, setProjectIds] = useState([]);
  const [employeeIds, setEmployeeIds] = useState([]);
  const [equipmentIds, setEquipmentIds] = useState([]);
  const [internalProjectRequestIds, setInternalProjectRequestIds] = useState([]);
  const [internalProjectIds, setInternalProjectIds] = useState([]);
  const [departmentIds, setDepartmentIds] = useState([]);
  const [projectStatusOptions, setProjectStatusOptions] = useState([]);
  const [internalProjectStatusOptions, setInternalProjectStatusOptions] = useState([]);
  const [bomIds, setBomIds] = useState([]);
  const [budgetApprovalIds, setBudgetApprovalIds] = useState([]);
  
  // Form data states
  // External Project Request Form
  const [externalProjectRequestForm, setExternalProjectRequestForm] = useState({
    projectName: "",
    projectDescription: "",
    approvalId: "",
    orderId: ""
  });
  
  // External Project Details Form
  const [externalProjectDetailsForm, setExternalProjectDetailsForm] = useState({
    projectRequestId: "",
    projectStatus: ""
  });
  
  // External Project Labor Form
  const [externalProjectLaborForm, setExternalProjectLaborForm] = useState({
    projectId: "",
    jobRoleNeeded: "",
    employeeId: ""
  });
  
  // External Project Equipment Form
  const [externalProjectEquipmentForm, setExternalProjectEquipmentForm] = useState({
    projectId: "",
    projectEquipmentId: ""
  });
  
  // External Project Warranty Form
  const [externalProjectWarrantyForm, setExternalProjectWarrantyForm] = useState({
    projectId: "",
    warrantyCoverageYear: "",
    warrantyStartDate: "",
    warrantyEndDate: ""
  });
  
  // External Project Cost Management Form
  const [externalProjectCostForm, setExternalProjectCostForm] = useState({
    projectId: "",
    bomId: "",
    projectBudgetApproval: ""
  });
  
  // Internal Project Request Form
  const [internalProjectRequestForm, setInternalProjectRequestForm] = useState({
    projectName: "",
    requestDate: "",
    startingDate: "",
    employeeId: "",
    departmentId: "",
    budgetRequest: "",
    budgetDescription: ""
  });
  
  // Internal Project Details Form
  const [internalProjectDetailsForm, setInternalProjectDetailsForm] = useState({
    projectRequestId: "",
    projectStatus: "",
    approvalId: "",
    projectDescription: ""
  });
  
  // Internal Project Labor Form
  const [internalProjectLaborForm, setInternalProjectLaborForm] = useState({
    projectId: "",
    jobRole: "",
    employeeId: ""
  });

  // Fetch all dropdown data on component mount
  useEffect(() => {
    const fetchDropdownData = async () => {
      try {
        const [
          approvalRes, 
          orderRes, 
          projectReqRes, 
          projectIdRes, 
          employeeRes, 
          equipmentRes,
          intProjectReqRes,
          intProjectIdRes,
          departmentRes,
          projectStatusRes,
          internalProjectStatusRes,
          bomIdsRes,
          budgetApprovalIdsRes
        ] = await Promise.all([
          axios.get('/api/project-planning/get-approval-ids/'),
          axios.get('/api/project-planning/get-order-ids/'),
          axios.get('/api/project-planning/get-external-project-request-ids/'),
          axios.get('/api/project-planning/get-external-project-ids/'),
          axios.get('/api/project-planning/get-employee-ids/'),
          axios.get('/api/project-planning/get-equipment-ids/'),
          axios.get('/api/project-planning/get-internal-project-request-ids/'),
          axios.get('/api/project-planning/get-internal-project-ids/'),
          axios.get('/api/project-planning/get-department-ids/'),
          axios.get('/api/project-planning/get-project-status-values/'),
          axios.get('/api/project-planning/get-internal-project-status-values/'),
          axios.get('/api/project-planning/get-bom-ids-from-cost-management/'),
          axios.get('/api/project-planning/get-budget-approval-ids-from-cost-management/')
        ]);
        
        setApprovalIds(approvalRes.data);
        setOrderIds(orderRes.data);
        setProjectRequestIds(projectReqRes.data);
        setProjectIds(projectIdRes.data);
        setEmployeeIds(employeeRes.data);
        setEquipmentIds(equipmentRes.data);
        setInternalProjectRequestIds(intProjectReqRes.data);
        setInternalProjectIds(intProjectIdRes.data);
        setDepartmentIds(departmentRes.data);
        setProjectStatusOptions(projectStatusRes.data);
        setInternalProjectStatusOptions(internalProjectStatusRes.data);
        setBomIds(bomIdsRes.data);
        setBudgetApprovalIds(budgetApprovalIdsRes.data);
        
      } catch (error) {
        console.error("Error fetching dropdown data:", error);
        setMessage({ 
          text: "Failed to load data. Please refresh the page.", 
          type: "error" 
        });
      }
    };
    
    fetchDropdownData();
  }, []);

  // Handle form input changes
  const handleInputChange = (formName, fieldName, value) => {
    switch(formName) {
      case 'externalProjectRequest':
        setExternalProjectRequestForm({
          ...externalProjectRequestForm,
          [fieldName]: value
        });
        break;
      case 'externalProjectDetails':
        setExternalProjectDetailsForm({
          ...externalProjectDetailsForm,
          [fieldName]: value
        });
        break;
      case 'externalProjectLabor':
        setExternalProjectLaborForm({
          ...externalProjectLaborForm,
          [fieldName]: value
        });
        break;
      case 'externalProjectEquipment':
        setExternalProjectEquipmentForm({
          ...externalProjectEquipmentForm,
          [fieldName]: value
        });
        break;
      case 'externalProjectWarranty':
        setExternalProjectWarrantyForm({
          ...externalProjectWarrantyForm,
          [fieldName]: value
        });
        break;
      case 'externalProjectCost':
        setExternalProjectCostForm({
          ...externalProjectCostForm,
          [fieldName]: value
        });
        break;
      case 'internalProjectRequest':
        setInternalProjectRequestForm({
          ...internalProjectRequestForm,
          [fieldName]: value
        });
        break;
      case 'internalProjectDetails':
        setInternalProjectDetailsForm({
          ...internalProjectDetailsForm,
          [fieldName]: value
        });
        break;
      case 'internalProjectLabor':
        setInternalProjectLaborForm({
          ...internalProjectLaborForm,
          [fieldName]: value
        });
        break;
      default:
        break;
    }
  };

  // Form submission handlers
  const handleExternalProjectRequestSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/project-planning/create-external-project-request/', {
        ProjectName: externalProjectRequestForm.projectName,
        ProjectDescription: externalProjectRequestForm.projectDescription,
        ApprovalID: externalProjectRequestForm.approvalId,
        OrderID: externalProjectRequestForm.orderId,
        ProjectStatus: "Pending"
      });
      
      setMessage({ 
        text: "External project request created successfully!", 
        type: "success" 
      });
      
      // Refresh project request IDs
      const projectReqRes = await axios.get('/api/project-planning/get-external-project-request-ids/');
      setProjectRequestIds(projectReqRes.data);
      
      // Reset form
      setExternalProjectRequestForm({
        projectName: "",
        projectDescription: "",
        approvalId: "",
        orderId: ""
      });
      
      // Return to dashboard
      setActiveView("dashboard");
    } catch (error) {
      console.error("Error creating project:", error);
      setMessage({ 
        text: "Failed to create project. Please try again.", 
        type: "error" 
      });
    }
  };

  const handleExternalProjectDetailsSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.put(
        `/api/project-planning/external-details/${externalProjectDetailsForm.projectRequestId}/`, 
        {
          project_status: externalProjectDetailsForm.projectStatus
        }
      );
      
      setMessage({ 
        text: "Project details updated successfully!", 
        type: "success" 
      });
      
      // Refresh project IDs
      const projectIdRes = await axios.get('/api/project-planning/get-external-project-ids/');
      setProjectIds(projectIdRes.data);
      
      // Reset form
      setExternalProjectDetailsForm({
        projectRequestId: "",
        projectStatus: ""
      });
      
      // Return to dashboard
      setActiveView("dashboard");
    } catch (error) {
      console.error("Error updating project details:", error);
      setMessage({ 
        text: "Failed to update project details. Please try again.", 
        type: "error" 
      });
    }
  };

  const handleExternalProjectLaborSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/project-planning/add-external-project-labor/', {
        ProjectID: externalProjectLaborForm.projectId,
        JobRoleNeeded: externalProjectLaborForm.jobRoleNeeded,
        EmployeeID: externalProjectLaborForm.employeeId
      });
      
      setMessage({ 
        text: "Project labor added successfully!", 
        type: "success" 
      });
      
      // Reset form
      setExternalProjectLaborForm({
        projectId: "",
        jobRoleNeeded: "",
        employeeId: ""
      });
      
      // Return to dashboard
      setActiveView("dashboard");
    } catch (error) {
      console.error("Error adding project labor:", error);
      setMessage({ 
        text: "Failed to add project labor. Please try again.", 
        type: "error" 
      });
    }
  };

  // Added missing form submission handlers
  const handleExternalProjectEquipmentSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/project-planning/add-external-project-equipment/', {
        ProjectID: externalProjectEquipmentForm.projectId,
        ProjectEquipmentID: externalProjectEquipmentForm.projectEquipmentId    
      });
      
      setMessage({ 
        text: "Project equipment added successfully!", 
        type: "success" 
      });
      
      // Reset form
      setExternalProjectEquipmentForm({
        projectId: "",
        projectEquipmentId: ""
      });
      
      // Return to dashboard
      setActiveView("dashboard");
    } catch (error) {
      console.error("Error adding project equipment:", error);
      setMessage({ 
        text: "Failed to add project equipment. Please try again.", 
        type: "error" 
      });
    }
  };

  const handleExternalProjectWarrantySubmit = async (e) => {
    e.preventDefault();
    
    // Validate dates
    const startDate = new Date(externalProjectWarrantyForm.warrantyStartDate);
    const endDate = new Date(externalProjectWarrantyForm.warrantyEndDate);
    
    if (endDate <= startDate) {
      setMessage({ 
        text: "Warranty end date must be after warranty start date", 
        type: "error" 
      });
      return;
    }
    
    try {
      const response = await axios.post('/api/project-planning/add-external-project-warranty/', {
        ProjectID: externalProjectWarrantyForm.projectId,
        Warrantycoverageyear: externalProjectWarrantyForm.warrantyCoverageYear,
        Warrantystartdate: externalProjectWarrantyForm.warrantyStartDate,
        Warrantyenddate: externalProjectWarrantyForm.warrantyEndDate
      });
      
      setMessage({ 
        text: "Project warranty added successfully!", 
        type: "success" 
      });
      
      // Reset form
      setExternalProjectWarrantyForm({
        projectId: "",
        warrantyCoverageYear: "",
        warrantyStartDate: "",
        warrantyEndDate: ""
      });
      
      // Return to dashboard
      setActiveView("dashboard");
    } catch (error) {
      console.error("Error adding project warranty:", error);
      if (error.response && error.response.data && error.response.data.error) {
        setMessage({ 
          text: `Failed to add project warranty: ${error.response.data.error}`, 
          type: "error" 
        });
      } else {
        setMessage({ 
          text: "Failed to add project warranty. Please try again.", 
          type: "error" 
        });
      }
    }
  };

  const handleExternalProjectCostSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/project-planning/add-external-project-cost-management/', {
        ProjectID: externalProjectCostForm.projectId,
        BomID: externalProjectCostForm.bomId,
        ProjectBudgetApproval: externalProjectCostForm.projectBudgetApproval
      });
      
      setMessage({ 
        text: "Project cost management added successfully!", 
        type: "success" 
      });
      
      // Reset form
      setExternalProjectCostForm({
        projectId: "",
        bomId: "",
        projectBudgetApproval: ""
      });
      
      // Return to dashboard
      setActiveView("dashboard");
    } catch (error) {
      console.error("Error adding project cost management:", error);
      if (error.response && error.response.data && error.response.data.error) {
        setMessage({ 
          text: `Failed to add project cost management: ${error.response.data.error}`, 
          type: "error" 
        });
      } else {
        setMessage({ 
          text: "Failed to add project cost management. Please try again.", 
          type: "error" 
        });
      }
    }
  };

  const handleInternalProjectRequestSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/project-planning/create-internal-project/', {
        ProjectNameint: internalProjectRequestForm.projectName,
        RequestDateint: internalProjectRequestForm.requestDate,
        Startingdateint: internalProjectRequestForm.startingDate,
        EmployeeIDint: internalProjectRequestForm.employeeId,
        DepartmentIDint: internalProjectRequestForm.departmentId,
        Budgetrequestint: internalProjectRequestForm.budgetRequest,
        Budgetdescriptionint: internalProjectRequestForm.budgetDescription
      });
      
      setMessage({ 
        text: "Internal project request created successfully!", 
        type: "success" 
      });
      
      // Refresh internal project request IDs
      const intProjectReqRes = await axios.get('/api/project-planning/get-internal-project-request-ids/');
      setInternalProjectRequestIds(intProjectReqRes.data);
      
      // Reset form
      setInternalProjectRequestForm({
        projectName: "",
        requestDate: "",
        startingDate: "",
        employeeId: "",
        departmentId: "",
        budgetRequest: "",
        budgetDescription: ""
      });
      
      // Return to dashboard
      setActiveView("dashboard");
    } catch (error) {
      console.error("Error creating internal project:", error);
      setMessage({ 
        text: "Failed to create internal project. Please try again.", 
        type: "error" 
      });
    }
  };

  const handleInternalProjectDetailsSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.put(`/api/project-planning/internal-details/${internalProjectDetailsForm.projectRequestId}/`, {
        intrnl_project_status: internalProjectDetailsForm.projectStatus,
        approval_id: internalProjectDetailsForm.approvalId,
        project_description: internalProjectDetailsForm.projectDescription
      });
      
      setMessage({ 
        text: "Internal project details updated successfully!", 
        type: "success" 
      });
      
      // Refresh internal project IDs
      const intProjectIdRes = await axios.get('/api/project-planning/get-internal-project-ids/');
      setInternalProjectIds(intProjectIdRes.data);
      
      // Reset form
      setInternalProjectDetailsForm({
        projectRequestId: "",
        projectStatus: "",
        approvalId: "",
        projectDescription: ""
      });
      
      // Return to dashboard
      setActiveView("dashboard");
    } catch (error) {
      console.error("Error updating internal project details:", error);
      setMessage({ 
        text: "Failed to update internal project details. Please try again.", 
        type: "error" 
      });
    }
  };

  const handleInternalProjectLaborSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/project-planning/add-internal-project-labor/', {
        Projectidint: internalProjectLaborForm.projectId, 
        Jobroleint: internalProjectLaborForm.jobRole,
        EmployeeIDint: internalProjectLaborForm.employeeId
      });
      
      setMessage({ 
        text: "Internal project labor added successfully!", 
        type: "success" 
      });
      
      // Reset form
      setInternalProjectLaborForm({
        projectId: "",
        jobRole: "",
        employeeId: ""
      });
      
      // Return to dashboard
      setActiveView("dashboard");
    } catch (error) {
      console.error("Error adding internal project labor:", error);
      setMessage({ 
        text: "Failed to add internal project labor. Please try again.", 
        type: "error" 
      });
    }
  };

  // Function to render the dashboard
  const renderDashboard = () => {
    return (
      <div className="project-planning-dashboard">
        <h2 className="dashboard-title">Project Planning Dashboard</h2>
        
        <div className="dashboard-tabs">
          <button 
            className={`dashboard-tab ${selectedProjectType === 'external' ? 'active' : ''}`}
            onClick={() => setSelectedProjectType('external')}
          >
            External Projects
          </button>
          <button 
            className={`dashboard-tab ${selectedProjectType === 'internal' ? 'active' : ''}`}
            onClick={() => setSelectedProjectType('internal')}
          >
            Internal Projects
          </button>
        </div>
        
        <div className="dashboard-cards">
          {selectedProjectType === 'external' ? (
            <>
              <div className="dashboard-card" onClick={() => setActiveView("externalProjectRequest")}>
                <h3>Project Request</h3>
                <p>Create a new external project request</p>
              </div>
              <div className="dashboard-card" onClick={() => setActiveView("externalProjectDetails")}>
                <h3>Project Details</h3>
                <p>Update external project details and status</p>
              </div>
              <div className="dashboard-card" onClick={() => setActiveView("externalProjectLabor")}>
                <h3>Project Labor</h3>
                <p>Assign labor resources to external projects</p>
              </div>
              <div className="dashboard-card" onClick={() => setActiveView("externalProjectEquipment")}>
                <h3>Project Equipment</h3>
                <p>Assign equipment to external projects</p>
              </div>
              <div className="dashboard-card" onClick={() => setActiveView("externalProjectWarranty")}>
                <h3>Project Warranty</h3>
                <p>Set up warranty details for external projects</p>
              </div>
              <div className="dashboard-card" onClick={() => setActiveView("externalProjectCost")}>
                <h3>Project Cost Management</h3>
                <p>Manage costs for external projects</p>
              </div>
            </>
          ) : (
            <>
              <div className="dashboard-card" onClick={() => setActiveView("internalProjectRequest")}>
                <h3>Project Request</h3>
                <p>Create a new internal project request</p>
              </div>
              <div className="dashboard-card" onClick={() => setActiveView("internalProjectDetails")}>
                <h3>Project Details</h3>
                <p>Update internal project details and status</p>
              </div>
              <div className="dashboard-card" onClick={() => setActiveView("internalProjectLabor")}>
                <h3>Project Labor</h3>
                <p>Assign labor resources to internal projects</p>
              </div>
            </>
          )}
        </div>
      </div>
    );
  };

  // Function to render External Project Request Form
  const renderExternalProjectRequestForm = () => {
    return (
      <div className="project-form-container">
        <h2 className="form-title">External Project Request</h2>
        <form onSubmit={handleExternalProjectRequestSubmit} className="project-form">
          <div className="form-group">
            <label className="form-label">
              <b>Project Name*</b>
            </label>
            <input
              className="form-input"
              type="text"
              placeholder="Name"
              value={externalProjectRequestForm.projectName}
              onChange={(e) => handleInputChange('externalProjectRequest', 'projectName', e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <b>Project Description</b>
            </label>
            <textarea
              className="form-textarea"
              placeholder="Add Description"
              value={externalProjectRequestForm.projectDescription}
              onChange={(e) => handleInputChange('externalProjectRequest', 'projectDescription', e.target.value)}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">
                <b>Approval ID</b>
              </label>
              <select
                className="form-select"
                value={externalProjectRequestForm.approvalId}
                onChange={(e) => handleInputChange('externalProjectRequest', 'approvalId', e.target.value)}
                required
              >
                <option value="">Select Approval ID</option>
                {approvalIds.map((id) => (
                  <option key={id} value={id}>{id}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">
                <b>Order ID*</b>
              </label>
              <select
                className="form-select"
                value={externalProjectRequestForm.orderId}
                onChange={(e) => handleInputChange('externalProjectRequest', 'orderId', e.target.value)}
                required
              >
                <option value="">Select Order ID</option>
                {orderIds.map((id) => (
                  <option key={id} value={id}>{id}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="form-button save-button">
              <b>Save</b>
            </button>
            <button 
              type="button" 
              className="form-button cancel-button"
              onClick={() => {
                setActiveView("dashboard");
                setExternalProjectRequestForm({
                  projectName: "",
                  projectDescription: "",
                  approvalId: "",
                  orderId: ""
                });
              }}
            >
              <b>Cancel</b>
            </button>
          </div>
        </form>
      </div>
    );
  };

  // Function to render External Project Details Form
  const renderExternalProjectDetailsForm = () => {
    return (
      <div className="project-form-container">
        <h2 className="form-title">External Project Details</h2>
        <form onSubmit={handleExternalProjectDetailsSubmit} className="project-form">
          <div className="form-group">
            <label className="form-label">
              <b>Project Request ID*</b>
            </label>
            <select
              className="form-select"
              value={externalProjectDetailsForm.projectRequestId}
              onChange={(e) => handleInputChange('externalProjectDetails', 'projectRequestId', e.target.value)}
              required
            >
              <option value="">Select Project Request ID</option>
              {projectRequestIds.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label"><b>Project Status</b></label>
            <select
              className="form-select"
              value={externalProjectDetailsForm.projectStatus}
              onChange={(e) => handleInputChange('externalProjectDetails', 'projectStatus', e.target.value)}
              required
            >
              <option value="">Choose Project Status</option>
              {projectStatusOptions.map((status) => (
                <option key={status} value={status}>{status.replace('_', ' ')}</option>
              ))}
            </select>
          </div>

          <div className="form-actions">
            <button type="submit" className="form-button save-button">
              <b>Save</b>
            </button>
            <button 
              type="button" 
              className="form-button cancel-button"
              onClick={() => {
                setActiveView("dashboard");
                setExternalProjectDetailsForm({
                  projectRequestId: "",
                  projectStatus: ""
                });
              }}
            >
              <b>Cancel</b>
            </button>
          </div>
        </form>
      </div>
    );
  };

  // Function to render External Project Labor Form
  const renderExternalProjectLaborForm = () => {
    return (
      <div className="project-form-container">
        <h2 className="form-title">External Project Labor</h2>
        <form onSubmit={handleExternalProjectLaborSubmit} className="project-form">
          <div className="form-group">
            <label className="form-label">
              <b>Project ID*</b>
            </label>
            <select
              className="form-select"
              value={externalProjectLaborForm.projectId}
              onChange={(e) => handleInputChange('externalProjectLabor', 'projectId', e.target.value)}
              required
            >
              <option value="">Select Project ID</option>
              {projectIds.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">
                <b>Job Role Needed*</b>
              </label>
              <input
                className="form-input"
                type="text"
                placeholder="Job Role"
                value={externalProjectLaborForm.jobRoleNeeded}
                onChange={(e) => handleInputChange('externalProjectLabor', 'jobRoleNeeded', e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                <b>Employee ID*</b>
              </label>
              <select
                className="form-select"
                value={externalProjectLaborForm.employeeId}
                onChange={(e) => handleInputChange('externalProjectLabor', 'employeeId', e.target.value)}
                required
              >
                <option value="">Select Employee ID</option>
                {employeeIds.map((id) => (
                  <option key={id} value={id}>{id}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="form-button save-button">
              <b>Save</b>
            </button>
            <button 
              type="button" 
              className="form-button cancel-button"
              onClick={() => {
                setActiveView("dashboard");
                setExternalProjectLaborForm({
                  projectId: "",
                  jobRoleNeeded: "",
                  employeeId: ""
                });
              }}
            >
              <b>Cancel</b>
            </button>
          </div>
        </form>
      </div>
    );
  };

  // Added missing form rendering functions
  // Function to render External Project Equipment Form
  const renderExternalProjectEquipmentForm = () => {
    return (
      <div className="project-form-container">
        <h2 className="form-title">External Project Equipment</h2>
        <form onSubmit={handleExternalProjectEquipmentSubmit} className="project-form">
          <div className="form-group">
            <label className="form-label">
              <b>Project ID*</b>
            </label>
            <select
              className="form-select"
              value={externalProjectEquipmentForm.projectId}
              onChange={(e) => handleInputChange('externalProjectEquipment', 'projectId', e.target.value)}
              required
            >
              <option value="">Select Project ID</option>
              {projectIds.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">
              <b>Project Equipment ID*</b>
            </label>
            <select
              className="form-select"
              value={externalProjectEquipmentForm.projectEquipmentId}
              onChange={(e) => handleInputChange('externalProjectEquipment', 'projectEquipmentId', e.target.value)}
              required
            >
              <option value="">Select Equipment ID</option>
              {equipmentIds.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>

          <div className="form-actions">
            <button type="submit" className="form-button save-button">
              <b>Save</b>
            </button>
            <button 
              type="button" 
              className="form-button cancel-button"
              onClick={() => {
                setActiveView("dashboard");
                setExternalProjectEquipmentForm({
                  projectId: "",
                  projectEquipmentId: ""
                });
              }}
            >
              <b>Cancel</b>
            </button>
          </div>
        </form>
      </div>
    );
  };

  // Function to render External Project Warranty Form
  const renderExternalProjectWarrantyForm = () => {
    return (
      <div className="project-form-container">
        <h2 className="form-title">External Project Warranty</h2>
        <form onSubmit={handleExternalProjectWarrantySubmit} className="project-form">
          <div className="form-group">
            <label className="form-label">
              <b>Project ID*</b>
            </label>
            <select
              className="form-select"
              value={externalProjectWarrantyForm.projectId}
              onChange={(e) => handleInputChange('externalProjectWarranty', 'projectId', e.target.value)}
              required
            >
              <option value="">Select Project ID</option>
              {projectIds.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">
              <b>Warranty Coverage Year*</b>
            </label>
            <input
              className="form-input"
              type="number"
              placeholder="Coverage in years"
              value={externalProjectWarrantyForm.warrantyCoverageYear}
              onChange={(e) => handleInputChange('externalProjectWarranty', 'warrantyCoverageYear', e.target.value)}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">
                <b>Warranty Start Date*</b>
              </label>
              <input
                className="form-input"
                type="date"
                value={externalProjectWarrantyForm.warrantyStartDate}
                onChange={(e) => handleInputChange('externalProjectWarranty', 'warrantyStartDate', e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                <b>Warranty End Date*</b>
              </label>
              <input
                className="form-input"
                type="date"
                value={externalProjectWarrantyForm.warrantyEndDate}
                onChange={(e) => handleInputChange('externalProjectWarranty', 'warrantyEndDate', e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="form-button save-button">
              <b>Save</b>
            </button>
            <button 
              type="button" 
              className="form-button cancel-button"
              onClick={() => {
                setActiveView("dashboard");
                setExternalProjectWarrantyForm({
                  projectId: "",
                  warrantyCoverageYear: "",
                  warrantyStartDate: "",
                  warrantyEndDate: ""
                });
              }}
            >
              <b>Cancel</b>
            </button>
          </div>
        </form>
      </div>
    );
  };

  // Function to render External Project Cost Management Form
  const renderExternalProjectCostForm = () => {
    return (
      <div className="project-form-container">
        <h2 className="form-title">External Project Cost Management</h2>
        <form onSubmit={handleExternalProjectCostSubmit} className="project-form">
          <div className="form-group">
            <label className="form-label">
              <b>Project ID*</b>
            </label>
            <select
              className="form-select"
              value={externalProjectCostForm.projectId}
              onChange={(e) => handleInputChange('externalProjectCost', 'projectId', e.target.value)}
              required
            >
              <option value="">Select Project ID</option>
              {projectIds.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">
              <b>BOM ID</b>
            </label>
            <select
              className="form-select"
              value={externalProjectCostForm.bomId}
              onChange={(e) => handleInputChange('externalProjectCost', 'bomId', e.target.value)}
            >
              <option value="">Select BOM ID</option>
              {bomIds.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">
              <b>Project Budget Approval</b>
            </label>
            <select
              className="form-select"
              value={externalProjectCostForm.projectBudgetApproval}
              onChange={(e) => handleInputChange('externalProjectCost', 'projectBudgetApproval', e.target.value)}
            >
              <option value="">Select Budget Approval ID</option>
              {budgetApprovalIds.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>

          <div className="form-actions">
            <button type="submit" className="form-button save-button">
              <b>Save</b>
            </button>
            <button 
              type="button" 
              className="form-button cancel-button"
              onClick={() => {
                setActiveView("dashboard");
                setExternalProjectCostForm({
                  projectId: "",
                  bomId: "",
                  projectBudgetApproval: ""
                });
              }}
            >
              <b>Cancel</b>
            </button>
          </div>
        </form>
      </div>
    );
  };

  // Function to render Internal Project Request Form
  const renderInternalProjectRequestForm = () => {
    return (
      <div className="project-form-container">
        <h2 className="form-title">Internal Project Request</h2>
        <form onSubmit={handleInternalProjectRequestSubmit} className="project-form">
          <div className="form-group">
            <label className="form-label">
              <b>Project Name*</b>
            </label>
            <input
              className="form-input"
              type="text"
              placeholder="Name"
              value={internalProjectRequestForm.projectName}
              onChange={(e) => handleInputChange('internalProjectRequest', 'projectName', e.target.value)}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">
                <b>Request Date*</b>
              </label>
              <input
                className="form-input"
                type="date"
                value={internalProjectRequestForm.requestDate}
                onChange={(e) => handleInputChange('internalProjectRequest', 'requestDate', e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                <b>Starting Date*</b>
              </label>
              <input
                className="form-input"
                type="date"
                value={internalProjectRequestForm.startingDate}
                onChange={(e) => handleInputChange('internalProjectRequest', 'startingDate', e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">
                <b>Employee ID</b>
              </label>
              <select
                className="form-select"
                value={internalProjectRequestForm.employeeId}
                onChange={(e) => handleInputChange('internalProjectRequest', 'employeeId', e.target.value)}
                required
              >
                <option value="">Select Employee ID</option>
                {employeeIds.map((id) => (
                  <option key={id} value={id}>{id}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">
                <b>Department ID</b>
              </label>
              <select
                className="form-select"
                value={internalProjectRequestForm.departmentId}
                onChange={(e) => handleInputChange('internalProjectRequest', 'departmentId', e.target.value)}
                required
              >
                <option value="">Select Department ID</option>
                {departmentIds.map((id) => (
                  <option key={id} value={id}>{id}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">
              <b>Budget Request</b>
            </label>
            <input
              className="form-input"
              type="number"
              placeholder="000.000.000"
              value={internalProjectRequestForm.budgetRequest}
              onChange={(e) => handleInputChange('internalProjectRequest', 'budgetRequest', e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <b>Budget Description</b>
            </label>
            <textarea
              className="form-textarea"
              placeholder="Budget Description"
              value={internalProjectRequestForm.budgetDescription}
              onChange={(e) => handleInputChange('internalProjectRequest', 'budgetDescription', e.target.value)}
              required
            />
          </div>

          <div className="form-actions">
            <button type="submit" className="form-button save-button">
              <b>Save</b>
            </button>
            <button 
              type="button" 
              className="form-button cancel-button"
              onClick={() => {
                setActiveView("dashboard");
                setInternalProjectRequestForm({
                  projectName: "",
                  requestDate: "",
                  startingDate: "",
                  employeeId: "",
                  departmentId: "",
                  budgetRequest: "",
                  budgetDescription: ""
                });
              }}
            >
              <b>Cancel</b>
            </button>
          </div>
        </form>
      </div>
    );
  };

  // Function to render Internal Project Details Form
  const renderInternalProjectDetailsForm = () => {
    return (
      <div className="project-form-container">
        <h2 className="form-title">Internal Project Details</h2>
        <form onSubmit={handleInternalProjectDetailsSubmit} className="project-form">
          <div className="form-group">
            <label className="form-label">
              <b>Project Request ID*</b>
            </label>
            <select
              className="form-select"
              value={internalProjectDetailsForm.projectRequestId}
              onChange={(e) => handleInputChange('internalProjectDetails', 'projectRequestId', e.target.value)}
              required
            >
              <option value="">Select Project Request ID</option>
              {internalProjectRequestIds.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">
              <b>Project Status</b>
            </label>
            <select
              className="form-select"
              value={internalProjectDetailsForm.projectStatus}
              onChange={(e) => handleInputChange('internalProjectDetails', 'projectStatus', e.target.value)}
              required
            >
              <option value="">Choose Project Status</option>
              {internalProjectStatusOptions.map((status) => (
                <option key={status} value={status}>{status.replace('_', ' ')}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">
              <b>Approval ID</b>
            </label>
            <select
              className="form-select"
              value={internalProjectDetailsForm.approvalId}
              onChange={(e) => handleInputChange('internalProjectDetails', 'approvalId', e.target.value)}
            >
              <option value="">Select Approval ID</option>
              {approvalIds.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">
              <b>Project Description</b>
            </label>
            <textarea
              className="form-textarea"
              placeholder="Project Description"
              value={internalProjectDetailsForm.projectDescription}
              onChange={(e) => handleInputChange('internalProjectDetails', 'projectDescription', e.target.value)}
            />
          </div>

          <div className="form-actions">
            <button type="submit" className="form-button save-button">
              <b>Save</b>
            </button>
            <button 
              type="button" 
              className="form-button cancel-button"
              onClick={() => {
                setActiveView("dashboard");
                setInternalProjectDetailsForm({
                  projectRequestId: "",
                  projectStatus: "",
                  approvalId: "",
                  projectDescription: ""
                });
              }}
            >
              <b>Cancel</b>
            </button>
          </div>
        </form>
      </div>
    );
  };

  // Function to render Internal Project Labor Form
  const renderInternalProjectLaborForm = () => {
    return (
      <div className="project-form-container">
        <h2 className="form-title">Internal Project Labor</h2>
        <form onSubmit={handleInternalProjectLaborSubmit} className="project-form">
          <div className="form-group">
            <label className="form-label">
              <b>Project ID*</b>
            </label>
            <select
              className="form-select"
              value={internalProjectLaborForm.projectId}
              onChange={(e) => handleInputChange('internalProjectLabor', 'projectId', e.target.value)}
              required
            >
              <option value="">Select Project ID</option>
              {internalProjectIds.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">
                <b>Job Role*</b>
              </label>
              <input
                className="form-input"
                type="text"
                placeholder="Job Role"
                value={internalProjectLaborForm.jobRole}
                onChange={(e) => handleInputChange('internalProjectLabor', 'jobRole', e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                <b>Employee ID*</b>
              </label>
              <select
                className="form-select"
                value={internalProjectLaborForm.employeeId}
                onChange={(e) => handleInputChange('internalProjectLabor', 'employeeId', e.target.value)}
                required
              >
                <option value="">Select Employee ID</option>
                {employeeIds.map((id) => (
                  <option key={id} value={id}>{id}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="form-button save-button">
              <b>Save</b>
            </button>
            <button 
              type="button" 
              className="form-button cancel-button"
              onClick={() => {
                setActiveView("dashboard");
                setInternalProjectLaborForm({
                  projectId: "",
                  jobRole: "",
                  employeeId: ""
                });
              }}
            >
              <b>Cancel</b>
            </button>
          </div>
        </form>
      </div>
    );
  };

  // Main render function
  return (
    <div className="project-planning-container">
      <div className="project-planning-header">
        <h1 className="project-planning-title">Project Planning</h1>
        <div className="project-planning-actions">
          <button className="gantt-chart-button">
            <b>Gantt Chart</b>
          </button>
          {activeView === "dashboard" ? (
            <button className="create-plan-button">
              <b>Create Plan</b>
            </button>
          ) : (
            <button 
              className="back-to-dashboard-button"
              onClick={() => setActiveView("dashboard")}
            >
              <b>Back to Dashboard</b>
            </button>
          )}
        </div>
      </div>

      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      {activeView === "dashboard" && renderDashboard()}
      {activeView === "externalProjectRequest" && renderExternalProjectRequestForm()}
      {activeView === "externalProjectDetails" && renderExternalProjectDetailsForm()}
      {activeView === "externalProjectLabor" && renderExternalProjectLaborForm()}
      {activeView === "externalProjectEquipment" && renderExternalProjectEquipmentForm()}
      {activeView === "externalProjectWarranty" && renderExternalProjectWarrantyForm()}
      {activeView === "externalProjectCost" && renderExternalProjectCostForm()}
      {activeView === "internalProjectRequest" && renderInternalProjectRequestForm()}
      {activeView === "internalProjectDetails" && renderInternalProjectDetailsForm()}
      {activeView === "internalProjectLabor" && renderInternalProjectLaborForm()}
    </div>
  );
};

export default ProjectPlanningDashboard;