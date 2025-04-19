import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/ProjectPlanning.css";

const BodyContent = () => {
    
const [projectStatusOptions, setProjectStatusOptions] = useState([]);
const [internalProjectStatusOptions, setInternalProjectStatusOptions] = useState([]);

    
  const [newProjectname, setNewProjectname] = useState("");
  const [newProjectdescription, setNewProjectdescription] = useState("");
  const [newApprovalid, setNewApprovalid] = useState("");
  const [newOrderid, setNewOrderid] = useState("");
  const [newProjectrequestid, setNewProjectrequestid] = useState("");
  const [newProjectid, setNewProjectid] = useState("");
  const [newJobroleneeeded, setNewjobroleneeded] = useState("");
  const [newEmployeeid, setNewEmployeeid] = useState("");
  const [newProjectequipmentid, setNewProjectequipmentid] = useState("");
  const [newWarrantycoverageyear, setNewWarrantycoverageyear] = useState("");
  const [newWarrantystartdate, setNewWarrantystartdate] = useState("");
  const [newWarrantyenddate, setNewWarrantyenddate] = useState("");
  const [newBomID, setNewBomID] = useState("");
  const [newProjectbudgetapproval, setNewProjectbudgetapproval] = useState("");
  const [bomIds, setBomIds] = useState([]);
  const [budgetApprovalIds, setBudgetApprovalIds] = useState([]); 
    
  const [newProjectNameint, setNewProjectNameint] = useState("");
  const [newRequestDateint, setNewRequestDateint] = useState("");
  const [newStartingdateint, setNewStartingdateint] = useState("");
  const [newDepartmentIDint, setNewDepartmentIDint] = useState("");
  const [newEmployeeIDint, setNewEmployeeIDint] = useState("");
  const [newBudgetrequestint, setNewBudgetrequestint] = useState("");
  const [newBudgetdescriptionint, setNewBudgetdescriptionint] = useState("");
  const [newProjectrequestidint, setNewProjectrequestidint] = useState("");
  const [newApprovalidint, setNewApprovalidint] = useState("");
  const [newProjectdescriptionint, setNewProjectdescriptionint] = useState("");
  const [newProjectidint, setNewProjectidint] = useState("");
  const [newJobroleint, setNewJobroleint] = useState("");
  
    
  const [selectedProjectStatusint, setSelectedProjectStatusint] = useState("");
  const [selectedProjectStatus, setSelectedProjectStatus] = useState("");
  const [currentForm, setCurrentForm] = useState(1);
  const [selectedNavplan, setSelectedNavplan] = useState("External");
  
    
  const [approvalIds, setApprovalIds] = useState([]);
  const [orderIds, setOrderIds] = useState([]);
  const [projectRequestIds, setProjectRequestIds] = useState([]);
  const [projectIds, setProjectIds] = useState([]);
  const [employeeIds, setEmployeeIds] = useState([]);
  const [equipmentIds, setEquipmentIds] = useState([]);
  const [internalProjectRequestIds, setInternalProjectRequestIds] = useState([]);
  const [internalProjectIds, setInternalProjectIds] = useState([]);
  const [departmentIds, setDepartmentIds] = useState([]);
  
    
  const [message, setMessage] = useState({ text: "", type: "" });

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
        
          
        const bomIdsRes = await axios.get('/api/project-planning/get-bom-ids-from-cost-management/');
        console.log("BOM IDs response:", bomIdsRes.data);
        setBomIds(bomIdsRes.data);
        
        const budgetApprovalIdsRes = await axios.get('/api/project-planning/get-budget-approval-ids-from-cost-management/');
        console.log("Budget Approval IDs response:", budgetApprovalIdsRes.data);
        setBudgetApprovalIds(budgetApprovalIdsRes.data);
        
      } catch (error) {
        console.error("Error fetching dropdown data:", error);
        setMessage({ text: "Failed to load data. Please refresh the page.", type: "error" });
      }
    };
    
    fetchDropdownData();
  }, []);
  
  const handleNavClick = (nav) => {
    setSelectedNavplan(nav);
    console.log(`Nav clicked: ${nav}`);
    setCurrentForm(1);
    setMessage({ text: "", type: "" });
  };

  const handleFirstSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/project-planning/create-external-project-request/', {
        ProjectName: newProjectname,
        ProjectDescription: newProjectdescription,
        ApprovalID: newApprovalid,
        OrderID: newOrderid,
        ProjectStatus: "Pending"
      });
      
      console.log("New Project Data:", response.data);
      setMessage({ text: "Project created successfully!", type: "success" });
      setCurrentForm(2);
      
      const projectReqRes = await axios.get('/api/project-planning/get-external-project-request-ids/');
      setProjectRequestIds(projectReqRes.data);
    } catch (error) {
      console.error("Error creating project:", error);
      setMessage({ text: "Failed to create project. Please try again.", type: "error" });
    }
  };

  const handleSecondSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.put(`/api/project-planning/external-details/${newProjectrequestid}/`, {
        project_status: selectedProjectStatus
      });
      
      console.log("Project Request ID Data:", response.data);
      setMessage({ text: "Project status updated successfully!", type: "success" });
      setCurrentForm(3);
      
      const projectIdRes = await axios.get('/api/project-planning/get-external-project-ids/');
      setProjectIds(projectIdRes.data);
    } catch (error) {
      console.error("Error updating project status:", error);
      setMessage({ text: "Failed to update project status. Please try again.", type: "error" });
    }
  };

  const handleThirdSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/project-planning/add-external-project-labor/', {
        ProjectID: newProjectid,
        JobRoleNeeded: newJobroleneeeded,
        EmployeeID: newEmployeeid
      });
      
      console.log("Project Labor Data:", response.data);
      setMessage({ text: "Project labor added successfully!", type: "success" });
      setCurrentForm(4);
      setNewjobroleneeded("");
      setNewEmployeeid("");
    } catch (error) {
      console.error("Error adding project labor:", error);
      setMessage({ text: "Failed to add project labor. Please try again.", type: "error" });
    }
  };

  const handleFourthSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/project-planning/add-external-project-equipment/', {
        ProjectID: newProjectid,
        ProjectEquipmentID: newProjectequipmentid    
      });
      
      console.log("Project Equipment ID Data:", response.data);
      setMessage({ text: "Project equipment added successfully!", type: "success" });
      setCurrentForm(5);
    } catch (error) {
      console.error("Error adding project equipment:", error);
      setMessage({ text: "Failed to add project equipment. Please try again.", type: "error" });
    }
  };

