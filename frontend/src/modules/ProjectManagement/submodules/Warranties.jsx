// Updated Warranties.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/Warranties.css";

const BodyContent = () => {
  const [warranties, setWarranties] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null
  });
  const [selectedWarranties, setSelectedWarranties] = useState([]);
  const [statusCounts, setStatusCounts] = useState({
    active: 0,
    expired: 0,
    pending: 0
  });

  useEffect(() => {
    fetchWarranties();
  }, []);

  useEffect(() => {
    // Calculate status counts whenever warranties change
    if (warranties.length > 0) {
      const counts = warranties.reduce((acc, warranty) => {
        const status = warranty.warranty_status?.toLowerCase() || '';
        if (status.includes('active')) acc.active++;
        else if (status.includes('expired')) acc.expired++;
        else acc.pending++;
        return acc;
      }, { active: 0, expired: 0, pending: 0 });
      
      setStatusCounts(counts);
    }
  }, [warranties]);

  const fetchWarranties = async (url = '/api/warranties/') => {
    setIsLoading(true);
    try {
      const response = await axios.get(url);
      
      if (response.data.results !== undefined) {
        const warrantiesWithNames = await Promise.all(
          response.data.results.map(async (warranty) => {
            try {
              const projectResponse = await axios.get(`/api/warranties/project-warranty-details/${warranty.project_id}/`);
              return {
                ...warranty,
                ext_project_name: projectResponse.data.project_name || `Project ${warranty.project_id}`,
                warranty_status: projectResponse.data.warranty_status || 'Pending'
              };
            } catch (error) {
              console.error(`Error fetching details for project ${warranty.project_id}:`, error);
              return {
                ...warranty,
                ext_project_name: `Project ${warranty.project_id}`,
                warranty_status: 'Pending'
              };
            }
          })
        );
        
        setWarranties(warrantiesWithNames);
        setPagination({
          count: response.data.count,
          next: response.data.next,
          previous: response.data.previous
        });
      } else {
        const warrantiesWithNames = await Promise.all(
          response.data.map(async (warranty) => {
            try {
              const projectResponse = await axios.get(`/api/warranties/project-warranty-details/${warranty.project_id}/`);
              return {
                ...warranty,
                ext_project_name: projectResponse.data.project_name || `Project ${warranty.project_id}`,
                warranty_status: projectResponse.data.warranty_status || 'Pending'
              };
            } catch (error) {
              return {
                ...warranty,
                ext_project_name: `Project ${warranty.project_id}`,
                warranty_status: 'Pending'
              };
            }
          })
        );
        
        setWarranties(warrantiesWithNames);
      }
      
      setError("");
    } catch (error) {
      console.error("Error fetching warranties:", error);
      setError("Failed to load warranties. Please check the console for details.");
    } finally {
      setIsLoading(false);
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

  const toggleWarrantySelection = (warrantyId) => {
    setSelectedWarranties(prev => {
      if (prev.includes(warrantyId)) {
        return prev.filter(id => id !== warrantyId);
      } else {
        return [...prev, warrantyId];
      }
    });
  };

  const removeSelected = () => {
    if (selectedWarranties.length === 0) return;
    
    // Filter out selected warranties
    setWarranties(prev => prev.filter(warranty => !selectedWarranties.includes(warranty.project_id)));
    setSelectedWarranties([]);
  };

  const getStatusClass = (status) => {
    const statusLower = status.toLowerCase();
    if (statusLower.includes('active')) return 'status-active';
    if (statusLower.includes('expired')) return 'status-expired';
    return 'status-pending';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  };

  return (
    <div className="body-content-container-warranty">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Warranty Management</h1>
      </div>
  
      {error && <div className="alert alert-error">{error}</div>}
      
      <div className="warranty-stats">
        <div className="stat-item">
          <span className="stat-value">{statusCounts.active}</span>
          <span className="stat-label">Active</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">{statusCounts.expired}</span>
          <span className="stat-label">Expired</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">{statusCounts.pending}</span>
          <span className="stat-label">Not Started</span>
        </div>
      </div>
        
      <div className="data-section">
        {isLoading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading warranties...</p>
          </div>
        ) : (
          <>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th><b>WARRANTY ID</b></th>
                    <th><b>PROJECT NAME</b></th>
                    <th><b>COVERAGE</b></th>
                    <th><b>START DATE</b></th>
                    <th><b>END DATE</b></th>
                    <th><b>STATUS</b></th>
                  </tr>
                </thead>
                <tbody>
                  {warranties.length > 0 ? (
                    warranties.map((warranty) => (
                      <tr key={warranty.project_id}>

                        <td className="warranty-id">
                          <span className="warranty-code">
                            WARR-{String(warranty.project_id).padStart(6, '0')}
                          </span>
                        </td>
                        <td>{warranty.ext_project_name || `Project ${warranty.project_id}`}</td>
                        <td>{warranty.warranty_coverage_yr || 'N/A'} {warranty.warranty_coverage_yr === 1 ? 'Year' : 'Years'}</td>
                        <td>{formatDate(warranty.warranty_start_date)}</td>
                        <td>{formatDate(warranty.warranty_end_date)}</td>
                        <td>
                          <span className={`status-badge ${getStatusClass(warranty.warranty_status)}`}>
                            {warranty.warranty_status || 'Pending'}
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7" className="no-data">
                        <div className="empty-state">
                          <span className="icon">📋</span>
                          <p>No warranties found</p>
                        </div>
                      </td>
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
                  className="pagination-btn"
                >
                  Previous
                </button>
                <div className="pagination-info">
                  Showing {warranties.length} of {pagination.count} warranties
                </div>
                <button 
                  onClick={handleNextPage} 
                  disabled={!pagination.next}
                  className="pagination-btn"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default BodyContent;