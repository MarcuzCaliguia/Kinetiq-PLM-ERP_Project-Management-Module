import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "../styles/Warranties.css";

const BodyContent = () => {
  const [warranties, setWarranties] = useState([]);
  const [selectedWarranties, setSelectedWarranties] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newWarranty, setNewWarranty] = useState({
    project_id: "",
    warranty_coverage_yr: "1",
    warranty_start_date: "",
    warranty_end_date: ""
  });
  const [error, setError] = useState("");
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null
  });
  
  const [projectSuggestions, setProjectSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const suggestionRef = useRef(null);
  const formRef = useRef(null);

  useEffect(() => {
    fetchWarranties();
    
    // Load project suggestions when the form is shown
    if (showAddForm) {
      fetchProjectSuggestions("PROJ");
    }
    
    const handleClickOutside = (event) => {
      if (suggestionRef.current && !suggestionRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };
    
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [showAddForm]);

  const fetchWarranties = async (url = '/api/warranties/') => {
    setIsLoading(true);
    try {
      const response = await axios.get(url);
      
      if (response.data.results !== undefined) {
        setWarranties(response.data.results);
        setPagination({
          count: response.data.count,
          next: response.data.next,
          previous: response.data.previous
        });
      } else {
        setWarranties(response.data);
      }
      
      setError("");
    } catch (err) {
      console.error("Error fetching warranties:", err);
      setError("Failed to load warranties. Please check the console for details.");
    } finally {
      setIsLoading(false);
    }
  };

  const fetchProjectSuggestions = async (query) => {
    console.log("Fetching project suggestions for:", query);
    setIsLoadingSuggestions(true);
    
    try {
      // Use the correct API endpoint
      const response = await axios.get(`/api/project-autocomplete/?query=${query}`);
      console.log("Project suggestions response:", response.data);
      
      if (response.data && response.data.length > 0) {
        setProjectSuggestions(response.data);
        setShowSuggestions(true);
      } else {
        setProjectSuggestions([]);
        setShowSuggestions(false);
      }
    } catch (err) {
      console.error("Error fetching project suggestions:", err);
      setProjectSuggestions([]);
    } finally {
      setIsLoadingSuggestions(false);
    }
  };

  const handleProjectInputChange = (e) => {
    const value = e.target.value;
    setNewWarranty(prev => ({ ...prev, project_id: value }));
    
    if (value.length >= 2) {
      fetchProjectSuggestions(value);
    } else {
      setProjectSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const handleProjectSelect = (projectId) => {
    setNewWarranty(prev => ({ ...prev, project_id: projectId }));
    setShowSuggestions(false);
  };

  const handleCheckboxChange = (warrantyId) => {
    setSelectedWarranties(prev => {
      if (prev.includes(warrantyId)) {
        return prev.filter(id => id !== warrantyId);
      } else {
        return [...prev, warrantyId];
      }
    });
  };

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      const allIds = warranties.map(warranty => warranty.project_warranty_id);
      setSelectedWarranties(allIds);
    } else {
      setSelectedWarranties([]);
    }
  };

  const handleDeleteWarranties = async () => {
    if (selectedWarranties.length === 0) {
      setError("Please select at least one warranty to delete");
      return;
    }

    try {
      await axios.delete('/api/warranties/bulk-delete/', {
        data: { ids: selectedWarranties }
      });
      
      setWarranties(prev => prev.filter(
        warranty => !selectedWarranties.includes(warranty.project_warranty_id)
      ));
      setSelectedWarranties([]);
      setError("");
    } catch (err) {
      console.error("Error deleting warranties:", err);
      setError("Failed to delete warranties. Please try again.");
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewWarranty(prev => ({
      ...prev,
      [name]: value
    }));
    
    if (name === "warranty_start_date" || name === "warranty_coverage_yr") {
      const startDate = new Date(name === "warranty_start_date" ? value : newWarranty.warranty_start_date);
      const years = parseInt(name === "warranty_coverage_yr" ? value : newWarranty.warranty_coverage_yr);
      
      if (!isNaN(startDate.getTime()) && !isNaN(years)) {
        const endDate = new Date(startDate);
        endDate.setFullYear(endDate.getFullYear() + years);
        
        setNewWarranty(prev => ({
          ...prev,
          warranty_end_date: endDate.toISOString().split('T')[0]
        }));
      }
    }
  };

  const handleAddWarranty = async (e) => {
    e.preventDefault();
    
    try {
      console.log("Sending warranty data:", newWarranty);
      
    const formattedWarranty = {
      ...newWarranty,
      warranty_start_date: newWarranty.warranty_start_date, // Should be in YYYY-MM-DD format
      warranty_end_date: newWarranty.warranty_end_date,     // Should be in YYYY-MM-DD format
      warranty_coverage_yr: parseInt(newWarranty.warranty_coverage_yr)
    };
      
      console.log("Formatted warranty data:", formattedWarranty);
      
      const response = await axios.post('/api/warranties/', formattedWarranty);
      console.log("Add warranty response:", response.data);
      
      setWarranties(prev => [...prev, response.data]);
      
      setNewWarranty({
        project_id: "",
        warranty_coverage_yr: "1",
        warranty_start_date: "",
        warranty_end_date: ""
      });
      setShowAddForm(false);
      setError("");
    } catch (err) {
      console.error("Error adding warranty:", err);
      if (err.response && err.response.data) {
        console.error("Error details:", err.response.data);
        
        if (typeof err.response.data === 'object') {
          const errorMessages = Object.entries(err.response.data)
            .map(([field, errors]) => `${field}: ${errors.join(', ')}`)
            .join('; ');
          setError(`Failed to add warranty: ${errorMessages}`);
        } else {
          setError(`Failed to add warranty: ${err.response.data}`);
        }
      } else {
        setError("Failed to add warranty. Please check your inputs.");
      }
    }
  };

  const handleNextPage = () => {
    if (pagination.next) {
      fetchWarranties(pagination.next);
    }
  };

  const handlePreviousPage = () => {
    if (pagination.previous) {
      fetchWarranties(pagination.previous);
    }
  };

  const handleDragStart = (e, projectId) => {
    e.dataTransfer.setData("text/plain", projectId);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const projectId = e.dataTransfer.getData("text/plain");
    setNewWarranty(prev => ({ ...prev, project_id: projectId }));
    setIsDragging(false);
    e.target.classList.remove('drag-over');
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.target.classList.add('drag-over');
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.target.classList.remove('drag-over');
    setIsDragging(false);
  };

  const handleFocus = () => {
    if (newWarranty.project_id.length >= 2) {
      fetchProjectSuggestions(newWarranty.project_id);
    }
  };

  return (
    <div className="body-content-container">
      <div className="warrantymonitoring">
        <b>Warranties</b>
      </div>
      
      <div className="warranty-actions">
        <button className="add-warranty" onClick={() => setShowAddForm(!showAddForm)}>
          <b>{showAddForm ? "Cancel" : "Add Warranty"}</b>
        </button>
        <button className="delproj" onClick={handleDeleteWarranties}>
          <b>Delete Selected</b>
        </button>
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      {showAddForm && (
        <div className="add-warranty-form" ref={formRef}>
          <h3>Add New Warranty</h3>
          <form onSubmit={handleAddWarranty}>
            <div className="form-group">
              <label>Project ID:</label>
              <div className="autocomplete-container" ref={suggestionRef}>
                <input 
                  type="text" 
                  name="project_id" 
                  value={newWarranty.project_id} 
                  onChange={handleProjectInputChange}
                  onFocus={handleFocus}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragEnter={handleDragEnter}
                  onDragLeave={handleDragLeave}
                  className={`draggable-input ${isDragging ? 'drag-over' : ''}`}
                  placeholder="Type or drag a project ID here"
                  required 
                />
                <div className="input-tooltip">
                  Type to search for projects or drag from below
                </div>
                
                {isLoadingSuggestions && (
                  <div className="suggestions-loading">Loading projects...</div>
                )}
                
                {showSuggestions && projectSuggestions.length > 0 && (
                  <ul className="suggestions-list">
                    {projectSuggestions.map((project, index) => (
                      <li 
                        key={index} 
                        onClick={() => handleProjectSelect(project.project_id)}
                        className="suggestion-item"
                      >
                        <strong>{project.project_id}</strong>
                        {project.project_name && <span> - {project.project_name}</span>}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
            <div className="form-group">
              <label>Warranty Coverage (Years):</label>
              <input 
                type="number" 
                name="warranty_coverage_yr" 
                value={newWarranty.warranty_coverage_yr} 
                onChange={handleInputChange} 
                min="1"
                required 
              />
            </div>
            <div className="form-group">
              <label>Start Date:</label>
              <input 
                type="date" 
                name="warranty_start_date" 
                value={newWarranty.warranty_start_date} 
                onChange={handleInputChange} 
                required 
              />
            </div>
            <div className="form-group">
              <label>End Date:</label>
              <input 
                type="date" 
                name="warranty_end_date" 
                value={newWarranty.warranty_end_date} 
                onChange={handleInputChange} 
                required 
              />
            </div>
            <button type="submit" className="submit-btn">Add Warranty</button>
          </form>
        </div>
      )}
      
      {isLoading ? (
        <div className="loading">Loading warranties...</div>
      ) : (
        <>
          <div className="warrantytable">
            <table className="warrantytable1">
              <thead>
                <tr>
                  <th>
                    <input 
                      type="checkbox" 
                      onChange={handleSelectAll} 
                      checked={selectedWarranties.length === warranties.length && warranties.length > 0}
                    />
                  </th>
                  <th><b>Warranty ID</b></th>
                  <th><b>Project ID</b></th>
                  <th><b>Warranty Coverage Yr.</b></th>
                  <th><b>Start Date</b></th>
                  <th><b>End Date</b></th>
                </tr>
              </thead>
              <tbody>
                {warranties.length > 0 ? (
                  warranties.map((warranty) => (
                    <tr key={warranty.project_warranty_id}>
                      <td>
                        <input 
                          type="checkbox" 
                          checked={selectedWarranties.includes(warranty.project_warranty_id)} 
                          onChange={() => handleCheckboxChange(warranty.project_warranty_id)} 
                        />
                      </td>
                      <td><b>{warranty.project_warranty_id}</b></td>
                      <td 
                        draggable 
                        onDragStart={(e) => handleDragStart(e, warranty.project_id)}
                        className="draggable-cell"
                        title="Drag this project ID to the form"
                      >
                        {warranty.project_id}
                      </td>
                      <td>{warranty.warranty_coverage_yr}</td>
                      <td>{warranty.warranty_start_date}</td>
                      <td>{warranty.warranty_end_date}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="no-data">No warranties found</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          
          {(pagination.next || pagination.previous) && (
            <div className="pagination-controls">
              <button 
                onClick={handlePreviousPage} 
                disabled={!pagination.previous}
                className="pagination-button"
              >
                Previous
              </button>
              <span className="pagination-info">
                Showing {warranties.length} of {pagination.count} warranties
              </span>
              <button 
                onClick={handleNextPage} 
                disabled={!pagination.next}
                className="pagination-button"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default BodyContent;