import React, { useState, useEffect } from "react";
import "../styles/Project List.css";
import listService from "../services/listService";

const BodyContent = () => {
  const [selectedNav, setSelectedNav] = useState("External Request");
  const [selectedNavdetails, setSelectedNavdetails] = useState("External Details");
  const [selectedRequests, setSelectedRequests] = useState([]);
  const [showProjectRequestList, setShowProjectRequestList] = useState(true);

  // State for data
  const [externalRequests, setExternalRequests] = useState([]);
  const [internalLabor, setInternalLabor] = useState([]);
  const [internalDetails, setInternalDetails] = useState([]);
  const [externalDetails, setExternalDetails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Add loading state for individual data types
  const [loadingExternal, setLoadingExternal] = useState(true);
  const [loadingLabor, setLoadingLabor] = useState(true);
  const [loadingInternalDetails, setLoadingInternalDetails] = useState(true);
  const [loadingExternalDetails, setLoadingExternalDetails] = useState(true);

  // Fetch data from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      // Fetch external projects
      setLoadingExternal(true);
      try {
        const externalRes = await listService.getExternalProjects();
        // Handle both array and paginated responses
        const externalData = externalRes.data.results || externalRes.data;
        console.log('External projects data:', externalData);
        setExternalRequests(externalData);
      } catch (err) {
        console.error('Error loading external projects:', err);
        setError('Failed to load some data. Please try again later.');
      } finally {
        setLoadingExternal(false);
      }
      
      // Fetch external labor
      setLoadingLabor(true);
      try {
        const laborRes = await listService.getExternalLabor();
        // Handle both array and paginated responses
        const laborData = laborRes.data.results || laborRes.data;
        console.log('External labor data:', laborData);
        setInternalLabor(laborData);
      } catch (err) {
        console.error('Error loading external labor:', err);
        if (!error) setError('Failed to load some data. Please try again later.');
      } finally {
        setLoadingLabor(false);
      }
      
      // Fetch internal details only when needed
      if (selectedNavdetails === "Internal Details" || !showProjectRequestList) {
        setLoadingInternalDetails(true);
        try {
          const internalDetailedRes = await listService.getInternalProjectsDetailed();
          setInternalDetails(internalDetailedRes.data);
        } catch (err) {
          console.error('Error loading internal details:', err);
          if (!error) setError('Failed to load some data. Please try again later.');
        } finally {
          setLoadingInternalDetails(false);
        }
      }
      
      // Fetch external details only when needed
      if (selectedNavdetails === "External Details" || !showProjectRequestList) {
        setLoadingExternalDetails(true);
        try {
          const externalDetailedRes = await listService.getExternalProjectsDetailed();
          setExternalDetails(externalDetailedRes.data);
        } catch (err) {
          console.error('Error loading external details:', err);
          if (!error) setError('Failed to load some data. Please try again later.');
        } finally {
          setLoadingExternalDetails(false);
        }
      }
      
      setLoading(false);
    };

    fetchData();
    
    // Safety timeout
    const timer = setTimeout(() => {
      if (loading) {
        setLoading(false);
        if (!error) setError('Request timed out. Please try again.');
      }
    }, 60000);
    
    return () => clearTimeout(timer);
  }, [selectedNavdetails, showProjectRequestList]);

  // Load details data when switching tabs
  useEffect(() => {
    const loadDetailsData = async () => {
      if (!showProjectRequestList) {
        if (selectedNavdetails === "Internal Details" && internalDetails.length === 0 && !loadingInternalDetails) {
          setLoadingInternalDetails(true);
          try {
            const internalDetailedRes = await listService.getInternalProjectsDetailed();
            setInternalDetails(internalDetailedRes.data);
          } catch (err) {
            console.error('Error loading internal details:', err);
            if (!error) setError('Failed to load internal details. Please try again.');
          } finally {
            setLoadingInternalDetails(false);
          }
        } else if (selectedNavdetails === "External Details" && externalDetails.length === 0 && !loadingExternalDetails) {
          setLoadingExternalDetails(true);
          try {
            const externalDetailedRes = await listService.getExternalProjectsDetailed();
            setExternalDetails(externalDetailedRes.data);
          } catch (err) {
            console.error('Error loading external details:', err);
            if (!error) setError('Failed to load external details. Please try again.');
          } finally {
            setLoadingExternalDetails(false);
          }
        }
      }
    };
    
    loadDetailsData();
  }, [selectedNavdetails, showProjectRequestList]);

  useEffect(() => {
    if (externalRequests.length > 0) {
      console.log('External Requests Data Structure:', externalRequests[0]);
    }
    if (internalLabor.length > 0) {
      console.log('Internal Labor Data Structure:', internalLabor[0]);
    }
  }, [externalRequests, internalLabor]);

  // Handle navigation click
  const handleNavClick = (nav) => {
    setSelectedNav(nav);
    setSelectedRequests([]);
  };

  const handleNavDetailsClick = (navdetails) => {
    setSelectedNavdetails(navdetails);
  };

  const handleCheckboxChange = (index) => {
    const updatedSelection = [...selectedRequests];
    updatedSelection[index] = !updatedSelection[index];
    setSelectedRequests(updatedSelection);
  };

  const handleRemoveRequests = async () => {
    try {
      const selectedIds = [];
      
      if (selectedNav === "Internal Request") {
        internalLabor.forEach((item, index) => {
          if (selectedRequests[index]) {
            selectedIds.push(item.project_labor_id);
          }
        });
        
        if (selectedIds.length > 0) {
          await listService.deleteExternalLabor(selectedIds);
          setInternalLabor(prev => prev.filter((_, index) => !selectedRequests[index]));
        }
      } else if (selectedNav === "External Request") {
        externalRequests.forEach((item, index) => {
          if (selectedRequests[index]) {
            selectedIds.push(item.project_id);
          }
        });
        
        if (selectedIds.length > 0) {
          await listService.deleteExternalProjects(selectedIds);
          setExternalRequests(prev => prev.filter((_, index) => !selectedRequests[index]));
        }
      }
      
      setSelectedRequests([]);
    } catch (err) {
      console.error('Failed to remove requests:', err);
      setError('Failed to remove selected items');
    }
  };

  const handleBackClick = () => {
    setShowProjectRequestList(true);
  };

  const handleProjectRequestDetailsClick = () => {
    setShowProjectRequestList(false);
  };

  // Show loading indicator while initial data is being fetched
  if (loading && (loadingExternal && loadingLabor)) {
    return (
      <div className="body-content-container">
        <div className="loading-message">
          <p>Loading project data...</p>
        </div>
      </div>
    );
  }

  // Rest of your render code...
  return (
    <div className="body-content-container">
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
      
      {showProjectRequestList ? (
        <>
          <div className="projreq">
            <h1>
              <b>Project Request</b>
            </h1>
          </div>
          <h2 className="appr">
            <b>Approve</b>
          </h2>
          <h2 className="nappr">
            <b>Not Approve</b>
          </h2>
          <h2 className="og">
            <b>Ongoing</b>
          </h2>

          <button className="filter">Filter By</button>
          <button className="remove" onClick={handleRemoveRequests}>
            Remove Request
          </button>

          <button className="projectrequestlist" onClick={handleProjectRequestDetailsClick}>
            <b>Project Request Details</b>
          </button>

          <div className="rectangle4"></div>

          <div className="topnavreq">
            <button
              className={`nav-button ${
                selectedNav === "Internal Request" ? "selected1" : ""
              }`}
              onClick={() => handleNavClick("Internal Request")}
            >
              <b>Internal Request</b>
            </button>

            <button
              className={`nav-button ${
                selectedNav === "External Request" ? "selected1" : ""
              }`}
              onClick={() => handleNavClick("External Request")}
            >
              <b>External Request</b>
            </button>
          </div>

          {selectedNav === "Internal Request" && (
  <div className="reqtable2">
    {loadingLabor ? (
      <div className="loading-message">Loading internal labor data...</div>
    ) : (
      <table className="reqtable3">
        <thead>
          <tr>
            <th></th>
            <th>
              <b>Int Project Labor ID</b>
            </th>
            <th>
              <b>Project ID</b>
            </th>
            <th>
              <b>Job Roles Needed</b>
            </th>
            <th>
              <b>Employee ID</b>
            </th>
          </tr>
        </thead>
        <tbody>
          {internalLabor.length > 0 ? (
            internalLabor.map((item, index) => (
              <tr key={index}>
                <td>
                  <input
                    type="checkbox"
                    checked={selectedRequests[index] || false}
                    onChange={() => handleCheckboxChange(index)}
                  />
                </td>
                <td>{item.project_labor_id}</td>
                <td>{item.project_id}</td>
                <td>{item.job_role_needed}</td>
                <td>{item.employee_id}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="5" className="no-data">No internal labor data available</td>
            </tr>
          )}
        </tbody>
      </table>
    )}
  </div>
)}

         {selectedNav === "External Request" && (
  <div className="reqtable4">
    {loadingExternal ? (
      <div className="loading-message">Loading external request data...</div>
    ) : (
      <table className="reqtable5">
        <thead>
          <tr>
            <th></th>
            <th>
              <b>ExtProject ID</b>
            </th>
            <th>
              <b>Project Request ID</b>
            </th>
            <th>
              <b>Project Status</b>
            </th>
            <th>
              <b>Job Role Needed</b>
            </th>
            <th>
              <b>Employee ID</b>
            </th>
            <th>
              <b>Project Equipment ID</b>
            </th>
          </tr>
        </thead>
        <tbody>
          {externalRequests.length > 0 ? (
            externalRequests.map((item, index) => (
              <tr key={index}>
                <td>
                  <input
                    type="checkbox"
                    checked={selectedRequests[index] || false}
                    onChange={() => handleCheckboxChange(index)}
                  />
                </td>
                <td>{item.project_id}</td>
                <td>{item.ext_project_request_id}</td>
                <td>{item.project_status}</td>
                {/* The next properties might need adjustment based on your API response */}
                <td>N/A</td>
                <td>N/A</td>
                <td>N/A</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="7" className="no-data">No external request data available</td>
            </tr>
          )}
        </tbody>
      </table>
    )}
  </div>
)}

          <div id="line5"></div>
          <div id="line6"></div>
        </>
      ) : (
        <>
          <div className="projectdetailsnav">
            <button
              className={`nav-button ${
                selectedNavdetails === "Internal Details" ? "selected1" : ""
              }`}
              onClick={() => handleNavDetailsClick("Internal Details")}
            >
              <b>Internal Details</b>
            </button>

            <button
              className={`nav-button ${
                selectedNavdetails === "External Details" ? "selected1" : ""
              }`}
              onClick={() => handleNavDetailsClick("External Details")}
            >
              <b>External Details</b>
            </button>
          </div>

          {selectedNavdetails === "Internal Details" && (
            <div className="internaldetails1">
              {loadingInternalDetails ? (
                <div className="loading-message">Loading internal details...</div>
              ) : (
                <table className="internaldetails">
                  <thead>
                    <tr>
                      <th></th>
                      <th>
                        <b>Int Project ID</b>
                      </th>
                      <th>
                        <b>Project Request ID</b>
                      </th>
                      <th>
                        <b>Project Name</b>
                      </th>
                      <th>
                        <b>Project Status</b>
                      </th>
                      <th>
                        <b>Approval ID</b>
                      </th>
                      <th>
                        <b>Employee ID</b>
                      </th>
                      <th>
                        <b>Department ID</b>
                      </th>
                      <th>
                        <b>Budget Request</b>
                      </th>
                      <th>
                        <b>Budget Description</b>
                      </th>
                      <th>
                        <b>Project Description</b>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {internalDetails.length > 0 ? (
                      internalDetails.map((item, index) => (
                        <tr key={index}>
                          <td></td>
                          <td>{item.intrnl_project_id}</td>
                          <td>{item.project_request?.project_request_id}</td>
                          <td>{item.project_request?.project_name}</td>
                          <td>{item.intrnl_project_status}</td>
                          <td>{item.approval_id}</td>
                          <td>{item.project_request?.employee_id}</td>
                          <td>{item.project_request?.dept_id}</td>
                          <td>{item.project_request?.project_budget_request}</td>
                          <td>{item.project_request?.project_budget_description}</td>
                          <td>{item.project_request?.project_description}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="11" className="no-data">No internal details available</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              )}
            </div>
          )}

          {selectedNavdetails === "External Details" && (
            <div className="externaldetails1">
              {loadingExternalDetails ? (
                <div className="loading-message">Loading external details...</div>
              ) : (
                <table className="externaldetails">
                  <thead>
                    <tr>
                      <th></th>
                      <th>
                        <b>ExtProject ID</b>
                      </th>
                      <th>
                        <b>Project Name</b>
                      </th>
                      <th>
                        <b>Project Description</b>
                      </th>
                      <th>
                        <b>Approval Id</b>
                      </th>
                      <th>
                        <b>Item ID</b>
                      </th>
                      <th>
                        <b>Project Status</b>
                      </th>
                      <th>
                        <b>Warranty Coverage</b>
                      </th>
                      <th>
                        <b>Warranty Start Date</b>
                      </th>
                      <th>
                        <b>Warranty End Date</b>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {externalDetails.length > 0 ? (
                      externalDetails.map((item, index) => (
                        <tr key={index}>
                          <td></td>
                          <td>{item.project_id}</td>
                          <td>{item.ext_project_request?.ext_project_name}</td>
                          <td>{item.ext_project_request?.ext_project_description}</td>
                          <td>{item.ext_project_request?.approval_id}</td>
                          <td>{item.ext_project_request?.item_id}</td>
                          <td>{item.project_status}</td>
                          <td>{item.warranty?.warranty_coverage_yr} {item.warranty?.warranty_coverage_yr ? 'Years' : ''}</td>
                          <td>{item.warranty?.warranty_start_date}</td>
                          <td>{item.warranty?.warranty_end_date}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="10" className="no-data">No external details available</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              )}
            </div>
          )}
          <button onClick={handleBackClick} className="back1">
            <b>Back</b>
          </button>
        </>
      )}
    </div>
  );
};

export default BodyContent;