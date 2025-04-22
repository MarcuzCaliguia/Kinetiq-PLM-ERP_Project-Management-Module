import React, { useState, useEffect } from "react";
import "./styles/ProjectManagement.css";
import axios from "axios";

const BodyContent = () => {
    const [overdueTasks, setOverdueTasks] = useState([]);
    const [todayTasks, setTodayTasks] = useState([]);
    const [projectSummary, setProjectSummary] = useState([]);
  
    const [selectedNav3, setSelectedNav3] = useState('All3');
    const [selectedNav2, setSelectedNav2] = useState('Internal Project');
    
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
  
    const handleNavClick2 = (navItem) => {
        setSelectedNav3(navItem);
    };
  
    return (
        <div className="project-management-container">
            <div className="dashboard-view">
                {/* Header Section */}
                <div className="dashboard-header">
                    <h1 className="dashboard-title">Project Overview</h1>
                    {/* New Task button removed */}
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
                            <div className="task-tabs">
                                <button
                                    className={`task-tab ${selectedNav3 === 'All3' ? 'active' : ''}`}
                                    onClick={() => handleNavClick2('All3')}
                                >
                                    All
                                </button>
                                <button
                                    className={`task-tab ${selectedNav3 === 'Important' ? 'active' : ''}`}
                                    onClick={() => handleNavClick2('Important')}
                                >
                                    Important
                                </button>
                                <button
                                    className={`task-tab ${selectedNav3 === 'Notes' ? 'active' : ''}`}
                                    onClick={() => handleNavClick2('Notes')}
                                >
                                    Notes
                                </button>
                                <button
                                    className={`task-tab ${selectedNav3 === 'Links' ? 'active' : ''}`}
                                    onClick={() => handleNavClick2('Links')}
                                >
                                    Links
                                </button>
                            </div>

                            {selectedNav3 === 'All3' && (
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
                            )}
                        </div>
                    </div>

                    {/* Project Summary Section */}
                    <div className="dashboard-section project-summary-section">
                        <div className="section-header">
                            <h2>Project Summary</h2>
                        </div>
                        <div className="section-content">
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
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
                                    ) : projectSummary.length === 0 ? (
                                        <tr><td colSpan="6" className="no-data-cell">No projects found</td></tr>
                                    ) : (
                                        projectSummary.map((project, index) => (
                                            <tr key={index} className={project.issue ? "has-issue" : ""}>
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
        </div>
    );
};

export default BodyContent;