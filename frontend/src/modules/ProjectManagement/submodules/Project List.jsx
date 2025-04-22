import React, { useState, useEffect } from "react";
import "../styles/Project List.css";
import listService from "../services/listService";

const BodyContent = () => {
  const [selectedNav, setSelectedNav] = useState("External Request");
  const [selectedNavdetails, setSelectedNavdetails] = useState("External Details");
  const [selectedRequests, setSelectedRequests] = useState([]);
  const [showProjectRequestList, setShowProjectRequestList] = useState(true);

  
  const [externalRequests, setExternalRequests] = useState([]);
  const [internalRequests, setInternalRequests] = useState([]);
  const [internalDetails, setInternalDetails] = useState([]);
  const [externalDetails, setExternalDetails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  
  const [loadingExternal, setLoadingExternal] = useState(true);
  const [loadingInternal, setLoadingInternal] = useState(true);
  const [loadingInternalDetails, setLoadingInternalDetails] = useState(false);
  const [loadingExternalDetails, setLoadingExternalDetails] = useState(false);

  
  useEffect(() => {
    const fetchData = async () => {
      console.log("Fetching initial data...");
      setLoading(true);
      
      try {
        
        setLoadingExternal(true);
        const externalRes = await listService.getExternalProjects();
        console.log('External projects response:', externalRes);
        const externalData = externalRes.data;
        setExternalRequests(externalData);
        setLoadingExternal(false);
        
        
        setLoadingInternal(true);
        const internalRes = await listService.getInternalProjects();
        console.log('Internal projects response:', internalRes);
        const internalData = internalRes.data;
        setInternalRequests(internalData);
        setLoadingInternal(false);
      } catch (err) {
        console.error('Error loading data:', err);
        setError('Failed to load data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  
  useEffect(() => {
    const loadDetailsData = async () => {
      if (!showProjectRequestList) {
        if (selectedNavdetails === "Internal Details" && internalDetails.length === 0) {
          setLoadingInternalDetails(true);
          try {
            const internalDetailedRes = await listService.getInternalProjectsDetailed();
            console.log('Internal details response:', internalDetailedRes);
            setInternalDetails(internalDetailedRes.data);
          } catch (err) {
            console.error('Error loading internal details:', err);
            setError('Failed to load internal details. Please try again.');
          } finally {
            setLoadingInternalDetails(false);
          }
        } else if (selectedNavdetails === "External Details" && externalDetails.length === 0) {
          setLoadingExternalDetails(true);
          try {
            const externalDetailedRes = await listService.getExternalProjectsDetailed();
            console.log('External details response:', externalDetailedRes);
            setExternalDetails(externalDetailedRes.data);
          } catch (err) {
            console.error('Error loading external details:', err);
            setError('Failed to load external details. Please try again.');
          } finally {
            setLoadingExternalDetails(false);
          }
        }
      }
    };
    
    loadDetailsData();
  }, [selectedNavdetails, showProjectRequestList]);

  
  const handleNavClick = (nav) => {
    setSelectedNav(nav);
    setSelectedRequests([]);
  };

  const handleNavDetailsClick = (navdetails) => {
    setSelectedNavdetails(navdetails);
  };

  const handleBackClick = () => {
    setShowProjectRequestList(true);
  };

  const handleProjectRequestDetailsClick = () => {
    setShowProjectRequestList(false);
  };

  
  const handleFilter = () => {
    
    console.log("Filter functionality will be implemented here");
  };

  
  if (loading) {
    return (
      <div className="body-content-container">
        <div className="loading-message">
          <p>Loading project data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="project-list-container">
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="retry-button"
          >
            Retry
          </button>
        </div>
      )}
      
      <div className="content-wrapper">
        {showProjectRequestList ? (
          <>
            <div className="header-section">
              <h1 className="page-title">Project Request</h1>
              
              <div className="status-indicators">
                <span className="status-indicator approved">
                  <div className="status-dot"></div>
                  <span>Approved</span>
                </span>
                <span className="status-indicator not-approved">
                  <div className="status-dot"></div>
                  <span>Not Approved</span>
                </span>
                <span className="status-indicator ongoing">
                  <div className="status-dot"></div>
                  <span>Ongoing</span>
                </span>
              </div>
              
              <div className="action-buttons">
                <button className="btn btn-filter" onClick={handleFilter}>
                  <i className="filter-icon"></i>
                  Filter By
                </button>
                <button className="btn btn-secondary" onClick={handleProjectRequestDetailsClick}>
                  <i className="details-icon"></i>
                  Project Request Details
                </button>
              </div>
            </div>

            <div className="tab-navigation">
              <button
                className={`tab-button ${selectedNav === "Internal Request" ? "active" : ""}`}
                onClick={() => handleNavClick("Internal Request")}
              >
                Internal Request
              </button>
              <button
                className={`tab-button ${selectedNav === "External Request" ? "active" : ""}`}
                onClick={() => handleNavClick("External Request")}
              >
                External Request
              </button>
            </div>

            <div className="table-container">
              {selectedNav === "Internal Request" && (
                <div className="data-table-wrapper">
                  {loadingInternal ? (
                    <div className="loading-message">
                      <div className="spinner"></div>
                      <p>Loading internal request data...</p>
                    </div>
                  ) : (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Project ID</th>
                          <th>Approval ID</th>
                          <th>Project Budget Approval</th>
                          <th>Project Budget Request</th>
                          <th>Project Budget Description</th>
                        </tr>
                      </thead>
                      <tbody>
                        {internalRequests.length > 0 ? (
                          internalRequests.map((item, index) => (
                            <tr key={index}>
                              <td>{item.intrnl_project_id || item.project_id}</td>
                              <td>{item.budget_approvals_id || item.approval_id || 'N/A'}</td>
                              <td>{item.project_budget_approval || 'N/A'}</td>
                              <td>{item.project_budget_request || 'N/A'}</td>
                              <td>{item.project_budget_description || 'N/A'}</td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan="5" className="no-data">
                              No internal request data available
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  )}
                </div>
              )}

              {selectedNav === "External Request" && (
                <div className="data-table-wrapper">
                  {loadingExternal ? (
                    <div className="loading-message">
                      <div className="spinner"></div>
                      <p>Loading external request data...</p>
                    </div>
                  ) : (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>ExtProject ID</th>
                          <th>Project Request ID</th>
                          <th>Project Status</th>
                          <th>Approval ID</th>
                          <th>Project Budget Approval</th>
                          <th>Sales Order ID</th>
                        </tr>
                      </thead>
                      <tbody>
                        {externalRequests.length > 0 ? (
                          externalRequests.map((item, index) => (
                            <tr key={index}>
                              <td>{item.project_id}</td>
                              <td>{item.ext_project_request_id}</td>
                              <td>
                                <span className={`status-badge ${item.project_status?.toLowerCase() || 'pending'}`}>
                                  {item.project_status || 'Pending'}
                                </span>
                              </td>
                              <td>{item.budget_approvals_id || item.approval_id || 'N/A'}</td>
                              <td>{item.project_budget_approval || 'N/A'}</td>
                              <td>{item.sales_order_id || 'N/A'}</td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan="6" className="no-data">
                              No external request data available
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  )}
                </div>
              )}
            </div>
          </>
        ) : (
          <>
            <div className="header-section">
              <h1 className="page-title">Project Details</h1>
              <button onClick={handleBackClick} className="btn btn-back">
                <i className="back-icon"></i>
                Back
              </button>
            </div>

            <div className="tab-navigation">
              <button
                className={`tab-button ${selectedNavdetails === "Internal Details" ? "active" : ""}`}
                onClick={() => handleNavDetailsClick("Internal Details")}
              >
                Internal Details
              </button>
              <button
                className={`tab-button ${selectedNavdetails === "External Details" ? "active" : ""}`}
                onClick={() => handleNavDetailsClick("External Details")}
              >
                External Details
              </button>
            </div>

            <div className="table-container">
              {selectedNavdetails === "Internal Details" && (
                <div className="data-table-wrapper">
                  {loadingInternalDetails ? (
                    <div className="loading-message">
                      <div className="spinner"></div>
                      <p>Loading internal details...</p>
                    </div>
                  ) : (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Int Project ID</th>
                          <th>Project Request ID</th>
                          <th>Project Name</th>
                          <th>Project Status</th>
                          <th>Approval ID</th>
                          <th>Department ID</th>
                          <th>Budget Request</th>
                          <th>Budget Description</th>
                          <th>Project Description</th>
                          <th>Project Budget Request</th>
                          <th>Project Budget Description</th>
                        </tr>
                      </thead>
                      <tbody>
                        {internalDetails.length > 0 ? (
                          internalDetails.map((item, index) => (
                            <tr key={index}>
                              <td>{item.intrnl_project_id}</td>
                              <td>{item.project_request_id}</td>
                              <td>{item.project_request?.project_name || 'N/A'}</td>
                              <td>
                                <span className={`status-badge ${item.intrnl_project_status?.toLowerCase() || 'pending'}`}>
                                  {item.intrnl_project_status || 'Pending'}
                                </span>
                              </td>
                              <td>{item.budget_approvals_id || item.approval_id || 'N/A'}</td>
                              <td>{item.project_request?.dept_id || 'N/A'}</td>
                              <td>{item.project_request?.project_budget_request || 'N/A'}</td>
                              <td>{item.project_request?.project_budget_description || 'N/A'}</td>
                              <td>{item.project_request?.project_description || 'N/A'}</td>
                              <td>{item.project_request?.project_budget_request || 'N/A'}</td>
                              <td>{item.project_request?.project_budget_description || 'N/A'}</td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan="11" className="no-data">
                              No internal details available
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  )}
                </div>
              )}

              {selectedNavdetails === "External Details" && (
                <div className="data-table-wrapper">
                  {loadingExternalDetails ? (
                    <div className="loading-message">
                      <div className="spinner"></div>
                      <p>Loading external details...</p>
                    </div>
                  ) : (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>ExtProject ID</th>
                          <th>Project Name</th>
                          <th>Project Description</th>
                          <th>Approval ID</th>
                          <th>Item ID</th>
                          <th>Project Status</th>
                          <th>Warranty Coverage</th>
                          <th>Warranty Start Date</th>
                          <th>Warranty End Date</th>
                          <th>Sales Order ID</th>
                        </tr>
                      </thead>
                      <tbody>
                        {externalDetails.length > 0 ? (
                          externalDetails.map((item, index) => (
                            <tr key={index}>
                              <td>{item.project_id}</td>
                              <td>{item.ext_project_request?.ext_project_name || 'N/A'}</td>
                              <td>{item.ext_project_request?.ext_project_description || 'N/A'}</td>
                              <td>{item.budget_approvals_id || item.ext_project_request?.approval_id || 'N/A'}</td>
                              <td>{item.ext_project_request?.item_id || 'N/A'}</td>
                              <td>
                                <span className={`status-badge ${item.project_status?.toLowerCase() || 'pending'}`}>
                                  {item.project_status || 'Pending'}
                                </span>
                              </td>
                              <td>{item.warranty?.warranty_coverage_yr} {item.warranty?.warranty_coverage_yr ? 'Years' : ''}</td>
                              <td>{item.warranty?.warranty_start_date || 'N/A'}</td>
                              <td>{item.warranty?.warranty_end_date || 'N/A'}</td>
                              <td>{item.sales_order_id || item.ext_project_request?.item_id || 'N/A'}</td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan="10" className="no-data">
                              No external details available
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  )}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default BodyContent;