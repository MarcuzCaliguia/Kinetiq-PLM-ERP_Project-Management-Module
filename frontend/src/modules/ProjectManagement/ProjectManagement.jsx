// ProjectManagement.jsx with improved API integration, autocomplete, and Project Summary
import React, { useState, useEffect } from "react";
import "./styles/ProjectManagement.css";
import axios from "axios";
import { debounce } from 'lodash'; // You'll need to install lodash: npm install lodash

const BodyContent = () => {
    const [overdueTasks, setOverdueTasks] = useState([]);
    const [todayTasks, setTodayTasks] = useState([]);
    const [dataExternal, setDataExternal] = useState([]);
    const [dataInternal, setDataInternal] = useState([]);
    const [projectSummary, setProjectSummary] = useState([]);
  
    const [selectedNav3, setSelectedNav3] = useState('All3');
    const [selectedNav2, setSelectedNav2] = useState('Internal Project');
    const [showAddProjectForm, setShowAddProjectForm] = useState(false);
    const [selectedNavplan, setSelectedNavplan] = useState("External");
  
    // External project form state
    const [newProjectIDExternal, setNewProjectIDExternal] = useState("");
    const [selectedProjectMilestoneExternal, setSelectedProjectMilestoneExternal] = useState("");
    const [newStartDateExternal, setNewStartDateExternal] = useState("");
    const [newEndDateExternal, setNewEndDateExternal] = useState("");
    const [newProjectIssueExternal, setNewProjectIssueExternal] = useState("");
    const [newProjectWarrantyIDExternal, setNewProjectWarrantyIDExternal] = useState("");
  
    // Internal project form state
    const [newProjectIDInternal, setNewProjectIDInternal] = useState("");
    const [newStartDateInternal, setNewStartDateInternal] = useState("");
    const [newEndDateInternal, setNewEndDateInternal] = useState("");
    const [newProjectIssueInternal, setNewProjectIssueInternal] = useState("");
    const [newProjectRequestIDInternal, setNewProjectRequestIDInternal] = useState("");
    
    // Search results state
    const [externalProjectSearchResults, setExternalProjectSearchResults] = useState([]);
    const [internalProjectSearchResults, setInternalProjectSearchResults] = useState([]);
    const [warrantySearchResults, setWarrantySearchResults] = useState([]);
    const [projectRequestSearchResults, setProjectRequestSearchResults] = useState([]);
    
    // Loading states
    const [isLoading, setIsLoading] = useState({
        overdueTasks: false,
        todayTasks: false,
        externalProjects: false,
        internalProjects: false,
        projectSummary: false
    });
    
    // Error states
    const [errors, setErrors] = useState({
        overdueTasks: null,
        todayTasks: null,
        externalProjects: null,
        internalProjects: null,
        projectSummary: null
    });
  
    // Fetch data on component mount
    useEffect(() => {
        fetchOverdueTasks();
        fetchTodayTasks();
        fetchExternalProjects();
        fetchInternalProjects();
        fetchProjectSummary();
    }, []);
  
    const fetchInitialExternalProjects = async () => {
      try {
          const response = await axios.get('/api/search-external-project/');
          setExternalProjectSearchResults(response.data);
      } catch (error) {
          console.error("Error fetching initial external projects:", error);
      }
  };
  
  const fetchInitialInternalProjects = async () => {
      try {
          const response = await axios.get('/api/search-internal-project/');
          setInternalProjectSearchResults(response.data);
      } catch (error) {
          console.error("Error fetching initial internal projects:", error);
      }
  };
  
  const fetchInitialWarranties = async () => {
      try {
          const response = await axios.get('/api/search-warranty/');
          setWarrantySearchResults(response.data);
      } catch (error) {
          console.error("Error fetching initial warranties:", error);
      }
  };
  
  const fetchInitialProjectRequests = async () => {
      try {
          const response = await axios.get('/api/search-project-request/');
          setProjectRequestSearchResults(response.data);
      } catch (error) {
          console.error("Error fetching initial project requests:", error);
      }
  };

    const fetchOverdueTasks = async () => {
        setIsLoading(prev => ({ ...prev, overdueTasks: true }));
        try {
            const response = await axios.get('/api/overdue-tasks/');
            setOverdueTasks(response.data);
            setErrors(prev => ({ ...prev, overdueTasks: null }));
        } catch (error) {
            console.error("Error fetching overdue tasks:", error);
            setErrors(prev => ({ ...prev, overdueTasks: "Failed to load overdue tasks" }));
        } finally {
            setIsLoading(prev => ({ ...prev, overdueTasks: false }));
        }
    };
  
    const fetchTodayTasks = async () => {
        setIsLoading(prev => ({ ...prev, todayTasks: true }));
        try {
            const response = await axios.get('/api/today-tasks/');
            setTodayTasks(response.data);
            setErrors(prev => ({ ...prev, todayTasks: null }));
        } catch (error) {
            console.error("Error fetching today's tasks:", error);
            setErrors(prev => ({ ...prev, todayTasks: "Failed to load today's tasks" }));
        } finally {
            setIsLoading(prev => ({ ...prev, todayTasks: false }));
        }
    };
  
    const fetchExternalProjects = async () => {
        setIsLoading(prev => ({ ...prev, externalProjects: true }));
        try {
            const response = await axios.get('/api/external-projects/');
            setDataExternal(response.data);
            setErrors(prev => ({ ...prev, externalProjects: null }));
        } catch (error) {
            console.error("Error fetching external projects:", error);
            setErrors(prev => ({ ...prev, externalProjects: "Failed to load external projects" }));
        } finally {
            setIsLoading(prev => ({ ...prev, externalProjects: false }));
        }
    };
  
    const fetchInternalProjects = async () => {
        setIsLoading(prev => ({ ...prev, internalProjects: true }));
        try {
            const response = await axios.get('/api/internal-projects/');
            setDataInternal(response.data);
            setErrors(prev => ({ ...prev, internalProjects: null }));
        } finally {
            setIsLoading(prev => ({ ...prev, internalProjects: false }));
        }
    };
    
    const fetchProjectSummary = async () => {
      setIsLoading(prev => ({ ...prev, projectSummary: true }));
      try {
          const response = await axios.get('/api/project-summary/');
          console.log("Project summary data:", response.data); // Add this for debugging
          setProjectSummary(response.data);
          setErrors(prev => ({ ...prev, projectSummary: null }));
      } catch (error) {
          console.error("Error fetching project summary:", error);
          setErrors(prev => ({ ...prev, projectSummary: "Failed to load project summary" }));
      } finally {
          setIsLoading(prev => ({ ...prev, projectSummary: false }));
      }
  };
  
    
    // Debounced search functions
    const searchExternalProjects = debounce(async (query) => {
        if (!query) {
            setExternalProjectSearchResults([]);
            return;
        }
        
        try {
            const response = await axios.get(`/api/search-external-project/?query=${query}`);
            setExternalProjectSearchResults(response.data);
        } catch (error) {
            console.error("Error searching external projects:", error);
            setExternalProjectSearchResults([]);
        }
    }, 300);
    
    const searchInternalProjects = debounce(async (query) => {
        if (!query) {
            setInternalProjectSearchResults([]);
            return;
        }
        
        try {
            const response = await axios.get(`/api/search-internal-project/?query=${query}`);
            setInternalProjectSearchResults(response.data);
        } catch (error) {
            console.error("Error searching internal projects:", error);
            setInternalProjectSearchResults([]);
        }
    }, 300);
    
    const searchWarranties = debounce(async (query) => {
        if (!query) {
            setWarrantySearchResults([]);
            return;
        }
        
        try {
            const response = await axios.get(`/api/search-warranty/?query=${query}`);
            setWarrantySearchResults(response.data);
        } catch (error) {
            console.error("Error searching warranties:", error);
            setWarrantySearchResults([]);
        }
    }, 300);
    
    const searchProjectRequests = debounce(async (query) => {
        if (!query) {
            setProjectRequestSearchResults([]);
            return;
        }
        
        try {
            const response = await axios.get(`/api/search-project-request/?query=${query}`);
            setProjectRequestSearchResults(response.data);
        } catch (error) {
            console.error("Error searching project requests:", error);
            setProjectRequestSearchResults([]);
        }
    }, 300);
  
const handleNavClickdash = (nav) => {
    setSelectedNavplan(nav);
    
    if (nav === "External") {
        fetchInitialExternalProjects();
        fetchInitialWarranties();
    } else {
        fetchInitialInternalProjects();
        fetchInitialProjectRequests();
    }
};

  
    const handleNavClick = (navItem) => {
        setSelectedNav2(navItem);
    };
  
    const handleNavClick2 = (navItem) => {
        setSelectedNav3(navItem);
    };
  
    const handleAddProjectClick = () => {
      setShowAddProjectForm(true);
      
      // Fetch initial data for the forms
      if (selectedNavplan === "External") {
          fetchInitialExternalProjects();
          fetchInitialWarranties();
      } else {
          fetchInitialInternalProjects();
          fetchInitialProjectRequests();
      }
  };
  
    const handleAddExternalProject = async (e) => {
        e.preventDefault();
        try {
            const projectData = {
                project_id: newProjectIDExternal,
                project_milestone: selectedProjectMilestoneExternal,
                start_date: newStartDateExternal,
                estimated_end_date: newEndDateExternal,
                project_warranty_id: newProjectWarrantyIDExternal,
                project_issue: newProjectIssueExternal
            };
            
            await axios.post('/api/create-external-project/', projectData);
            await fetchExternalProjects(); // Refresh the list after adding
            await fetchProjectSummary(); // Also refresh the summary
            setShowAddProjectForm(false);
            resetExternalForm();
        } catch (error) {
            console.error("Error creating external project:", error);
            alert("Failed to create external project. Please try again.");
        }
    };
  
    const handleAddInternalProject = async (e) => {
        e.preventDefault();
        try {
            const projectData = {
                project_id: newProjectIDInternal,
                start_date: newStartDateInternal,
                estimated_end_date: newEndDateInternal,
                project_issue: newProjectIssueInternal,
                project_request_id: newProjectRequestIDInternal
            };
            
            await axios.post('/api/create-internal-project/', projectData);
            await fetchInternalProjects(); // Refresh the list after adding
            await fetchProjectSummary(); // Also refresh the summary
            setShowAddProjectForm(false);
            resetInternalForm();
        } catch (error) {
            console.error("Error creating internal project:", error);
            alert("Failed to create internal project. Please try again.");
        }
    };
  
    const resetExternalForm = () => {
        setNewProjectIDExternal("");
        setSelectedProjectMilestoneExternal("");
        setNewStartDateExternal("");
        setNewEndDateExternal("");
        setNewProjectWarrantyIDExternal("");
        setNewProjectIssueExternal("");
        setExternalProjectSearchResults([]);
        setWarrantySearchResults([]);
    };
  
    const resetInternalForm = () => {
        setNewProjectIDInternal("");
        setNewStartDateInternal("");
        setNewEndDateInternal("");
        setNewProjectIssueInternal("");
        setNewProjectRequestIDInternal("");
        setInternalProjectSearchResults([]);
        setProjectRequestSearchResults([]);
    };
  
    const handleCancelAddProject = () => {
        setShowAddProjectForm(false);
        resetExternalForm();
        resetInternalForm();
    };
    
    // Handle project ID search input
    const handleExternalProjectIDChange = (e) => {
        const value = e.target.value;
        setNewProjectIDExternal(value);
        searchExternalProjects(value);
    };
    
    const handleInternalProjectIDChange = (e) => {
        const value = e.target.value;
        setNewProjectIDInternal(value);
        searchInternalProjects(value);
    };
    
    // Handle warranty ID search input
    const handleWarrantyIDChange = (e) => {
        const value = e.target.value;
        setNewProjectWarrantyIDExternal(value);
        searchWarranties(value);
    };
    
    // Handle project request ID search input
    const handleProjectRequestIDChange = (e) => {
        const value = e.target.value;
        setNewProjectRequestIDInternal(value);
        searchProjectRequests(value);
    };
    
    // Select a project from search results
    const selectExternalProject = (project) => {
        setNewProjectIDExternal(project.project_id);
        setExternalProjectSearchResults([]);
    };
    
    const selectInternalProject = (project) => {
        setNewProjectIDInternal(project.intrnl_project_id);
        setInternalProjectSearchResults([]);
    };
    
    // Select a warranty from search results
    const selectWarranty = (warranty) => {
        setNewProjectWarrantyIDExternal(warranty.id);
        setWarrantySearchResults([]);
    };
    
    // Select a project request from search results
    const selectProjectRequest = (request) => {
        setNewProjectRequestIDInternal(request.project_request_id);
        setProjectRequestSearchResults([]);
    };
  
    return (
        <div className="body-content-container">
            {!showAddProjectForm ? (
                <>
                    <h1 className="overview"><b>Overview</b></h1>
                    <h2 className="overdue1"><b>Overdue Task</b></h2>
                    <h2 className="tft"><b>Tasks for Today</b></h2>
                    <h2 className="projsum"><b>Project Summary</b></h2>
                    <div className="rectangle"></div>
                    <div className="rectangle2"></div>
                    <div className="rectangle3"></div>
                    <button className="add"><b>New task</b></button>
  
                    <div className="scroll">
                        <table className="tb">
                            <thead>
                                <tr>
                                    <th><b>Overdue</b></th>
                                    <th><b>Task</b></th>
                                    <th><b>Deadline</b></th>
                                    <th><b>Employee</b></th>
                                </tr>
                            </thead>
                            <tbody>
                                {isLoading.overdueTasks ? (
                                    <tr><td colSpan="4">Loading...</td></tr>
                                ) : errors.overdueTasks ? (
                                    <tr><td colSpan="4">Error: {errors.overdueTasks}</td></tr>
                                ) : overdueTasks.length === 0 ? (
                                    <tr><td colSpan="4">No overdue tasks</td></tr>
                                ) : (
                                    overdueTasks.map((item, index) => (
                                        <tr key={index}>
                                            <td className="due"><b>{item.Overdue}</b></td>
                                            <td>{item.Task}</td>
                                            <td>{item.Deadline}</td>
                                            <td>{item.Employee}</td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                    
                    {/* Project Summary Section */}
                    <div className="project-summary-container">
                        <div className="project-summary-scroll">
                            <table className="project-summary-table">
                                <thead>
                                    <tr>
                                        <th><b>ID</b></th>
                                        <th><b>Project ID</b></th>
                                        <th><b>Type</b></th>
                                        <th><b>Start Date</b></th>
                                        <th><b>End Date</b></th>
                                        <th><b>Status</b></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {isLoading.projectSummary ? (
                                        <tr><td colSpan="6">Loading...</td></tr>
                                    ) : errors.projectSummary ? (
                                        <tr><td colSpan="6">Error: {errors.projectSummary}</td></tr>
                                    ) : projectSummary.length === 0 ? (
                                        <tr><td colSpan="6">No projects found</td></tr>
                                    ) : (
                                        projectSummary.map((project, index) => (
                                            <tr key={index}>
                                                <td>{project.id}</td>
                                                <td><b>{project.projectId}</b></td>
                                                <td>{project.type}</td>
                                                <td>{project.startDate}</td>
                                                <td>{project.endDate}</td>
                                                <td>
                                                    {project.issue ? 
                                                        <span className="status-issue">Has Issues</span> : 
                                                        <span className="status-ok">On Track</span>
                                                    }
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <div>
                        <div className="top-nav2">
                            <button
                                className={`nav-button ${selectedNav2 === "Internal Project" ? "selected2" : ""}`}
                                onClick={() => handleNavClick("Internal Project")}
                            >
                                <b>Internal Project</b>
                            </button>
                            <button
                                className={`nav-button ${selectedNav2 === "External Project" ? "selected2" : ""}`}
                                onClick={() => handleNavClick("External Project")}
                            >
                                <b>External Project</b>
                            </button>
                        </div>
                        <button className="AddProject" onClick={handleAddProjectClick}><b>Add Project</b></button>
                    </div>
  
                    <div className="dashtable">
                        {selectedNav2 === "External Project" && (
                            <table className="dashtable3">
                                <thead>
                                    <tr>
                                        <th><b>Project Tracking ID</b></th>
                                        <th><b>Project ID</b></th>
                                        <th><b>Project Milestone</b></th>
                                        <th><b>Start Date</b></th>
                                        <th><b>Est. End Date</b></th>
                                        <th><b>Project Warranty ID</b></th>
                                        <th><b>Project Issue</b></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {isLoading.externalProjects ? (
                                        <tr><td colSpan="7">Loading...</td></tr>
                                    ) : errors.externalProjects ? (
                                        <tr><td colSpan="7">Error: {errors.externalProjects}</td></tr>
                                    ) : dataExternal.length === 0 ? (
                                        <tr><td colSpan="7">No external projects</td></tr>
                                    ) : (
                                        dataExternal.map((item, index) => (
                                            <tr key={index}>
                                                <td>{item.ProjectTrackingID}</td>
                                                <td><b>{item.ProjectID}</b></td>
                                                <td>{item.ProjectMilestone}</td>
                                                <td>{item.StartDate}</td>
                                                <td>{item.EstimatedEndDate}</td>
                                                <td>{item.ProjectWarrantyStatus}</td>
                                                <td>{item.ProjectIssue}</td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        )}
                    </div>
  
                    <div className="dashtableinternal">
                        {selectedNav2 === "Internal Project" && (
                            <table className="dashtableinternal2">
                                <thead>
                                    <tr>
                                        <th><b>Project Tracking ID</b></th>
                                        <th><b>Project ID</b></th>
                                        <th><b>Start Date</b></th>
                                        <th><b>Est. End Date</b></th>
                                        <th><b>Project Issue</b></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {isLoading.internalProjects ? (
                                        <tr><td colSpan="5">Loading...</td></tr>
                                    ) : errors.internalProjects ? (
                                        <tr><td colSpan="5">Error: {errors.internalProjects}</td></tr>
                                    ) : dataInternal.length === 0 ? (
                                        <tr><td colSpan="5">No internal projects</td></tr>
                                    ) : (
                                        dataInternal.map((item, index) => (
                                            <tr key={index}>
                                                <td>{item.ProjectTrackingID}</td>
                                                <td><b>{item.ProjectID}</b></td>
                                                <td>{item.StartDate}</td>
                                                <td>{item.EstimatedEndDate}</td>
                                                <td>{item.ProjectIssue}</td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        )}
                    </div>
  
                    <div className="scroll2">
                        <table className="tb2">
                            <thead>
                                <tr>
                                    <th
                                        className={`nav-button2 ${selectedNav3 === 'All3' ? 'selected3' : ''}`}
                                        onClick={() => handleNavClick2('All3')}
                                    >
                                        <b>All</b>
                                        {selectedNav3 === 'All3' && (
                                            <div className="tasklist">
                                                <form>
                                                    {isLoading.todayTasks ? (
                                                        <div>Loading...</div>
                                                    ) : errors.todayTasks ? (
                                                        <div>Error: {errors.todayTasks}</div>
                                                    ) : todayTasks.length === 0 ? (
                                                        <div>No tasks for today</div>
                                                    ) : (
                                                        todayTasks.map((task, index) => (
                                                            <div key={index}>
                                                                <input type="checkbox" id={`task-${index}`} name={`task-${index}`} />
                                                                <label htmlFor={`task-${index}`}>{task.Task}</label>
                                                                <br />
                                                            </div>
                                                        ))
                                                    )}
                                                </form>
                                            </div>
                                        )}
                                    </th>
                                    <th
                                        className={`nav-button2 ${selectedNav3 === 'Important' ? 'selected3' : ''}`}
                                        onClick={() => handleNavClick2('Important')}
                                    >
                                        <b>Important</b>
                                        {selectedNav3 === 'Important' && (
                                            <div className="tasklist2">
                                                <form>
                                                    <input type="checkbox" id="docu6" name="docu6" value="documents6" />
                                                    <label htmlFor="docu6">None</label>
                                                    <br />
                                                    <input type="checkbox" id="docu7" name="docu7" value="documents7" />
                                                    <label htmlFor="docu7">None</label>
                                                    <br />
                                                    <input type="checkbox" id="docu8" name="docu8" value="documents8" />
                                                    <label htmlFor="docu8">None</label>
                                                    <br />
                                                    <input type="checkbox" id="docu9" name="docu9" value="documents9" />
                                                    <label htmlFor="docu9">None</label>
                                                    <br />
                                                </form>
                                            </div>
                                        )}
                                    </th>
                                    <th
                                        className={`nav-button2 ${selectedNav3 === 'Notes' ? 'selected3' : ''}`}
                                        onClick={() => handleNavClick2('Notes')}
                                    >
                                        <b>Notes</b>
                                        {selectedNav3 === 'Notes' && (
                                            <div className="tasklist3">
                                                <form>
                                                    <input type="checkbox" id="docu10" name="docu10" value="documents10" />
                                                    <label htmlFor="docu10">Notes</label>
                                                    <br />
                                                    <input type="checkbox" id="docu11" name="docu11" value="documents11" />
                                                    <label htmlFor="docu11">Notes</label>
                                                    <br />
                                                    <input type="checkbox" id="docu12" name="docu12" value="documents12" />
                                                    <label htmlFor="docu12">Notes</label>
                                                    <br />
                                                    <input type="checkbox" id="docu13" name="docu13" value="documents13" />
                                                    <label htmlFor="docu13">Notes</label>
                                                    <br />
                                                </form>
                                            </div>
                                        )}
                                    </th>
                                    <th
                                        className={`nav-button2 ${selectedNav3 === 'Links' ? 'selected3' : ''}`}
                                        onClick={() => handleNavClick2('Links')}
                                    >
                                        <b>Links</b>
                                    </th>
                                </tr>
                            </thead>
                        </table>
                    </div>
                    <div className="top-nav-container">
                        <div id="linedashboard"></div>
                    </div>
                </>
            ) : (
                <div className="add-project-form">
                    <div className="addprojectnav">
                        <button
                            className={`nav-button ${selectedNavplan === "Internal" ? "selected1" : ""}`}
                            onClick={() => handleNavClickdash("Internal")}
                        >
                            <b>Internal</b>
                        </button>
                        <button
                            className={`nav-button ${selectedNavplan === "External" ? "selected1" : ""}`}
                            onClick={() => handleNavClickdash("External")}
                        >
                            <b>External</b>
                        </button>
                    </div>
                    <h2 className='addprojectnew'><b>New Project Plan</b></h2>
                    <h2 className='projectracking'>Project Tracking</h2>
                    {selectedNavplan === "External" && (
    <>
        <form onSubmit={handleAddExternalProject} className="project-form">
            <div className="form-row">
                <div className="form-column">
                    <label className="form-label">
                        <b>Project ID*</b>
                    </label>
                    <div className="search-container">
                        <input className="form-input"
                            type="text"
                            placeholder="Name"
                            value={newProjectIDExternal}
                            onChange={handleExternalProjectIDChange}
                            onFocus={() => fetchInitialExternalProjects()}
                            required
                        />
                        {externalProjectSearchResults.length > 0 && (
                            <div className="search-results">
                                {externalProjectSearchResults.map((project, index) => (
                                    <div 
                                        key={index} 
                                        className="search-result-item"
                                        onClick={() => selectExternalProject(project)}
                                    >
                                        {project.project_id}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                    
                    <label className="form-label">
                        <b>Project Milestone</b>
                    </label>
                    <select
                        className="form-input"
                        value={selectedProjectMilestoneExternal}
                        onChange={(e) => setSelectedProjectMilestoneExternal(e.target.value)}
                        required
                    >
                        <option value="">Choose Project Milestone</option>
                        <option value="Project Initiation Completed">Project Initiation Completed</option>
                        <option value="Project Initiation Ongoing">Project Initiation Ongoing</option>
                        <option value="Project Initiation Rejected">Project Initiation Rejected</option>
                    </select>
                    
                    <label className="form-label">
                        <b>Start Date</b>
                    </label>
                    <input
                        className="form-input"
                        type="date"
                        value={newStartDateExternal}
                        onChange={(e) => setNewStartDateExternal(e.target.value)}
                        required
                    />
                    
                    <label className="form-label">
                        <b>Est. End Date</b>
                    </label>
                    <input
                        className="form-input"
                        type="date"
                        value={newEndDateExternal}
                        onChange={(e) => setNewEndDateExternal(e.target.value)}
                        required
                    />
                    
                    <label className="form-label">
                        <b>Project Warranty ID</b>
                    </label>
                    <div className="search-container">
                        <input
                            className="form-input"
                            type="text"
                            placeholder="Insert Warranty ID"
                            value={newProjectWarrantyIDExternal}
                            onChange={handleWarrantyIDChange}
                            onFocus={() => fetchInitialWarranties()}
                        />
                        {warrantySearchResults.length > 0 && (
                            <div className="search-results">
                                {warrantySearchResults.map((warranty, index) => (
                                    <div 
                                        key={index} 
                                        className="search-result-item"
                                        onClick={() => selectWarranty(warranty)}
                                    >
                                        {warranty.id} - {warranty.coverage_years} years
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
                
                <div className="form-column">
                    <label className="form-label">
                        <b>Project Issue</b>
                    </label>
                    <textarea
                        className="form-textarea"
                        placeholder="Add Project Issue:"
                        value={newProjectIssueExternal}
                        onChange={(e) => setNewProjectIssueExternal(e.target.value)}
                        rows="10"
                    />
                </div>
            </div>
            
            <div className="form-actions">
                <button type="button" className="cancel-button" onClick={handleCancelAddProject}>
                    <b>Cancel</b>
                </button>
                <button type="submit" className="save-button">
                    <b>Save</b>
                </button>
            </div>
        </form>
    </>
)}
  
  {selectedNavplan === "Internal" && (
    <>
        <form onSubmit={handleAddInternalProject} className="project-form">
            <div className="form-row">
                <div className="form-column">
                    <label className="form-label">
                        <b>Project ID*</b>
                    </label>
                    <div className="search-container">
                        <input className="form-input"
                            type="text"
                            placeholder="Name"
                            value={newProjectIDInternal}
                            onChange={handleInternalProjectIDChange}
                            onFocus={() => fetchInitialInternalProjects()}
                            required
                        />
                        {internalProjectSearchResults.length > 0 && (
                            <div className="search-results">
                                {internalProjectSearchResults.map((project, index) => (
                                    <div 
                                        key={index} 
                                        className="search-result-item"
                                        onClick={() => selectInternalProject(project)}
                                    >
                                        {project.intrnl_project_id}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                    
                    <label className="form-label">
                        <b>Project Request ID</b>
                    </label>
                    <div className="search-container">
                        <input
                            className="form-input"
                            type="text"
                            placeholder="Insert Project Request ID"
                            value={newProjectRequestIDInternal}
                            onChange={handleProjectRequestIDChange}
                            onFocus={() => fetchInitialProjectRequests()}
                        />
                        {projectRequestSearchResults.length > 0 && (
                            <div className="search-results">
                                {projectRequestSearchResults.map((request, index) => (
                                    <div 
                                        key={index} 
                                        className="search-result-item"
                                        onClick={() => selectProjectRequest(request)}
                                    >
                                        {request.project_request_id} - {request.project_name}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                    
                    <label className="form-label">
                        <b>Start Date</b>
                    </label>
                    <input
                        className="form-input"
                        type="date"
                        value={newStartDateInternal}
                        onChange={(e) => setNewStartDateInternal(e.target.value)}
                        required
                    />
                    
                    <label className="form-label">
                        <b>Est. End Date</b>
                    </label>
                    <input
                        className="form-input"
                        type="date"
                        value={newEndDateInternal}
                        onChange={(e) => setNewEndDateInternal(e.target.value)}
                        required
                    />
                </div>
                
                <div className="form-column">
                    <label className="form-label">
                        <b>Project Issue</b>
                    </label>
                    <textarea
                        className="form-textarea"
                        placeholder="Add Project Issue:"
                        value={newProjectIssueInternal}
                        onChange={(e) => setNewProjectIssueInternal(e.target.value)}
                        rows="10"
                    />
                </div>
            </div>
            
            <div className="form-actions">
                <button type="button" className="cancel-button" onClick={handleCancelAddProject}>
                    <b>Cancel</b>
                </button>
                <button type="submit" className="save-button">
                    <b>Save</b>
                </button>
            </div>
        </form>
    </>
)}
                </div>
            )}
        </div>
    );
};
  
export default BodyContent;