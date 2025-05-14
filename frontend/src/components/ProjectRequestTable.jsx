import React from 'react';
import './ProjectRequestTable.css';

const ProjectRequestTable = ({ data, onActionClick }) => {
    return (
        <table className="project-requests-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>PROJECT NAME</th>
                    <th>APPROVAL ID</th>
                    <th>ITEM ID</th>
                    <th>START DATE</th>
                    <th>STATUS</th>
                    <th>ACTIONS</th>
                </tr>
            </thead>
            <tbody>
                {data.map((row, index) => (
                    <tr key={index}>
                        <td>{row.project_request_id}</td>
                        <td>{row.project_name}</td>
                        <td>{row.approval_id}</td>
                        <td>{row.item_id}</td>
                        <td>{row.start_date || 'N/A'}</td>
                        <td>{row.project_status}</td>
                        <td>
                            <button onClick={() => onActionClick(row.project_request_id)}>
                                Action
                            </button>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

export default ProjectRequestTable;