const handleFifthSubmit = async (e) => {
  e.preventDefault();
    const startDate = new Date(newWarrantystartdate);
  const endDate = new Date(newWarrantyenddate);
  
  if (endDate <= startDate) {
    setMessage({ text: "Warranty end date must be after warranty start date", type: "error" });
    return;
  }
  
  try {
    const response = await axios.post('/api/project-planning/add-external-project-warranty/', {
      ProjectID: newProjectid,
      Warrantycoverageyear: newWarrantycoverageyear,
      Warrantystartdate: newWarrantystartdate,
      Warrantyenddate: newWarrantyenddate
    });
    
    console.log("Project Warranty Data:", response.data);
    setMessage({ text: "Project warranty added successfully!", type: "success" });
    setCurrentForm(6);
  } catch (error) {
    console.error("Error adding project warranty:", error);
    if (error.response && error.response.data && error.response.data.error) {
      setMessage({ text: `Failed to add project warranty: ${error.response.data.error}`, type: "error" });
    } else {
      setMessage({ text: "Failed to add project warranty. Please try again.", type: "error" });
    }
  }
};

const handleSixthSubmit = async (e) => {
  e.preventDefault();
  try {
    console.log("Submitting form with data:", {
      ProjectID: newProjectid,
      BomID: newBomID,
      ProjectBudgetApproval: newProjectbudgetapproval
    });
    
    const response = await axios.post('/api/project-planning/add-external-project-cost-management/', {
      ProjectID: newProjectid,
      BomID: newBomID,
      ProjectBudgetApproval: newProjectbudgetapproval
    });
    
    console.log("Project Cost Management Data:", response.data);
    setMessage({ text: "Project completed successfully!", type: "success" });
    setCurrentForm(1);
  } catch (error) {
    console.error("Error completing project:", error);
    if (error.response && error.response.data && error.response.data.error) {
      setMessage({ text: `Failed to complete project: ${error.response.data.error}`, type: "error" });
    } else {
      setMessage({ text: "Failed to complete project. Please try again.", type: "error" });
    }
  }
};


