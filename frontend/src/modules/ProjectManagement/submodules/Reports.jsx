import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/Reports.css";
import GenerateReports from "./GenerateReports";
import ProjectForms from "./ProjectForms";

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

axios.interceptors.response.use(
  response => response,
  error => {
    console.error('Axios Error:', error);
    return Promise.reject(error);
  }
);

const BodyContent = () => {
  const [showProjectForms, setShowProjectForms] = useState(false);
  const [newProjectID, setNewProjectID] = useState("");
  const [newInternalprojectid, setNewInternalprojectid] = useState("");
  const [selectedReporttype, setSelectedReporttype] = useState("");
  const [newReporttitle, setNewReporttitle] = useState("");
  const [selectedReceivedform, setSelectedReceievedform] = useState("");
  const [newDatecreated, setNewDatecreated] = useState("");
  const [newDescriptionreport, setNewDescriptionreport] = useState("");
  const [selectedAssignedto, setSelectedAssignedto] = useState("");
  
  const [showReportList, setShowReportList] = useState(false);
  const [currentForm, setCurrentForm] = useState(1);
  const [reportData, setReportData] = useState([]);
  const [selectedReports, setSelectedReports] = useState([]);
  
  
  const [showGenerateReports, setShowGenerateReports] = useState(false);
  
  const [reportTypes, setReportTypes] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [externalProjects, setExternalProjects] = useState([]);
  const [internalProjects, setInternalProjects] = useState([]);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiErrors, setApiErrors] = useState({
    reports: false,
    reportTypes: false,
    departments: false,
    externalProjects: false,
    internalProjects: false
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        setApiErrors({
          reports: false,
          reportTypes: false,
          departments: false,
          externalProjects: false,
          internalProjects: false
        });
        
        console.log("Fetching data from API...");
        
        try {
          const reportsResponse = await axios.get('/api/reports/');
          console.log('Reports response:', reportsResponse.data);
          setReportData(Array.isArray(reportsResponse.data) ? 
            reportsResponse.data : reportsResponse.data.results || []);
        } catch (err) {
          console.error('Error fetching reports:', err);
          setApiErrors(prev => ({ ...prev, reports: true }));
        }
        
        try {
          const typesResponse = await axios.get('/api/reports/report_types/');
          console.log('Report types response:', typesResponse.data);
          setReportTypes(typesResponse.data || []);
        } catch (err) {
          console.error('Error fetching report types:', err);
          setApiErrors(prev => ({ ...prev, reportTypes: true }));
          setReportTypes([
            'Sales Order',
            'Resource Availability',
            'Bill of Material',
            'Information',
            'Progress Report',
            'Project Details',
            'Inventory Movement',
          ]);
        }
        
        try {
          const deptsResponse = await axios.get('/api/reports/departments/');
          console.log('Departments response:', deptsResponse.data);
          setDepartments(deptsResponse.data || []);
        } catch (err) {
          console.error('Error fetching departments:', err);
          setApiErrors(prev => ({ ...prev, departments: true }));
          setDepartments([
            'Accounting',
            'Admin',
            'Distribution',
            'Finance',
            'Human Resources',
            'Inventory',
            'Management',
            'MRP',
            'Operations',
            'Production',
            'Project Management',
            'Purchasing',
            'Sales',
            'Services',
            'Solution Customizing',
            'Department - IT Team',
            'Department - Project Management',
          ]);
        }
        
        try {
          const externalProjectsResponse = await axios.get('/api/external-projects/');
          console.log('External projects response:', externalProjectsResponse.data);
          setExternalProjects(externalProjectsResponse.data || []);
        } catch (err) {
          console.error('Error fetching external projects:', err);
          setApiErrors(prev => ({ ...prev, externalProjects: true }));
        }
        
        try {
          const internalProjectsResponse = await axios.get('/api/internal-projects/');
          console.log('Internal projects response:', internalProjectsResponse.data);
          setInternalProjects(internalProjectsResponse.data || []);
        } catch (err) {
          console.error('Error fetching internal projects:', err);
          setApiErrors(prev => ({ ...prev, internalProjects: true }));
        }
        
        setLoading(false);
      } catch (err) {
        console.error('API Error:', err);
        setError('Error fetching data: ' + (err.response?.data?.error || err.message));
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const handleFirstSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      
      const reportData = {
        project_id: newProjectID || null,
        intrnl_project_id: newInternalprojectid || null,
        report_type: selectedReporttype,
        report_title: newReporttitle,
        received_from: selectedReceivedform,
        date_created: newDatecreated,
        assigned_to: selectedAssignedto,
        description: newDescriptionreport
      };
      
      console.log("Submitting report data:", reportData);
      
      const response = await axios.post('/api/reports/', reportData);
      console.log('Create report response:', response.data);
      
      try {
        const reportsResponse = await axios.get('/api/reports/');
        setReportData(Array.isArray(reportsResponse.data) ? 
          reportsResponse.data : reportsResponse.data.results || []);
      } catch (err) {
        console.error('Error refreshing reports:', err);
      }
      
      setShowReportList(true);
      setCurrentForm(null);
      resetForm();
      setLoading(false);
      
    } catch (err) {
      console.error('API Error:', err);
      setError('Error creating report: ' + (err.response?.data?.error || err.message));
      setLoading(false);
    }
  };

  const resetForm = () => {
    setNewProjectID("");
    setNewInternalprojectid("");
    setSelectedReporttype("");
    setNewReporttitle("");
    setSelectedReceievedform("");
    setNewDatecreated("");
    setNewDescriptionreport("");
    setSelectedAssignedto("");
  };

  const handleBackClick = () => {
    setShowReportList(false);
    setCurrentForm(1);
  };

  
  const handleShowGenerateReports = () => {
    setShowReportList(false);
    setCurrentForm(null);
    setShowGenerateReports(true);
  };

  
  const handleBackFromGenerateReports = () => {
    setShowGenerateReports(false);
    setShowReportList(true);
  };

  const handleRemoveReports = async () => {
    if (selectedReports.length === 0) return;
    
    try {
      setLoading(true);
      setError(null);
      
      for (const index of selectedReports) {
        const reportId = reportData[index].report_monitoring_id;
        console.log(`Deleting report with ID: ${reportId}`);
        await axios.delete(`/api/reports/${reportId}/`);
      }
      
      try {
        const reportsResponse = await axios.get('/api/reports/');
        setReportData(Array.isArray(reportsResponse.data) ? 
          reportsResponse.data : reportsResponse.data.results || []);
      } catch (err) {
        console.error('Error refreshing reports after deletion:', err);
      }
      
      setSelectedReports([]);
      setLoading(false);
      
    } catch (err) {
      console.error('API Error:', err);
      setError('Error removing reports: ' + (err.response?.data?.error || err.message));
      setLoading(false);
    }
  };

  const handleCheckboxChange = (index) => {
    if (selectedReports.includes(index)) {
      setSelectedReports(selectedReports.filter((i) => i !== index));
    } else {
      setSelectedReports([...selectedReports, index]);
    }
  };

  const handleExternalProjectChange = (e) => {
    setNewProjectID(e.target.value);
    if (e.target.value) {
      setNewInternalprojectid("");
    }
  };

  const handleInternalProjectChange = (e) => {
    setNewInternalprojectid(e.target.value);
    if (e.target.value) {
      setNewProjectID("");
    }
  };

  const handleShowProjectForms = () => {
    setShowReportList(false);
    setCurrentForm(null);
    setShowGenerateReports(false);
    setShowProjectForms(true);
  };
  
  const handleBackFromProjectForms = () => {
    setShowProjectForms(false);
    setShowReportList(true);
  };
  

  if (loading && (!reportTypes.length && !departments.length)) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading data...</p>
      </div>
    );
  }
  
  const hasApiErrors = Object.values(apiErrors).some(val => val);
  
  return (
    <div className="body-content-container">
      {error && (
        <div className="error-banner">
          <p>{error}</p>
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}
      
      {hasApiErrors && (
        <div className="warning-banner">
          <p>Some data could not be loaded. The form may have limited functionality.</p>
          <button onClick={() => window.location.reload()}>Reload Page</button>
        </div>
      )}
      
      {showProjectForms ? (
        <div className="project-forms-wrapper">
          <button 
            onClick={handleBackFromProjectForms} 
            className="back-button"
          >
            <b>← Back to Report List</b>
          </button>
          <ProjectForms />
        </div>
      ) : showGenerateReports ? (
        <div className="generate-reports-wrapper">
          <button 
            onClick={handleBackFromGenerateReports} 
            className="back-button"
          >
            <b>← Back to Report List</b>
          </button>
          <GenerateReports 
            reportData={reportData}
            reportTypes={reportTypes}
            externalProjects={externalProjects}
            internalProjects={internalProjects}
          />
        </div>
      ) : (
        <>

          {currentForm === 1 && (
            <form onSubmit={handleFirstSubmit}>
              <h1 className="newreport">
                <b>New Report</b>
              </h1>
              <h1 className="projectlist">Project Task List</h1>

              <label className="projectidrep">
                <b>Project ID*</b>
              </label>
              <br />
              <select
                className="projectidrep2"
                value={newProjectID}
                onChange={handleExternalProjectChange}
                disabled={loading || newInternalprojectid !== "" || apiErrors.externalProjects}
              >
                <option value="">Select Project ID</option>
                {externalProjects.map((project) => (
                  <option key={project.project_id} value={project.project_id}>
                    {project.project_id} {project.project_status ? `- ${project.project_status}` : ''}
                  </option>
                ))}
              </select>
              {apiErrors.externalProjects && (
                <div className="field-error">External projects could not be loaded</div>
              )}
              <br />

              <label className="internalprojid">
                <b>Internal Project ID</b>
              </label>
              <br />
              <select
                className="internalprojid2"
                value={newInternalprojectid}
                onChange={handleInternalProjectChange}
                disabled={loading || newProjectID !== "" || apiErrors.internalProjects}
              >
                <option value="">Select Internal Project ID</option>
                {internalProjects.map((project) => (
                  <option key={project.intrnl_project_id} value={project.intrnl_project_id}>
                    {project.intrnl_project_id} {project.intrnl_project_status ? `- ${project.intrnl_project_status}` : ''}
                  </option>
                ))}
              </select>
              {apiErrors.internalProjects && (
                <div className="field-error">Internal projects could not be loaded</div>
              )}
              <br />

              <label className="reporttype">
                <b>Report Type</b>
              </label>
              <br />
              <select
                name="Reporttype"
                className="reporttype2"
                value={selectedReporttype}
                onChange={(e) => setSelectedReporttype(e.target.value)}
                required
                disabled={loading}
              >
                <option value="">Choose Report Type</option>
                {reportTypes.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              <br />

              <label className="reporttitle">
                <b>Report Title</b>
              </label>
              <br />
              <input
                className="reporttitle2"
                type="text"
                placeholder="Insert Title"
                value={newReporttitle}
                onChange={(e) => setNewReporttitle(e.target.value)}
                required
                disabled={loading}
              />
              <br />

              <label className="receivedform">
                <b>Received From</b>
              </label>
              <br />
              <select
                name="Receivedfrom"
                className="receivedfrom2"
                value={selectedReceivedform}
                onChange={(e) => setSelectedReceievedform(e.target.value)}
                required
                disabled={loading}
              >
                <option value="">Choose Department</option>
                {departments.map((dept) => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
              <br />

              <label className="datecreated">
                <b>Date Created</b>
              </label>
              <br />
              <input
                className="datecreated2"
                type="date"
                placeholder="00/00/0000"
                value={newDatecreated}
                onChange={(e) => setNewDatecreated(e.target.value)}
                required
                disabled={loading}
              />
              <br />

              <label className="assignedto">
                <b>Assigned To:</b>
              </label>
              <br />
              <select
                name="Assigned to"
                className="assignedto2"
                value={selectedAssignedto}
                onChange={(e) => setSelectedAssignedto(e.target.value)}
                required
                disabled={loading}
              >
                <option value="">Choose Department</option>
                {departments.map((dept) => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
              <br />

              <label className="descreport">
                <b>Description</b>
              </label>
              <br />
              <input
                className="descreport2"
                type="text"
                placeholder="Add Description"
                value={newDescriptionreport}
                onChange={(e) => setNewDescriptionreport(e.target.value)}
                required
                disabled={loading}
              />
              <br />

              <button type="submit" className="saverep" disabled={loading}>
                <b>{loading ? "Saving..." : "Save"}</b>
              </button>
              <button type="button" className="editrep" disabled={loading}>
                <b>Edit</b>
              </button>
              <button type="button" className="attachfile" disabled={loading}>
                <b>Attach File</b>
              </button>
              <h1 className="attach2">
                <b>Attachments</b>
              </h1>
            </form>
          )}

          {showReportList && (
            <>
              <h1 className="reportmonitorlist">
                <b>Report Monitoring List</b>
              </h1>
              <div className="report-actions">
                <button onClick={handleBackClick} className="addreport" disabled={loading}>
                  <b>Add Report</b>
                </button>
                <button 
                  onClick={handleRemoveReports} 
                  className="removereport" 
                  disabled={selectedReports.length === 0 || loading}
                >
                  <b>{loading ? "Removing..." : "Remove Report"}</b>
                </button>
                <button 
                  onClick={handleShowGenerateReports} 
                  className="generatereport"
                  disabled={loading}
                >
                  <b>Generate Reports</b>
                </button>
                <button 
                onClick={handleShowProjectForms} 
                className="projectforms"
                disabled={loading}
              >
                <b>Project Forms</b>
              </button>
              </div>
              <div className="replisttable1">
                <table className="replist">
                  <thead>
                    <tr>
                      <th>
                        <input 
                          type="checkbox" 
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedReports([...Array(reportData.length).keys()]);
                            } else {
                              setSelectedReports([]);
                            }
                          }} 
                          checked={selectedReports.length === reportData.length && reportData.length > 0}
                          disabled={loading || reportData.length === 0}
                        />
                      </th>
                      <th>
                        <b>Project ID</b>
                      </th>
                      <th>
                        <b>Internal Project ID</b>
                      </th>
                      <th>
                        <b>Report Type</b>
                      </th>
                      <th>
                        <b>Report Title:</b>
                      </th>
                      <th>
                        <b>Received From:</b>
                      </th>
                      <th>
                        <b>Date Created</b>
                      </th>
                      <th>
                        <b>Assigned to:</b>
                      </th>
                      <th>
                        <b>Description</b>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {reportData.length > 0 ? (
                      reportData.map((item, index) => (
                        <tr key={index} className={selectedReports.includes(index) ? "selected-row" : ""}>
                          <td>
                            <input
                              type="checkbox"
                              checked={selectedReports.includes(index)}
                              onChange={() => handleCheckboxChange(index)}
                              disabled={loading}
                            />
                          </td>
                          <td>
                            <b>{item.project_id}</b>
                          </td>
                          <td>{item.intrnl_project_id}</td>
                          <td>{item.report_type}</td>
                          <td>{item.report_title}</td>
                          <td>{item.received_from}</td>
                          <td>{item.date_created}</td>
                          <td>{item.assigned_to}</td>
                          <td>{item.description}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="9" style={{ textAlign: "center" }}>
                          {apiErrors.reports ? "Could not load reports" : "No reports found"}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
              <div className="selection-info">
                <p>{selectedReports.length} of {reportData.length} reports selected</p>
              </div>
            </>
          )}

          {!showReportList && currentForm !== 1 && (
            <div className="view-reports-container">
              <button 
                onClick={() => setShowReportList(true)} 
                disabled={loading}
                className="view-reports-btn"
              >
                View Report List
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default BodyContent;