import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/Projectcost.css";

const BodyContent = () => {
  
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectID, setNewProjectID] = useState("");
  const [newBillofMaterials, setNewBillofMaterials] = useState("");
  const [newInternalprojectID, setNewInternalProjectid] = useState("");
  const [selectedApprovalID, setSelectedApprovalID] = useState("");
  const [newLaborCost, setNewLaborCost] = useState("");
  const [newOutsourcedCost, setNewOutsourcedCost] = useState("");
  const [newUtilityCost, setNewUtilityCost] = useState("");
  const [newOverallProjectCost, setNewOverallProjectCost] = useState("");
  
  
  const [showProjectCosting, setShowProjectCosting] = useState(false);
  const [currentForm, setCurrentForm] = useState(1);
  const [reportData, setReportData] = useState([]);
  const [selectedReports, setSelectedReports] = useState([]);
  const [loading, setLoading]= useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  
  // Determine if Internal Project ID field should be disabled
  const isInternalProjectIDDisabled = newProjectID && newProjectID.trim() !== "";
  
  // Determine if Project ID field should be disabled
  const isProjectIDDisabled = newInternalprojectID && newInternalprojectID.trim() !== "";
  
  // Determine if cost breakdown fields should be disabled
  // Now cost breakdown fields will be disabled if Project ID has a value
  const areCostBreakdownFieldsDisabled = newProjectID && newProjectID.trim() !== "";
  
  // Determine if other fields should be disabled (only if neither ID is provided)
  const areOtherFieldsDisabled = (!newProjectID || newProjectID.trim() === "") && 
                               (!newInternalprojectID || newInternalprojectID.trim() === "");
  
  const resetForm = () => {
    setNewProjectName("");
    setNewProjectID("");
    setNewBillofMaterials("");
    setNewInternalProjectid("");
    setSelectedApprovalID("");
    setNewLaborCost("");
    setNewOutsourcedCost("");
    setNewUtilityCost("");
    setNewOverallProjectCost("");
  };

  
  const handleBackClick = () => {
    setShowProjectCosting(false);
    setCurrentForm(1);
    setSelectedProject(null);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitLoading(true);
    
    // Create a new project cost entry
    const newEntry = {
      newProjectName: newProjectName || "Project " + (reportData.length + 1), // Default name if not provided
      newProjectID,
      newBillofMaterials,
      newInternalprojectID,
      newApprovalID: selectedApprovalID,
      newLaborCost,
      newOutsourcedCost,
      newUtilityCost,
      newOverallProjectCost
    };
    
    // Add to report data
    setReportData([...reportData, newEntry]);
    
    // Reset form and show the table
    resetForm();
    setSubmitLoading(false);
    
    // Only show the table after saving
    setShowProjectCosting(true);
  };
  
  const handleCheckboxChange = (index) => {
    if (selectedReports.includes(index)) {
      setSelectedReports(selectedReports.filter((i) => i !== index));
    } else {
      setSelectedReports([...selectedReports, index]);
    }
  };

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      const allIndexes = reportData.map((_, index) => index);
      setSelectedReports(allIndexes);
    } else {
      setSelectedReports([]);
    }
  };

  const handleRowClick = (project) => {
    setSelectedProject(project);
  };

  const handleBackToList = () => {
    setSelectedProject(null);
  };

  return (
    <div className="body-content-container">
      {!showProjectCosting && currentForm === 1 && (
        <form onSubmit={handleSubmit} className="project-request-form">
          <div className="form-header">
            <h1 className="form-title">
              <b>Project Cost</b>
            </h1>
          </div>

          <h2 className="section-title">Project Details</h2>
          <div className="form-grid">
            {/* Project ID*/}
            <div className="form-group">
              <label className="form-label">
                <b>Project ID</b>
              </label>
              <input
                className="form-input"
                type="text"
                placeholder="Enter Project ID"
                value={newProjectID}
                onChange={(e) => setNewProjectID(e.target.value)}
                disabled={isProjectIDDisabled}
              />
            </div>

            {/* Internal Project ID */}
            <div className="form-group">
              <label className="form-label">
                <b>Internal Project ID</b>
              </label>
              <input
                className="form-input"
                type="text"
                placeholder="Enter Internal Project ID"
                value={newInternalprojectID}
                onChange={(e) => setNewInternalProjectid(e.target.value)}
                disabled={isInternalProjectIDDisabled}
              />
            </div>

            {/* Project Name */}
            <div className="form-group">
              <label className="form-label">
                <b>Project Name</b>
              </label>
              <input
                className="form-input"
                type="text"
                placeholder="Enter Project Name"
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.target.value)}
              />
            </div>

            {/* Bill of Materials */}
            <div className="form-group">
              <label className="form-label">
                <b>Bill of Materials</b>
              </label>
              <input
                className="form-input"
                type="text"
                placeholder="Enter BOM ID"
                value={newBillofMaterials}
                onChange={(e) => setNewBillofMaterials(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label"><b>Approval ID</b></label>
              <select
                name="ApprovalID"
                className="form-input"
                value={selectedApprovalID}
                onChange={(e) => setSelectedApprovalID(e.target.value)}
                required
              >
                <option value="">Insert Approval ID</option>
                <option value="approved">Approve</option>
                <option value="rejected">Reject</option>
                <option value="pending">Pending</option>
              </select>
            </div>
          </div>

          <h2 className="section-title">Cost Breakdown</h2>
          <div className="form-grid">
            {/* Labor Cost */}
            <div className="form-group">
              <label className="form-label">
                <b>Labor Cost</b>
              </label>
              <div className="input-with-icon">
                <span className="currency-symbol">₱</span>
                <input
                  className="form-input with-currency"
                  type="text"
                  placeholder="123,456.78"
                  value={newLaborCost}
                  onChange={(e) => setNewLaborCost(e.target.value)}
                  required
                  disabled={areCostBreakdownFieldsDisabled}
                />
              </div>
            </div>

            {/* Utility cost */}
            <div className="form-group">
              <label className="form-label">
                <b>Utility Cost</b>
              </label>
              <div className="input-with-icon">
                <span className="currency-symbol">₱</span>
                <input
                  className="form-input with-currency"
                  type="text"
                  placeholder="123,456.78"
                  value={newUtilityCost}
                  onChange={(e) => setNewUtilityCost(e.target.value)}
                  required
                  disabled={areCostBreakdownFieldsDisabled}
                />
              </div>
            </div>

            {/* Outsourced cost */}
            <div className="form-group">
              <label className="form-label">
                <b>Outsourced Cost</b>
              </label>
              <div className="input-with-icon">
                <span className="currency-symbol">₱</span>
                <input
                  className="form-input with-currency"
                  type="text"
                  placeholder="123,456.78"
                  value={newOutsourcedCost}
                  onChange={(e) => setNewOutsourcedCost(e.target.value)}
                  required
                  disabled={areCostBreakdownFieldsDisabled}
                />
              </div>
            </div>

            {/* Overall Project Cost */}
            <div className="form-group">
              <label className="form-label">
                <b>Overall Project Cost</b>
              </label>
              <div className="input-with-icon">
                <span className="currency-symbol">₱</span>
                <input
                  className="form-input with-currency"
                  type="text"
                  placeholder="123,456.78"
                  value={newOverallProjectCost}
                  onChange={(e) => setNewOverallProjectCost(e.target.value)}
                  required
                  disabled={areCostBreakdownFieldsDisabled}
                />
              </div>
            </div>
          </div>

          <div className="form-footer">
            <div className="button-group">
              <button type="button" className="btn btn-secondary" onClick={resetForm}>
                <b>Cancel</b>
              </button>
              <button 
                type="submit" 
                className="btn btn-primary" 
                disabled={submitLoading || (areOtherFieldsDisabled && !areCostBreakdownFieldsDisabled)}
              >
                <b>{submitLoading ? "Saving..." : "Save"}</b>
              </button>
            </div>
          </div>
        </form>
      )}

      {showProjectCosting && !selectedProject && (
        <div className="report-list-container">
          <div className="list-header">
            <h1 className="list-title">
              <b>Project Costing</b>
            </h1>
            <div className="list-controls">
              <button onClick={handleBackClick} className="btn btn-secondary">
                <b>Back</b>
              </button>
            </div>
          </div>

          <div className="table-responsive">
            {loading ? (
              <div className="loading-state">
                <div className="loader"></div>
                <p>Loading project requests...</p>
              </div>
            ) : reportData.length === 0 ? (
              <div className="empty-state">
                <p>No project requests found. Click "Add Request" to create one.</p>
              </div>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th><b>Project Name</b></th>
                    <th><b>Project ID</b></th>
                    <th><b>BOM ID</b></th>
                    <th><b>Total Cost</b></th>
                    <th><b>Approval Status</b></th>
                  </tr>
                </thead>
                <tbody>
                  {reportData.map((item, index) => (
                    <tr 
                      key={index} 
                      className={selectedReports.includes(index) ? "selected" : ""}
                      onClick={() => handleRowClick(item)}
                      style={{ cursor: 'pointer' }}
                    >
                      <td><b>{item.newProjectName}</b></td>
                      <td><b>{item.newProjectID || item.newInternalprojectID}</b></td>
                      <td><b>{item.newBillofMaterials}</b></td>
                      <td><b>₱{item.newOverallProjectCost}</b></td>
                      <td><span className="status-badge">{item.newApprovalID}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {showProjectCosting && selectedProject && (
        <div className="project-detail-container">
          <div className="detail-header">
            <h1 className="detail-title">
              <b>Project Details: {selectedProject.newProjectName}</b>
            </h1>
            <div className="detail-controls">
              <button onClick={handleBackToList} className="btn btn-secondary">
                <b>Back to List</b>
              </button>
            </div>
          </div>
          
          {/* Project details content would go here */}
          <div className="project-details-content">
            <div className="details-grid">
              <div className="detail-item">
                <h3 className="detail-label">Project ID</h3>
                <p className="detail-value">{selectedProject.newProjectID || selectedProject.newInternalprojectID}</p>
              </div>
              <div className="detail-item">
                <h3 className="detail-label">Bill of Materials</h3>
                <p className="detail-value">{selectedProject.newBillofMaterials}</p>
              </div>
              <div className="detail-item">
                <h3 className="detail-label">Approval Status</h3>
                <p className="detail-value">
                  <span className="status-badge">{selectedProject.newApprovalID}</span>
                </p>
              </div>
              
              <div className="detail-item">
                <h3 className="detail-label">Labor Cost</h3>
                <p className="detail-value">₱{selectedProject.newLaborCost}</p>
              </div>
              <div className="detail-item">
                <h3 className="detail-label">Utility Cost</h3>
                <p className="detail-value">₱{selectedProject.newUtilityCost}</p>
              </div>
              <div className="detail-item">
                <h3 className="detail-label">Outsourced Cost</h3>
                <p className="detail-value">₱{selectedProject.newOutsourcedCost}</p>
              </div>
              <div className="detail-item">
                <h3 className="detail-label">Overall Project Cost</h3>
                <p className="detail-value">₱{selectedProject.newOverallProjectCost}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {!showProjectCosting && currentForm !== 1 && (
        <div className="view-list-container">
          <button onClick={() => setShowProjectCosting(true)} className="btn btn-primary">
            <b>View Project Costing</b>
          </button>
        </div>
      )}
    </div>
  );
};

export default BodyContent;