const handleFirstSubmitint = async (e) => {
  e.preventDefault();
  try {
    console.log("Submitting internal project data:", {
      ProjectNameint: newProjectNameint,
      RequestDateint: newRequestDateint,
      Startingdateint: newStartingdateint,
      EmployeeIDint: newEmployeeIDint,
      DepartmentIDint: newDepartmentIDint,
      Budgetrequestint: newBudgetrequestint,
      Budgetdescriptionint: newBudgetdescriptionint
    });
    
    const response = await axios.post('/api/project-planning/create-internal-project/', {
      ProjectNameint: newProjectNameint,
      RequestDateint: newRequestDateint,
      Startingdateint: newStartingdateint,
      EmployeeIDint: newEmployeeIDint,
      DepartmentIDint: newDepartmentIDint,
      Budgetrequestint: newBudgetrequestint,
      Budgetdescriptionint: newBudgetdescriptionint
    });
    
    console.log("Project Name int:", response.data);
    setMessage({ text: "Internal project created successfully!", type: "success" });
    setCurrentForm(8);
    
      
    const intProjectReqRes = await axios.get('/api/project-planning/get-internal-project-request-ids/');
    setInternalProjectRequestIds(intProjectReqRes.data);
  } catch (error) {
    console.error("Error creating internal project:", error);
    setMessage({ text: "Failed to create internal project. Please try again.", type: "error" });
  }
};

  const handleSecondSubmitint = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.put(`/api/project-planning/internal-details/${newProjectrequestidint}/`, {
        intrnl_project_status: selectedProjectStatusint,
        approval_id: newApprovalidint,
        project_description: newProjectdescriptionint
      });
      
      console.log("Project Request ID:", response.data);
      setMessage({ text: "Internal project details updated successfully!", type: "success" });
      setCurrentForm(9);
      
        
      const intProjectIdRes = await axios.get('/api/project-planning/get-internal-project-ids/');
      setInternalProjectIds(intProjectIdRes.data);
    } catch (error) {
      console.error("Error updating internal project details:", error);
      setMessage({ text: "Failed to update internal project details. Please try again.", type: "error" });
    }
  };

  const handleThirdSubmitint = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/project-planning/add-internal-project-labor/', {
        Projectidint: newProjectidint, 
        Jobroleint: newJobroleint,
        EmployeeIDint: newEmployeeIDint
      });
      
      console.log("Project ID", response.data);
      setMessage({ text: "Internal project labor added successfully!", type: "success" });
      setCurrentForm(1);
    } catch (error) {
      console.error("Error adding internal project labor:", error);
      setMessage({ text: "Failed to add internal project labor. Please try again.", type: "error" });
    }
  };

  return (
    <div className="body-content-container3">
      <div className="newprojplan"><b>New Project Plan</b></div>
      <button className="ganttchart">
        <b>Gantt Chart</b>
      </button>
      <button className="crplan">
        <b>Create Plan</b>
      </button>

      <div className="planningnav">
        <button
          className={`nav-button ${
            selectedNavplan === "Internal" ? "selected1" : ""
          }`}
          onClick={() => handleNavClick("Internal")}
        >
          <b>Internal</b>
        </button>

        <button
          className={`nav-button ${
            selectedNavplan === "External" ? "selected1" : ""
          }`}
          onClick={() => handleNavClick("External")}
        >
          <b>External</b>
        </button>
      </div>

      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="samplebody">
        {selectedNavplan === "External" && (
          <>
            {currentForm === 1 && (
              <form onSubmit={handleFirstSubmit}>
                <h2 id="projrequest">Project Request</h2>
                <label className="projectname1">
                  <b>Project Name*</b>
                </label>
                <br />
                <input
                  className="projectname"
                  type="text"
                  placeholder="Name"
                  value={newProjectname}
                  onChange={(e) => setNewProjectname(e.target.value)}
                  required
                />
                <br />

                <label className="projectdescription1">
                  <b>Project Description</b>
                </label>
                <br />
                <input
                  className="projectdescription"
                  type="text"
                  placeholder="Add Description"
                  value={newProjectdescription}
                  onChange={(e) => setNewProjectdescription(e.target.value)}
                  required
                />
                <br />

                <label className="Approvalid1">
                  <b>Approval ID</b>
                </label>
                <br />
                <select
                  className="Approvalid"
                  value={newApprovalid}
                  onChange={(e) => setNewApprovalid(e.target.value)}
                  required
                >
                  <option value="">Select Approval ID</option>
                  {approvalIds.map((id) => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
                <br />

                <label className="Orderid1">
                  <b>Order ID*</b>
                </label>
                <br />
                <select
                  className="Orderid"
                  value={newOrderid}
                  onChange={(e) => setNewOrderid(e.target.value)}
                  required
                >
                  <option value="">Select Order ID</option>
                  {orderIds.map((id) => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
                <br />
                <button type="submit" className="next">
                  <b>Next</b>
                </button>
                <button type="button" className="edit" onClick={() => setCurrentForm(1)}>
                  <b>Edit</b>
                </button>
              </form>
            )}

            {currentForm === 2 && (
              <form onSubmit={handleSecondSubmit}>
                <h2 id="projrequest">Project Details</h2>
                <label className="projectrequestid1">
                  <b>Project Request ID*</b>
                </label>
                <br />
                <select
                  className="projectrequestid"
                  value={newProjectrequestid}
                  onChange={(e) => setNewProjectrequestid(e.target.value)}
                  required
                >
                  <option value="">Select Project Request ID</option>
                  {projectRequestIds.map((id) => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
                <br />

                <label className="projectstatus1"><b>Project Status</b></label>
                <br />
                  <select
                    name="projectstatus"
                    className="projectstatus"
                    value={selectedProjectStatus}
                    onChange={(e) => setSelectedProjectStatus(e.target.value)}
                    required
                  >
                    <option value="">Choose Project Status</option>
                    {projectStatusOptions.map((status) => (
                      <option key={status} value={status}>{status.replace('_', ' ')}</option>
                    ))}
                  </select>

                <br />
                <button type="submit" className="next">
                  <b>Next</b>
                </button>
                <button type="button" className="edit" onClick={() => setCurrentForm(1)}>
                  <b>Edit</b>
                </button>
              </form>
            )}

            {currentForm === 3 && (
              <form onSubmit={handleThirdSubmit}>
                <h2 id="projrequest">Project Labor</h2>
                <label className="projectid1">
                  <b>Project ID*</b>
                </label>
                <br />
                <select
                  className="projectid"
                  value={newProjectid}
                  onChange={(e) => setNewProjectid(e.target.value)}
                  required
                >
                  <option value="">Select Project ID</option>
                  {projectIds.map((id) => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
                <br />

                <label className="jobrole1">
                  <b>Job Role Needed*</b>
                </label>
                <br />
                <input
                  className="jobrole"
                  type="text"
                  placeholder=""
                  value={newJobroleneeeded}
                  onChange={(e) => setNewjobroleneeded(e.target.value)}
                  required
                />
                <h1 className="jobroleneeded"><b>Job Role:</b></h1>
                <br />

                <label className="employeeid1">
                  <b>Employee ID*</b>
                </label>
                <br />
                <select
                  className="employeeid"
                  value={newEmployeeid}
                  onChange={(e) => setNewEmployeeid(e.target.value)}
                  required
                >
                  <option value="">Select Employee ID</option>
                  {employeeIds.map((id) => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
                <br />
                <button type="submit" className="next">
                  <b>Next</b>
                </button>
                <button type="button" className="edit" onClick={() => setCurrentForm(2)}>
                  <b>Edit</b>
                </button>
              </form>
            )}

            {currentForm === 4 && (
              <form onSubmit={handleFourthSubmit}>
                <h2 id="projrequest">Project Equipments</h2>
                <label className="projectid1">
                  <b>Project ID*</b>
                </label>
                <br />
                <select
                  className="projectid"
                  value={newProjectid}
                  onChange={(e) => setNewProjectid(e.target.value)}
                  required
                >
                  <option value="">Select Project ID</option>
                  {projectIds.map((id) => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
                <br />
                <label className="projectequipid1">
                  <b>Project Equipment ID*</b>
                </label>
                <br />
                <select
                  className="projectequipid"
                  value={newProjectequipmentid}
                  onChange={(e) => setNewProjectequipmentid(e.target.value)}
                  required
                >
                  <option value="">Select Equipment ID</option>
                  {equipmentIds.map((id) => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
                <h1 className="eqpid">
                  <b>EQP ID:</b>
                </h1>
                <br />
                <button type="submit" className="next">
                  <b>Next</b>
                </button>
                <button type="button" className="edit" onClick={() => setCurrentForm(3)}>
                  <b>Edit</b>
                </button>
              </form>
            )}

            {currentForm === 5 && (
              <form onSubmit={handleFifthSubmit}>
                <h2 id="projrequest">Project Warranty</h2>
                <label className="projectid1">
                  <b>Project ID*</b>
                </label>
                <br />
                <select
                  className="projectid"
                  value={newProjectid}
                  onChange={(e) => setNewProjectid(e.target.value)}
                  required
                >
                  <option value="">Select Project ID</option>
                  {projectIds.map((id) => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
                <br />

                <label className="projectwarranty1">
                  <b>Warranty Coverage Year*</b>
                </label>
                <br />
                <input
                  className="projectwarranty"
                  type="number"
                  placeholder="Insert Year"
                  value={newWarrantycoverageyear}
                  onChange={(e) => setNewWarrantycoverageyear(e.target.value)}
                  required
                />
                <br />

                <label className="warrantystart1">
                  <b>Warranty Start Date</b>
                </label>
                <br />
                <input
                  className="warrantystart"
                  type="date"
                  placeholder="Insert Date"
                  value={newWarrantystartdate}
                  onChange={(e) => setNewWarrantystartdate(e.target.value)}
                  required
                />
                <br />

                <label className="warrantyend1">
                  <b>Warranty End Date</b>
                </label>
                <br />
                <input
                  className="warrantyend"
                  type="date"
                  placeholder="Insert Date"
                  value={newWarrantyenddate}
                  onChange={(e) => setNewWarrantyenddate(e.target.value)}
                  required
                />
                <br />
                <button type="submit" className="next">
                  <b>Next</b>
                </button>
                <button type="button" className="edit" onClick={() => setCurrentForm(4)}>
                  <b>Edit</b>
                </button>
              </form>
            )}

{currentForm === 6 && (
  <form onSubmit={handleSixthSubmit}>
    <h2 id="projrequest">Project Cost Management</h2>
    <label className="projectid1">
      <b>Project ID*</b>
    </label>
    <br />
    <select
      className="projectid"
      value={newProjectid}
      onChange={(e) => setNewProjectid(e.target.value)}
      required
    >
      <option value="">Select Project ID</option>
      {projectIds.map((id) => (
        <option key={id} value={id}>{id}</option>
      ))}
    </select>
    <br />

    <label className="Bomid1">
      <b>BOM ID</b>
    </label>
    <br />
    <select
      className="Bomid"
      value={newBomID}
      onChange={(e) => setNewBomID(e.target.value)}
      required
    >
      <option value="">Select BOM ID</option>
      {bomIds.map((id) => (
        <option key={id} value={id}>{id}</option>
      ))}
    </select>
    <br />

    <label className="projectbudget1">
      <b>Project Budget Approval</b>
    </label>
    <br />
    <select
      className="projectbudget"
      value={newProjectbudgetapproval}
      onChange={(e) => setNewProjectbudgetapproval(e.target.value)}
      required
    >
      <option value="">Select Budget Approval</option>
      {budgetApprovalIds.map((id) => (
        <option key={id} value={id}>{id}</option>
      ))}
    </select>
    <br />
    <button type="submit" className="next">
      <b>Save</b>
    </button>
    <button type="button" className="edit" onClick={() => setCurrentForm(5)}>
      <b>Edit</b>
    </button>
  </form>
)}
          </>
        )}

        {selectedNavplan === "Internal" && (
          <>
            {currentForm === 1 && (
              <form onSubmit={handleFirstSubmitint}>
                <h2 id="projrequest">Project Request</h2>
                <label className="projectname1">
                  <b>Project Name*</b>
                </label>
                <br />
                <input
                  className="projectname"
                  type="text"
                  placeholder="Name"
                  value={newProjectNameint}
                  onChange={(e) => setNewProjectNameint(e.target.value)}
                  required
                />
                <br />

                <label className="Requesdate2">
                  <b>Request Date</b>
                </label>
                <br />
                <input
                  className="requestdateint"
                  type="date"
                  placeholder="00/00/0000"
                  value={newRequestDateint}
                  onChange={(e) => setNewRequestDateint(e.target.value)}
                  required
                />
                <br />

                <label className="startingdate2">
                  <b>Starting Date</b>
                </label>
                <br />
                <input
                  className="startingdateint"
                  type="date"
                  placeholder="00/00/0000"
                  value={newStartingdateint}
                  onChange={(e) => setNewStartingdateint(e.target.value)}
                  required
                />
                <br />

                <label className="employeeid2">
                  <b>Employee ID</b>
                </label>
                <br />
                <select
                  className="employeeidint"
                  value={newEmployeeIDint}
                  onChange={(e) => setNewEmployeeIDint(e.target.value)}
                  required
                >
                  <option value="">Select Employee ID</option>
                  {employeeIds.map((id) => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
                <br />

                <label className="departmentid2">
                  <b>Department ID</b>
                </label>
                <br />
                <select
                  className="departmentidint"
                  value={newDepartmentIDint}
                  onChange={(e) => setNewDepartmentIDint(e.target.value)}
                  required
                >
                  <option value="">Select Department ID</option>
                  {departmentIds.map((id) => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
                <br />

                <label className="budgetrequest2">
                  <b>Budget Request</b>
                </label>
                <br />
                <input
                  className="budgetrequestint"
                  type="number"
                  placeholder="000.000.000"
                  value={newBudgetrequestint}
                  onChange={(e) => setNewBudgetrequestint(e.target.value)}
                  required
                />
                <br />

                <input
                  className="budgetdescriptionint"
                  type="text"
                  placeholder="Budget Description"
                  value={newBudgetdescriptionint}
                  onChange={(e) => setNewBudgetdescriptionint(e.target.value)}
                  required
                />
                <br />
                <button type="submit" className="next">
                  <b>Next</b>
                </button>
                <button type="button" className="edit" onClick={() => setCurrentForm(1)}>
                  <b>Edit</b>
                </button>
              </form>
            )}

            {currentForm === 8 && (
              <form onSubmit={handleSecondSubmitint}>
                <h2 id="projrequest">Project Details</h2>
                <div>
                  <label className="projectrequestid1">
                    <b>Project Request ID*</b>
                  </label>
                  <br />
                  <select
                    className="projectrequestid"
                    value={newProjectrequestidint}
                    onChange={(e) => setNewProjectrequestidint(e.target.value)}
                    required
                  >
                    <option value="">Select Project Request ID</option>
                    {internalProjectRequestIds.map((id) => (
                      <option key={id} value={id}>{id}</option>
                    ))}
                  </select>
                  <br />

                  <label className="projectstatus2"><b>Project Status</b></label>
                  <br />
                  <select
                    name="projectstatus"
                    className="projectstatusint"
                    value={selectedProjectStatusint}
                    onChange={(e) => setSelectedProjectStatusint(e.target.value)}
                    required
                  >
                    <option value="">Choose Project Status</option>
                    {internalProjectStatusOptions.map((status) => (
                      <option key={status} value={status}>{status.replace('_', ' ')}</option>
                    ))}
                  </select>
                  <br />

                  <label className="Approvalid2">
                    <b>Approval ID</b>
                  </label>
                  <br />
                  <select
                    className="Approvalidint"
                    value={newApprovalidint}
                    onChange={(e) => setNewApprovalidint(e.target.value)}
                    required
                  >
                    <option value="">Select Approval ID</option>
                    {approvalIds.map((id) => (
                      <option key={id} value={id}>{id}</option>
                    ))}
                  </select>
                  <br />

                  <input
                    className="projectdescint"
                    type="text"
                    placeholder="Project Description"
                    value={newProjectdescriptionint}
                    onChange={(e) => setNewProjectdescriptionint(e.target.value)}
                    required
                  />
                  <h1 className="projectdesc2"><b>Project Description:</b></h1>
                  <br />

                  <button type="submit" className="next">
                    <b>Save</b>
                  </button>
                  <button type="button" className="edit" onClick={() => setCurrentForm(1)}>
                    <b>Edit</b>
                  </button>
                </div>
              </form>
            )}

            {currentForm === 9 && (
              <form onSubmit={handleThirdSubmitint}>
                <h2 id="projrequest">Project Labor</h2>
                <div>
                  <label className="projectrequestid1">
                    <b>Project ID*</b>
                  </label>
                  <br />
                  <select
                    className="projectrequestid"
                    value={newProjectidint}
                    onChange={(e) => setNewProjectidint(e.target.value)}
                    required
                  >
                    <option value="">Select Project ID</option>
                    {internalProjectIds.map((id) => (
                      <option key={id} value={id}>{id}</option>
                    ))}
                  </select>
                  <br />

                  <label className="jobrole2">
                    <b>Job Role Needed</b>
                  </label>
                  <br />
                  <input
                    className="jobroleint"
                    type="text"
                    placeholder="Job Role: "
                    value={newJobroleint}
                    onChange={(e) => setNewJobroleint(e.target.value)}
                    required
                  />
                  <br />
                  
                  <button type="submit" className="next">
                    <b>Save</b>
                  </button>
                  <button type="button" className="edit" onClick={() => setCurrentForm(8)}>
                    <b>Edit</b>
                  </button>
                </div>
              </form>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default BodyContent;
                