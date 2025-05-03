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
  const [searchTerm, setSearchTerm] = useState("");
  
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

  const getStatusClass = (status) => {
    switch(status?.toLowerCase()) {
      case 'approved':
        return 'approved';
      case 'rejected':
        return 'rejected';
      case 'pending':
      default:
        return 'pending';
    }
  };

  const filteredReportData = reportData.filter(item => 
    item.newProjectName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (item.newProjectID && item.newProjectID.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (item.newInternalprojectID && item.newInternalprojectID.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="body-content-container">
      {!showProjectCosting && currentForm === 1 && (
        <form onSubmit={handleSubmit} className="project-request-form">
          <div className="form-header">
            <h1 className="form-title">
              <span className="title-icon"><i className="fas fa-calculator"></i></span>
              <b>Project Cost Management</b>
            </h1>
          </div>

          <div className="form-card">
            <div className="card-header">
              <h2 className="section-title">
                <i className="fas fa-info-circle section-icon"></i>
                Project Details
              </h2>
            </div>
            <div className="card-body">
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
                  <label className="form-label"><b>Approval Status</b></label>
                  <select
                    name="ApprovalID"
                    className="form-input select-input"
                    value={selectedApprovalID}
                    onChange={(e) => setSelectedApprovalID(e.target.value)}
                    required
                  >
                    <option value="">Select Approval Status</option>
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                    <option value="pending">Pending</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div className="form-card">
            <div className="card-header">
              <h2 className="section-title">
                <i className="fas fa-money-bill-wave section-icon"></i>
                Cost Breakdown
              </h2>
            </div>
            <div className="card-body">
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
            </div>
          </div>

          <div className="form-footer">
            <div className="button-group">
              <button type="button" className="btn" onClick={resetForm}>
                <i className="fas fa-times btn-icon"></i>
                <b>Cancel</b>
              </button>
              <button 
                type="submit" 
                className="btn btn-primary" 
                disabled={submitLoading || (areOtherFieldsDisabled && !areCostBreakdownFieldsDisabled)}
              >
                <i className="fas fa-save btn-icon"></i>
                <b>{submitLoading ? "Saving..." : "Save"}</b>
              </button>
            </div>
          </div>
        </form>
      )}

      {showProjectCosting && !selectedProject && (
        <div className="report-list-container">
          <div className="list-header">
            <div className="list-title-section">
              <h1 className="list-title">
                <i className="fas fa-project-diagram mr-2"></i>
                <b>Project Costing</b>
              </h1>
              <p className="list-subtitle">View and manage all project costs</p>
            </div>
            <div className="list-controls">
              <button onClick={handleBackClick} className="btn btn-secondary">
                <i className="fas fa-plus btn-icon"></i>
                <b>Add New Project</b>
              </button>
            </div>
          </div>

          <div className="table-responsive custom-shadow">
            <div className="table-header">
              <div className="table-title">Project Cost List</div>
              <div className="table-actions">
                <div className="search-container">
                  <i className="fas fa-search search-icon"></i>
                  <input 
                    type="text" 
                    className="search-input" 
                    placeholder="Search projects..." 
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <button className="btn btn-outline">
                  <i className="fas fa-filter"></i> Filter
                </button>
              </div>
            </div>

            {loading ? (
              <div className="loading-state">
                <div className="loader"></div>
                <p>Loading project costs...</p>
              </div>
            ) : filteredReportData.length === 0 ? (
              <div className="empty-state">
                <i className="fas fa-folder-open empty-icon"></i>
                <p>No project costs found. Click "Add New Project" to create one.</p>
              </div>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th><b>Project Name</b></th>
                    <th><b>Project ID</b></th>
                    <th><b>BOM ID</b></th>
                    <th><b>Total Cost</b></th>
                    <th><b>Status</b></th>
                    <th><b>Actions</b></th>
                  </tr>
                </thead>
                <tbody>
                  {filteredReportData.map((item, index) => (
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
                      <td>
                        <span className={`status-badge ${getStatusClass(item.newApprovalID)}`}>
                          {item.newApprovalID}
                        </span>
                      </td>
                      <td className="action-column">
                        <button className="action-btn" onClick={(e) => {
                          e.stopPropagation();
                          handleRowClick(item);
                        }}>
                          <i className="fas fa-eye"></i>
                        </button>
                        <button className="action-btn" onClick={(e) => {
                          e.stopPropagation();
                          // Add edit functionality
                        }}>
                          <i className="fas fa-edit"></i>
                        </button>
                      </td>
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
            <div className="detail-title-section">
              <h1 className="detail-title">
                <i className="fas fa-project-diagram mr-2"></i>
                <b>{selectedProject.newProjectName}</b>
              </h1>
              <div className="detail-subtitle">
                <span className="detail-id">ID: {selectedProject.newProjectID || selectedProject.newInternalprojectID}</span>
                <span className={`status-badge large-badge ${getStatusClass(selectedProject.newApprovalID)}`}>
                  {selectedProject.newApprovalID}
                </span>
              </div>
            </div>
            <div className="detail-controls">
              <button onClick={handleBackToList} className="btn btn-secondary">
                <i className="fas fa-arrow-left mr-2"></i>
                <b>Back to List</b>
              </button>
              <button className="btn btn-primary">
                <i className="fas fa-edit mr-2"></i>
                <b>Edit Project</b>
              </button>
            </div>
          </div>
          
          <div className="detail-content-grid">
            <div className="detail-card">
              <div className="detail-card-header">
                <h3><i className="fas fa-info-circle mr-2"></i>Project Information</h3>
              </div>
              <div className="detail-card-body">
                <div className="details-grid">
                  <div className="detail-item">
                    <h3 className="detail-label">Project ID</h3>
                    <p className="detail-value">{selectedProject.newProjectID || "—"}</p>
                  </div>
                  <div className="detail-item">
                    <h3 className="detail-label">Internal Project ID</h3>
                    <p className="detail-value">{selectedProject.newInternalprojectID || "—"}</p>
                  </div>
                  <div className="detail-item">
                    <h3 className="detail-label">Bill of Materials</h3>
                    <p className="detail-value">{selectedProject.newBillofMaterials}</p>
                  </div>
                  <div className="detail-item">
                    <h3 className="detail-label">Approval Status</h3>
                    <p className="detail-value">
                      <span className={`status-badge ${getStatusClass(selectedProject.newApprovalID)}`}>
                        {selectedProject.newApprovalID}
                      </span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="detail-card">
              <div className="detail-card-header">
                <h3><i className="fas fa-chart-pie mr-2"></i>Cost Breakdown</h3>
              </div>
              <div className="detail-card-body">
                <div className="details-grid">
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
                    <p className="detail-value cost-highlight">₱{selectedProject.newOverallProjectCost}</p>
                  </div>
                </div>
                
                <div className="cost-chart-container">
                  <h4 className="chart-title">Cost Distribution</h4>
                  <div className="cost-bars">
                    <div className="cost-bar-item">
                      <div className="cost-bar-label">Labor</div>
                      <div className="cost-bar-container">
                        <div className="cost-bar labor-bar" style={{ width: '60%' }}></div>
                      </div>
                      <div className="cost-bar-value">₱{selectedProject.newLaborCost}</div>
                    </div>
                    <div className="cost-bar-item">
                      <div className="cost-bar-label">Utility</div>
                      <div className="cost-bar-container">
                        <div className="cost-bar utility-bar" style={{ width: '20%' }}></div>
                      </div>
                      <div className="cost-bar-value">₱{selectedProject.newUtilityCost}</div>
                    </div>
                    <div className="cost-bar-item">
                      <div className="cost-bar-label">Outsourced</div>
                      <div className="cost-bar-container">
                        <div className="cost-bar outsourced-bar" style={{ width: '40%' }}></div>
                      </div>
                      <div className="cost-bar-value">₱{selectedProject.newOutsourcedCost}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {!showProjectCosting && currentForm !== 1 && (
        <div className="view-list-container">
          <button onClick={() => setShowProjectCosting(true)} className="btn btn-primary">
            <i className="fas fa-list btn-icon"></i>
            <b>View Project Costing</b>
          </button>
        </div>
      )}
    </div>
  );
};

export default BodyContent;