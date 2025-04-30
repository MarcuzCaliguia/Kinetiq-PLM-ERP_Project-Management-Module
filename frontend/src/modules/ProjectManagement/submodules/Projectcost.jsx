import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/Projectcost.css";

const BodyContent = () => {
  
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectID, setNewProjectID] = useState("");
  const [newBillofMaterials, setNewBillofMaterials] = useState("");
  const [newInternalprojectID, setNewInternalProjectid] = useState("");
  const [newApprovalID, setNewApprovalID] = useState("");
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
  
  // Determine if Internal Project ID field should be disabled
  const isInternalProjectIDDisabled = newProjectID && newProjectID.trim() !== "";
  
  // Determine if Project ID field should be disabled
  const isProjectIDDisabled = newInternalprojectID && newInternalprojectID.trim() !== "";
  
  // Determine if other fields should be disabled (only if neither ID is provided)
  const areOtherFieldsDisabled = (!newProjectID || newProjectID.trim() === "") && 
                               (!newInternalprojectID || newInternalprojectID.trim() === "");
  
  const resetForm = () => {
    setNewProjectName("");
    setNewProjectID("");
    setNewBillofMaterials("");
    setNewInternalProjectid("");
    setNewApprovalID("");
    setNewLaborCost("");
    setNewOutsourcedCost("");
    setNewUtilityCost("");
    setNewOverallProjectCost("");
  };

  
  const handleBackClick = () => {
    setShowProjectCosting(false);
    setCurrentForm(1);
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
      newApprovalID,
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

            {/* Approval ID */}
            <div className="form-group">
              <label className="form-label">
                <b>Approval ID</b>
              </label>
              <div className="autocomplete-container">
                <input
                  className="form-input"
                  type="text"
                  placeholder="Enter Approval ID"
                  value={newApprovalID}
                  onChange={(e) => setNewApprovalID(e.target.value)}
                  required
                />
              </div>
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
                  disabled={areOtherFieldsDisabled}
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
                  disabled={areOtherFieldsDisabled}
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
                  disabled={areOtherFieldsDisabled}
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
                  disabled={areOtherFieldsDisabled}
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
                disabled={submitLoading || (areOtherFieldsDisabled)}
              >
                <b>{submitLoading ? "Saving..." : "Save"}</b>
              </button>
            </div>
          </div>
        </form>
      )}

      {showProjectCosting && (
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
                    <th className="checkbox-column">
                    </th>
                    <th><b>Project Name</b></th>
                    <th><b>Project ID</b></th>
                    <th><b>BOM ID</b></th>
                    <th><b>Total Cost</b></th>
                    <th><b>Approval Status</b></th>
                  </tr>
                </thead>
                <tbody>
                  {reportData.map((item, index) => (
                    <tr key={index} className={selectedReports.includes(index) ? "selected" : ""}>
                      <td className="checkbox-column">
                      </td>
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