import React, { useState, useEffect } from "react";
import "./styles/ProjectManagement.css";
import axios from "axios";

const BodyContent = () => {
    const [selectedProject, setSelectedProject] = useState(null);
    const [projectDetail, setProjectDetail] = useState(null);
    const [showDetailsModal, setShowDetailsModal] = useState(false);
    const [overdueTasks, setOverdueTasks] = useState([]);
    const [todayTasks, setTodayTasks] = useState([]);
    const [projectSummary, setProjectSummary] = useState([]);
    const [isLoadingDetail, setIsLoadingDetail] = useState(false);
    const [detailError, setDetailError] = useState(null);
  
    const [selectedProjectType, setSelectedProjectType] = useState('All');
    
    // Loading states
    const [isLoading, setIsLoading] = useState({
        overdueTasks: false,
        todayTasks: false,
        projectSummary: false
    });
    
    // Error states
    const [errors, setErrors] = useState({
        overdueTasks: null,
        todayTasks: null,
        projectSummary: null
    });
  
    // Fetch data on component mount
    useEffect(() => {
        fetchOverdueTasks();
        fetchTodayTasks();
        fetchProjectSummary();
    }, []);

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
    
    const fetchProjectSummary = async () => {
      setIsLoading(prev => ({ ...prev, projectSummary: true }));
      try {
          const response = await axios.get('/api/project-summary/');
          console.log("Project summary data:", response.data);
          setProjectSummary(response.data);
          setErrors(prev => ({ ...prev, projectSummary: null }));
      } catch (error) {
          console.error("Error fetching project summary:", error);
          setErrors(prev => ({ ...prev, projectSummary: "Failed to load project summary" }));
      } finally {
          setIsLoading(prev => ({ ...prev, projectSummary: false }));
      }
    };
  
    const fetchProjectDetail = async (project) => {
        setIsLoadingDetail(true);
        setDetailError(null);
        
        try {
            const response = await axios.get(`/api/project-detail/${project.type}/${project.id}/`);
            setProjectDetail(response.data);
        } catch (error) {
            console.error("Error fetching project details:", error);
            setDetailError(error.response?.data?.error || "Failed to load project details");
        } finally {
            setIsLoadingDetail(false);
        }
    };
    
    const handleProjectRowClick = (project) => {
        setSelectedProject(project);
        fetchProjectDetail(project);
        setShowDetailsModal(true);
    };

    const closeDetailsModal = () => {
        setShowDetailsModal(false);
        setProjectDetail(null);
    };

    const filteredProjects = projectSummary.filter(project => 
        selectedProjectType === 'All' || project.type === selectedProjectType
    );
    
    return (
        <div className="project-management-container">
            <div className="dashboard-view">
                {/* Header Section */}
                <div className="dashboard-header">
                    <h1 className="dashboard-title">Project Overview</h1>
                </div>

                {/* Main Dashboard Sections */}
                <div className="dashboard-sections">
                    {/* Overdue Tasks Section */}
                    <div className="dashboard-section overdue-tasks-section">
                        <div className="section-header">
                            <h2>Overdue Tasks</h2>
                        </div>
                        <div className="section-content">
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Overdue</th>
                                        <th>Task</th>
                                        <th>Deadline</th>
                                        <th>Employee</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {isLoading.overdueTasks ? (
                                        <tr><td colSpan="4" className="loading-cell">Loading...</td></tr>
                                    ) : errors.overdueTasks ? (
                                        <tr><td colSpan="4" className="error-cell">Error: {errors.overdueTasks}</td></tr>
                                    ) : overdueTasks.length === 0 ? (
                                        <tr><td colSpan="4" className="no-data-cell">No overdue tasks</td></tr>
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
                    </div>

                    {/* Today's Tasks Section */}
                    <div className="dashboard-section todays-tasks-section">
                        <div className="section-header">
                            <h2>Today's Tasks</h2>
                        </div>
                        <div className="section-content">
                            <div className="task-list-container">
                                {isLoading.todayTasks ? (
                                    <div className="loading-cell">Loading...</div>
                                ) : errors.todayTasks ? (
                                    <div className="error-cell">Error: {errors.todayTasks}</div>
                                ) : todayTasks.length === 0 ? (
                                    <div className="no-data-cell">No tasks for today</div>
                                ) : (
                                    <form className="task-list-form">
                                        {todayTasks.map((task, index) => (
                                            <div key={index} className="task-item">
                                                <input 
                                                    type="checkbox" 
                                                    id={`task-${index}`} 
                                                    name={`task-${index}`} 
                                                />
                                                <label htmlFor={`task-${index}`}>{task.Task}</label>
                                            </div>
                                        ))}
                                    </form>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Project Summary Section */}
                    <div className="dashboard-section project-summary-section">
                        <div className="section-header">
                            <h2>Project Summary</h2>
                            <div className="project-type-tabs">
                                <button
                                    className={`project-tab ${selectedProjectType === 'All' ? 'active' : ''}`}
                                    onClick={() => setSelectedProjectType('All')}
                                >
                                    All Projects
                                </button>
                                <button
                                    className={`project-tab ${selectedProjectType === 'Internal' ? 'active' : ''}`}
                                    onClick={() => setSelectedProjectType('Internal')}
                                >
                                    Internal
                                </button>
                                <button
                                    className={`project-tab ${selectedProjectType === 'External' ? 'active' : ''}`}
                                    onClick={() => setSelectedProjectType('External')}
                                >
                                    External
                                </button>
                            </div>
                        </div>
                        <div className="section-content">
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Project Tracking ID</th>
                                        <th>Project ID</th>
                                        <th>Type</th>
                                        <th>Start Date</th>
                                        <th>End Date</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {isLoading.projectSummary ? (
                                        <tr><td colSpan="6" className="loading-cell">Loading...</td></tr>
                                    ) : errors.projectSummary ? (
                                        <tr><td colSpan="6" className="error-cell">Error: {errors.projectSummary}</td></tr>
                                    ) : filteredProjects.length === 0 ? (
                                        <tr><td colSpan="6" className="no-data-cell">No projects found</td></tr>
                                    ) : (
                                        filteredProjects.map((project, index) => (
                                            <tr 
                                                key={index} 
                                                className={`${project.issue ? "has-issue" : ""} clickable-row`}
                                                onClick={() => handleProjectRowClick(project)}
                                            >
                                                <td>{project.id}</td>
                                                <td><b>{project.projectId}</b></td>
                                                <td>{project.type}</td>
                                                <td>{project.startDate}</td>
                                                <td>{project.endDate}</td>
                                                <td>
                                                    {project.issue ? 
                                                        <span className="status-badge issue">Has Issues</span> : 
                                                        <span className="status-badge ok">On Track</span>
                                                    }
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            {showDetailsModal && selectedProject && (
    <div className="project-details-modal">
        <div className="modal-content">
            <div className="modal-header">
                <h2>Project Details</h2>
                <button className="close-button" onClick={closeDetailsModal}>×</button>
            </div>
            <div className="modal-body">
                {isLoadingDetail ? (
                    <div className="loading-cell">Loading project details...</div>
                ) : detailError ? (
                    <div className="error-cell">Error: {detailError}</div>
                ) : projectDetail ? (
                    <div className="project-details-grid">
                        {/* External Project */}
                        {selectedProject.type === 'External' && (
                            <>
                                <div className="detail-item">
                                    <span className="detail-label">Project Tracking ID:</span>
                                    <span className="detail-value">{projectDetail.project_tracking_id}</span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">Project ID:</span>
                                    <span className="detail-value">{projectDetail.project_id}</span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">Project Type:</span>
                                    <span className="detail-value">External</span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">Start Date:</span>
                                    <span className="detail-value">{projectDetail.start_date}</span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">Estimated End Date:</span>
                                    <span className="detail-value">{projectDetail.estimated_end_date}</span>
                                </div>
                                <div className="detail-item full-width">
                                    <span className="detail-label">Project Milestone:</span>
                                    <span className="detail-value">{projectDetail.project_milestone}</span>
                                </div>
                                {projectDetail.project_warranty_id && (
                                    <div className="detail-item">
                                        <span className="detail-label">Project Warranty ID:</span>
                                        <span className="detail-value">{projectDetail.project_warranty_id}</span>
                                    </div>
                                )}
                                {projectDetail.project_issue && (
                                    <div className="detail-item full-width">
                                        <span className="detail-label">Project Issue:</span>
                                        <span className="detail-value">{projectDetail.project_issue}</span>
                                    </div>
                                )}
                            </>
                        )}

                                    {/* Internal Project */}
{selectedProject.type === 'Internal' && (
    <>
        <div className="detail-item">
            <span className="detail-label">Project Tracking ID:</span>
            <span className="detail-value">{projectDetail.intrnl_project_tracking_id}</span>
        </div>
        <div className="detail-item">
            <span className="detail-label">Project ID:</span>
            <span className="detail-value">{projectDetail.intrnl_project_id}</span>
        </div>
        <div className="detail-item">
            <span className="detail-label">Project Type:</span>
            <span className="detail-value">Internal</span>
        </div>
        <div className="detail-item">
            <span className="detail-label">Start Date:</span>
            <span className="detail-value">{projectDetail.intrnl_start_date}</span>
        </div>
        <div className="detail-item">
            <span className="detail-label">Estimated End Date:</span>
            <span className="detail-value">{projectDetail.intrnl_estimated_end_date}</span>
        </div>
        {projectDetail.intrnl_project_issue && (
            <div className="detail-item full-width">
                <span className="detail-label">Project Issue:</span>
                <span className="detail-value">{projectDetail.intrnl_project_issue}</span>
            </div>
        )}
    </>
)}
                                </div>
                            ) : (
                                <div className="no-data-cell">No detailed information available for this project.</div>
                            )}
                        </div>
                        <div className="modal-footer">
                            <button className="cancel-btn" onClick={closeDetailsModal}>Close</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default BodyContent;