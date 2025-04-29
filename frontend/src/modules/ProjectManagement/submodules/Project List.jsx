// Project List.jsx
import React, { useState, useEffect } from "react";
import "../styles/Project List.css";
import axios from 'axios';

const ProjectList = () => {
  const [selectedNav, setSelectedNav] = useState("Internal Request");
  const [selectedNavdetails, setSelectedNavdetails] = useState("Internal Details");
  const [selectedRequests, setSelectedRequests] = useState([]);
  const [showProjectRequestList, setShowProjectRequestList] = useState(true);

  // State for data
  const [internalRequests, setInternalRequests] = useState([]);
  const [externalRequests, setExternalRequests] = useState([]);
  const [internalDetails, setInternalDetails] = useState([]);
  const [externalDetails, setExternalDetails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Pagination state
  const [internalRequestsPage, setInternalRequestsPage] = useState(1);
  const [externalRequestsPage, setExternalRequestsPage] = useState(1);
  const [internalDetailsPage, setInternalDetailsPage] = useState(1);
  const [externalDetailsPage, setExternalDetailsPage] = useState(1);
  const [internalRequestsPagination, setInternalRequestsPagination] = useState({});
  const [externalRequestsPagination, setExternalRequestsPagination] = useState({});
  const [internalDetailsPagination, setInternalDetailsPagination] = useState({});
  const [externalDetailsPagination, setExternalDetailsPagination] = useState({});
  
  // Filter state
  const [showFilter, setShowFilter] = useState(false);
  const [internalFilters, setInternalFilters] = useState({
    project_name: '',
    approval_id: '',
    employee_id: '',
    dept_id: '',
    status: ''
  });
  const [externalFilters, setExternalFilters] = useState({
    project_name: '',
    approval_id: '',
    item_id: '',
    status: ''
  });
  
  // Add loading state for individual data types
  const [loadingInternal, setLoadingInternal] = useState(true);
  const [loadingExternal, setLoadingExternal] = useState(true);
  const [loadingInternalDetails, setLoadingInternalDetails] = useState(true);
  const [loadingExternalDetails, setLoadingExternalDetails] = useState(true);

  // API base URL
  const API_URL = '/api/project-management';

  // Helper to build query string from filters
  const buildQueryString = (filters) => {
    return Object.entries(filters)
      .filter(([_, value]) => value)
      .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
      .join('&');
  };

  // Fetch data from API with pagination and filters
  const fetchInternalRequests = async (page = 1) => {
    setLoadingInternal(true);
    try {
      const queryString = buildQueryString(internalFilters);
      const url = `${API_URL}/internal-requests/?page=${page}${queryString ? '&' + queryString : ''}`;
      
      const response = await axios.get(url);
      console.log('Internal requests data:', response.data);
      setInternalRequests(response.data.results || []);
      setInternalRequestsPagination({
        count: response.data.count,
        next: response.data.next,
        previous: response.data.previous
      });
      setInternalRequestsPage(page);
      return true;
    } catch (err) {
      console.error('Error loading internal requests:', err);
      if (err.response && err.response.status === 404) {
        // Handle 404 (likely a page that doesn't exist)
        setInternalRequestsPage(1);
        return fetchInternalRequests(1);
      }
      return false;
    } finally {
      setLoadingInternal(false);
    }
  };

  const fetchExternalRequests = async (page = 1) => {
    setLoadingExternal(true);
    try {
      const queryString = buildQueryString(externalFilters);
      const url = `${API_URL}/external-requests/?page=${page}${queryString ? '&' + queryString : ''}`;
      
      const response = await axios.get(url);
      console.log('External requests data:', response.data);
      setExternalRequests(response.data.results || []);
      setExternalRequestsPagination({
        count: response.data.count,
        next: response.data.next,
        previous: response.data.previous
      });
      setExternalRequestsPage(page);
      return true;
    } catch (err) {
      console.error('Error loading external requests:', err);
      if (err.response && err.response.status === 404) {
        setExternalRequestsPage(1);
        return fetchExternalRequests(1);
      }
      return false;
    } finally {
      setLoadingExternal(false);
    }
  };

  const fetchInternalDetails = async (page = 1) => {
    setLoadingInternalDetails(true);
    try {
      const response = await axios.get(`${API_URL}/internal-projects/?page=${page}`);
      console.log('Internal details data:', response.data);
      setInternalDetails(response.data.results || []);
      setInternalDetailsPagination({
        count: response.data.count,
        next: response.data.next,
        previous: response.data.previous
      });
      setInternalDetailsPage(page);
      return true;
    } catch (err) {
      console.error('Error loading internal details:', err);
      if (err.response && err.response.status === 404) {
        setInternalDetailsPage(1);
        return fetchInternalDetails(1);
      }
      return false;
    } finally {
      setLoadingInternalDetails(false);
    }
  };

  const fetchExternalDetails = async (page = 1) => {
    setLoadingExternalDetails(true);
    try {
      const response = await axios.get(`${API_URL}/external-projects/?page=${page}`);
      console.log('External details data:', response.data);
      setExternalDetails(response.data.results || []);
      setExternalDetailsPagination({
        count: response.data.count,
        next: response.data.next,
        previous: response.data.previous
      });
      setExternalDetailsPage(page);
      return true;
    } catch (err) {
      console.error('Error loading external details:', err);
      if (err.response && err.response.status === 404) {
        setExternalDetailsPage(1);
        return fetchExternalDetails(1);
      }
      return false;
    } finally {
      setLoadingExternalDetails(false);
    }
  };

  // Initial data loading
  useEffect(() => {
    const loadInitialData = async () => {
      setLoading(true);
      setError(null);
      
      let success = true;
      
      // Load data based on current view
      if (showProjectRequestList) {
        if (selectedNav === "Internal Request") {
          success = await fetchInternalRequests();
        } else {
          success = await fetchExternalRequests();
        }
      } else {
        if (selectedNavdetails === "Internal Details") {
          success = await fetchInternalDetails();
        } else {
          success = await fetchExternalDetails();
        }
      }
      
      if (!success) {
        setError('Failed to load data. Please try again.');
      }
      
      setLoading(false);
    };

    loadInitialData();
    
    // Shorter timeout (15 seconds instead of 60)
    const timer = setTimeout(() => {
      if (loading) {
        setLoading(false);
        if (!error) setError('Request is taking longer than expected. Data may be incomplete.');
      }
    }, 15000);
    
    return () => clearTimeout(timer);
  }, [selectedNav, selectedNavdetails, showProjectRequestList]);

  // Handle navigation click
  const handleNavClick = (nav) => {
    setSelectedNav(nav);
    setSelectedRequests([]);
    
    // Load appropriate data when switching tabs
    if (nav === "Internal Request") {
      fetchInternalRequests(internalRequestsPage);
    } else {
      fetchExternalRequests(externalRequestsPage);
    }
  };

  const handleNavDetailsClick = (navdetails) => {
    setSelectedNavdetails(navdetails);
    
    // Load appropriate data when switching detail tabs
    if (navdetails === "Internal Details") {
      fetchInternalDetails(internalDetailsPage);
    } else {
      fetchExternalDetails(externalDetailsPage);
    }
  };

  const handleCheckboxChange = (index) => {
    const updatedSelection = [...selectedRequests];
    updatedSelection[index] = !updatedSelection[index];
    setSelectedRequests(updatedSelection);
  };

  const handleArchiveRequests = async () => {
    try {
      const selectedIds = [];
      
      if (selectedNav === "Internal Request") {
        internalRequests.forEach((item, index) => {
          if (selectedRequests[index]) {
            selectedIds.push(item.project_request_id);
          }
        });
        
        if (selectedIds.length > 0) {
          await axios.post(`${API_URL}/internal-requests/bulk_archive/`, { ids: selectedIds });
          // Refresh data after archiving
          fetchInternalRequests(internalRequestsPage);
        }
      } else if (selectedNav === "External Request") {
        externalRequests.forEach((item, index) => {
          if (selectedRequests[index]) {
            selectedIds.push(item.ext_project_request_id);
          }
        });
        
        if (selectedIds.length > 0) {
          await axios.post(`${API_URL}/external-requests/bulk_archive/`, { ids: selectedIds });
          // Refresh data after archiving
          fetchExternalRequests(externalRequestsPage);
        }
      }
      
      setSelectedRequests([]);
    } catch (err) {
      console.error('Failed to archive requests:', err);
      setError('Failed to archive selected items');
    }
  };

  const handleBackClick = () => {
    setShowProjectRequestList(true);
  };

  const handleProjectRequestDetailsClick = () => {
    setShowProjectRequestList(false);
    
    // Load appropriate details data
    if (selectedNavdetails === "Internal Details") {
      fetchInternalDetails();
    } else {
      fetchExternalDetails();
    }
  };

  // Pagination handlers
  const handlePageChange = (type, newPage) => {
    switch(type) {
      case 'internalRequests':
        fetchInternalRequests(newPage);
        break;
      case 'externalRequests':
        fetchExternalRequests(newPage);
        break;
      case 'internalDetails':
        fetchInternalDetails(newPage);
        break;
      case 'externalDetails':
        fetchExternalDetails(newPage);
        break;
      default:
        break;
    }
  };
  
  // Filter handlers
  const toggleFilter = () => {
    setShowFilter(!showFilter);
  };
  
  const handleFilterChange = (type, field, value) => {
    if (type === 'internal') {
      setInternalFilters({
        ...internalFilters,
        [field]: value
      });
    } else {
      setExternalFilters({
        ...externalFilters,
        [field]: value
      });
    }
  };
  
  const applyFilters = () => {
    if (selectedNav === "Internal Request") {
      fetchInternalRequests(1); // Reset to page 1 when applying filters
    } else {
      fetchExternalRequests(1);
    }
    setShowFilter(false);
  };
  
  const clearFilters = () => {
    if (selectedNav === "Internal Request") {
      setInternalFilters({
        project_name: '',
        approval_id: '',
        employee_id: '',
        dept_id: '',
        status: ''
      });
      fetchInternalRequests(1);
    } else {
      setExternalFilters({
        project_name: '',
        approval_id: '',
        item_id: '',
        status: ''
      });
      fetchExternalRequests(1);
    }
    setShowFilter(false);
  };

  // Show loading indicator while initial data is being fetched
  if (loading && (loadingInternal && loadingExternal)) {
    return (
      <div className="project-list-container">
        <div className="content-wrapper">
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Loading project data...</p>
          </div>
        </div>
      </div>
    );
  }

  // Check if any requests are selected
  const hasSelectedRequests = selectedRequests.some(selected => selected);

  // Pagination component
  const Pagination = ({ type, currentPage, pagination }) => {
    if (!pagination || !pagination.count) return null;
    
    const totalPages = Math.ceil(pagination.count / 10);
    
    return (
      <div className="pagination">
        <button 
          className="pagination-button" 
          disabled={currentPage <= 1}
          onClick={() => handlePageChange(type, currentPage - 1)}
        >
          Previous
        </button>
        <span className="pagination-info">Page {currentPage} of {totalPages}</span>
        <button 
          className="pagination-button" 
          disabled={currentPage >= totalPages}
          onClick={() => handlePageChange(type, currentPage + 1)}
        >
          Next
        </button>
      </div>
    );
  };

  // Filter component
  const FilterPanel = () => {
    if (!showFilter) return null;
    
    return (
      <div className="filter-panel">
        <div className="filter-header">
          <h3>Filter Projects</h3>
          <button className="close-filter" onClick={toggleFilter}>×</button>
        </div>
        
        {selectedNav === "Internal Request" ? (
          <div className="filter-form">
            <div className="filter-field">
              <label>Project Name</label>
              <input 
                type="text" 
                value={internalFilters.project_name} 
                onChange={(e) => handleFilterChange('internal', 'project_name', e.target.value)}
                placeholder="Filter by project name"
              />
            </div>
            <div className="filter-field">
              <label>Approval ID</label>
              <input 
                type="text" 
                value={internalFilters.approval_id} 
                onChange={(e) => handleFilterChange('internal', 'approval_id', e.target.value)}
                placeholder="Filter by approval ID"
              />
            </div>
            <div className="filter-field">
              <label>Employee ID</label>
              <input 
                type="text" 
                value={internalFilters.employee_id} 
                onChange={(e) => handleFilterChange('internal', 'employee_id', e.target.value)}
                placeholder="Filter by employee ID"
              />
            </div>
            <div className="filter-field">
              <label>Department ID</label>
              <input 
                type="text" 
                value={internalFilters.dept_id} 
                onChange={(e) => handleFilterChange('internal', 'dept_id', e.target.value)}
                placeholder="Filter by department ID"
              />
            </div>
            <div className="filter-field">
              <label>Project Status</label>
              <select 
                value={internalFilters.status} 
                onChange={(e) => handleFilterChange('internal', 'status', e.target.value)}
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="ongoing">Ongoing</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>
        ) : (
          <div className="filter-form">
            <div className="filter-field">
              <label>Project Name</label>
              <input 
                type="text" 
                value={externalFilters.project_name} 
                onChange={(e) => handleFilterChange('external', 'project_name', e.target.value)}
                placeholder="Filter by project name"
              />
            </div>
            <div className="filter-field">
              <label>Approval ID</label>
              <input 
                type="text" 
                value={externalFilters.approval_id} 
                onChange={(e) => handleFilterChange('external', 'approval_id', e.target.value)}
                placeholder="Filter by approval ID"
              />
            </div>
            <div className="filter-field">
              <label>Item ID</label>
              <input 
                type="text" 
                value={externalFilters.item_id} 
                onChange={(e) => handleFilterChange('external', 'item_id', e.target.value)}
                placeholder="Filter by item ID"
              />
            </div>
            <div className="filter-field">
              <label>Project Status</label>
              <select 
                value={externalFilters.status} 
                onChange={(e) => handleFilterChange('external', 'status', e.target.value)}
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="ongoing">Ongoing</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>
        )}
        
        <div className="filter-actions">
          <button className="btn btn-secondary" onClick={clearFilters}>Clear Filters</button>
          <button className="btn btn-primary" onClick={applyFilters}>Apply Filters</button>
        </div>
      </div>
    );
  };

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
              <h1 className="page-title">Project Request Management</h1>
              
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
                <button className="btn btn-filter" onClick={toggleFilter}>
                  <i className="filter-icon"></i>
                  Filter Projects
                </button>
                {hasSelectedRequests && (
                  <button className="btn btn-warning" onClick={handleArchiveRequests}>
                    <i className="archive-icon"></i>
                    Archive Selected
                  </button>
                )}
                <button className="btn btn-primary" onClick={handleProjectRequestDetailsClick}>
                  <i className="details-icon"></i>
                  View Project Details
                </button>
              </div>
            </div>

            <FilterPanel />

            <div className="tab-navigation">
              <button
                className={`tab-button ${selectedNav === "Internal Request" ? "active" : ""}`}
                onClick={() => handleNavClick("Internal Request")}
              >
                Internal Requests
              </button>
              <button
                className={`tab-button ${selectedNav === "External Request" ? "active" : ""}`}
                onClick={() => handleNavClick("External Request")}
              >
                External Requests
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
                    <>
                      <table className="data-table">
                      <thead>
  <tr>
    <th className="select-col"></th>
    <th>Project Request ID</th>
    <th>Project Name</th>
    <th>Approval ID</th>
    <th>Request Date</th>
    <th>Employee</th>
    <th>Department</th> 
    <th>Project Status</th>
  </tr>
</thead>
                        <tbody>
                          {internalRequests.length > 0 ? (
                            internalRequests.map((item, index) => (
                              <tr key={index}>
                                <td className="select-col">
                                  <input
                                    type="checkbox"
                                    checked={selectedRequests[index] || false}
                                    onChange={() => handleCheckboxChange(index)}
                                  />
                                </td>
                                <td>{item.project_request_id}</td>
                                <td>{item.project_name}</td>
                                <td>{item.approval_id}</td>
                                <td>{item.request_date}</td>
                                <td>{item.employee_name}</td>
                                <td>{item.department}</td> 
                                <td>
                                  <span className={`status-badge ${item.project_status?.toLowerCase() || 'pending'}`}>
                                    {item.project_status || 'Pending'}
                                  </span>
                                </td>
                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td colSpan="8" className="no-data">
                                No internal request data available
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                      <Pagination 
                        type="internalRequests" 
                        currentPage={internalRequestsPage} 
                        pagination={internalRequestsPagination} 
                      />
                    </>
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
                    <>
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th className="select-col"></th>
                            <th>Project Request ID</th>
                            <th>Project Name</th>
                            <th>Approval ID</th>
                            <th>Item ID</th>
                            <th>Start Date</th>
                            <th>Project Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {externalRequests.length > 0 ? (
                            externalRequests.map((item, index) => (
                              <tr key={index}>
                                <td className="select-col">
                                  <input
                                    type="checkbox"
                                    checked={selectedRequests[index] || false}
                                    onChange={() => handleCheckboxChange(index)}
                                  />
                                </td>
                                <td>{item.ext_project_request_id}</td>
                                <td>{item.project_name}</td>
                                <td>{item.approval_id}</td>
                                <td>{item.item_id}</td>
                                <td>{item.start_date}</td>
                                <td>
                                  <span className={`status-badge ${item.project_status?.toLowerCase() || 'pending'}`}>
                                    {item.project_status || 'Pending'}
                                  </span>
                                </td>
                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td colSpan="7" className="no-data">
                                No external request data available
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                      <Pagination 
                        type="externalRequests" 
                        currentPage={externalRequestsPage} 
                        pagination={externalRequestsPagination} 
                      />
                    </>
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
                Back to Projects
              </button>
            </div>

            <div className="tab-navigation">
              <button
                className={`tab-button ${selectedNavdetails === "Internal Details" ? "active" : ""}`}
                onClick={() => handleNavDetailsClick("Internal Details")}
              >
                Internal Project Details
              </button>
              <button
                className={`tab-button ${selectedNavdetails === "External Details" ? "active" : ""}`}
                onClick={() => handleNavDetailsClick("External Details")}
              >
                External Project Details
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
                    <>
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>Project ID</th>
                            <th>Request ID</th>
                            <th>Project Name</th>
                            <th>Status</th>
                            <th>Approval ID</th>
                            <th>Employee ID</th>
                            <th>Department</th>                  
                            <th>Description</th>
                            <th>Start Date</th>
                            <th>End Date</th>
                            <th>Issues</th>
                          </tr>
                        </thead>
                        <tbody>
                          {internalDetails.length > 0 ? (
                            internalDetails.map((item, index) => (
                              <tr key={index}>
                                <td>{item.intrnl_project_id}</td>
                                <td>{item.project_request_id}</td>
                                <td>{item.project_name}</td>
                                <td>
                                  <span className={`status-badge ${item.status?.toLowerCase() || 'pending'}`}>
                                    {item.status || 'Pending'}
                                  </span>
                                </td>
                                <td>{item.approval_id}</td>
                                <td>{item.employee_id}</td>
                                <td>{item.department}</td>
                                <td>{item.description}</td>
                                <td>{item.start_date}</td>
                                <td>{item.estimated_end_date}</td>
                                <td>{item.project_issues}</td>
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
                      <Pagination 
                        type="internalDetails" 
                        currentPage={internalDetailsPage} 
                        pagination={internalDetailsPagination} 
                      />
                    </>
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
                    <>
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>Project ID</th>
                            <th>Project Name</th>
                            <th>Approval ID</th>
                            <th>Item ID</th>
                            <th>Start Date</th>
                            <th>Project Status</th>
                            <th>Project Milestone</th>
                            <th>End Date</th>
                            <th>Warranty Coverage</th>
                            <th>Warranty Start</th>
                            <th>Warranty End</th>
                            <th>Warranty Status</th>
                            <th>Issues</th>
                          </tr>
                        </thead>
                        <tbody>
                          {externalDetails.length > 0 ? (
                            externalDetails.map((item, index) => (
                              <tr key={index}>
                                <td>{item.project_id}</td>
                                <td>{item.project_name}</td>
                                <td>{item.approval_id}</td>
                                <td>{item.item_id}</td>
                                <td>{item.start_date}</td>
                                <td>
                                  <span className={`status-badge ${item.project_status?.toLowerCase() || 'pending'}`}>
                                    {item.project_status || 'Pending'}
                                  </span>
                                </td>
                                <td>{item.project_milestone}</td>
                                <td>{item.estimated_end_date}</td>
                                <td>{item.warranty_coverage_yr}</td>
                                <td>{item.warranty_start_date}</td>
                                <td>{item.warranty_end_date}</td>
                                <td>{item.warranty_status}</td>
                                <td>{item.project_issues}</td>
                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td colSpan="13" className="no-data">
                                No external details available
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                      <Pagination 
                        type="externalDetails" 
                        currentPage={externalDetailsPage} 
                        pagination={externalDetailsPagination} 
                      />
                    </>
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

export default ProjectList;