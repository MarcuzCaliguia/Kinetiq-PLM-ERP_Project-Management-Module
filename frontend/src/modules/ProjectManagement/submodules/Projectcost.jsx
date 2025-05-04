import React, { useState } from "react";
import "../styles/Projectcost.css";

const BodyContent = () => {

  const [reportData, setReportData] = useState([
    {
      newProjectName: "Sample Project",
      newProjectID: "PRJ001",
      newInternalprojectID: "INT001",
      newBillofMaterials: "BOM001",
      newOverallProjectCost: "50000",
      newApprovalID: "Pending",
      newLaborCost: "20000",
      newUtilityCost: "15000",
      newOutsourcedCost: "15000"
    }
    // Add more sample data as needed
  ]);
  const [selectedReports, setSelectedReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");

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
      {!selectedProject && (
        <div className="report-list-container">
          <div className="list-header">
            <div className="list-title-section">
              <h1 className="list-title">
                <i className="fas fa-project-diagram mr-2"></i>
                <b>Project Costing</b>
              </h1>
              <p className="list-subtitle">View and manage all project costs</p>
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
                <p>No project costs found.</p>
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

      {selectedProject && (
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
    </div>
  );
};

export default BodyContent;