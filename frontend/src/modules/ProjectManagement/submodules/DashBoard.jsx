import React, { useState } from 'react';
import "../styles/DashBoard.css";

const BodyContent = () => {
  const [data, setData] = useState([
    { Overdue: '10days', Task: 'Get out Of Biome 1', Deadline: '00/00/0000', Employee: 'S.vassos' },
    { Overdue: '21days', Task: 'none', Deadline: '00/00/0000', Employee: 'none' },
    { Overdue: '12days', Task: 'none', Deadline: '00/00/0000', Employee: 'none' },
    { Overdue: '5days', Task: 'Another Task', Deadline: '01/01/2024', Employee: 'User 1' },
    { Overdue: '30days', Task: 'Yet Another Task', Deadline: '02/02/2024', Employee: 'User 2' },
    { Overdue: '1day', Task: 'Quick Task', Deadline: '03/03/2024', Employee: 'User 3' },
    { Overdue: '15days', Task: 'Long Task', Deadline: '04/04/2024', Employee: 'User 4' },
    { Overdue: '2days', Task: 'Short Task', Deadline: '05/05/2024', Employee: 'User 5' },
    { Overdue: '', Task: '', Deadline: '', Employee: '' },
    { Overdue: '', Task: '', Deadline: '', Employee: '' },
    { Overdue: '', Task: '', Deadline: '', Employee: '' },
    { Overdue: '', Task: '', Deadline: '', Employee: '' },
    { Overdue: '', Task: '', Deadline: '', Employee: '' },
    { Overdue: '', Task: '', Deadline: '', Employee: '' },
    { Overdue: '', Task: '', Deadline: '', Employee: '' },
  ]);

  const [dataExternal, setDataExternal] = useState([
    { ProjectTrackingID: '0000', ProjectID: '0000', ProjectMilestone: 'None', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectWarrantyStatus: 'None', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', ProjectMilestone: 'None', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectWarrantyStatus: 'None', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', ProjectMilestone: 'None', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectWarrantyStatus: 'None', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', ProjectMilestone: 'None', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectWarrantyStatus: 'None', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', ProjectMilestone: 'None', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectWarrantyStatus: 'None', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', ProjectMilestone: 'None', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectWarrantyStatus: 'None', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', ProjectMilestone: 'None', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectWarrantyStatus: 'None', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', ProjectMilestone: 'None', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectWarrantyStatus: 'None', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', ProjectMilestone: 'None', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectWarrantyStatus: 'None', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', ProjectMilestone: 'None', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectWarrantyStatus: 'None', ProjectIssue: '' },
  ]);

  const [dataInternal, setDataInternal] = useState([
    { ProjectTrackingID: '0000', ProjectID: '0000', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectIssue: '' },
    { ProjectTrackingID: '0000', ProjectID: '0000', StartDate: '00/00/0000', EstimatedEndDate: '00/00/0000', ProjectIssue: '' },
  ]);

  const [selectedNav3, setSelectedNav3] = useState('All3');
  const [selectedNav2, setSelectedNav2] = useState('Internal Project');
  const [showAddProjectForm, setShowAddProjectForm] = useState(false);
  const [selectedNavplan, setSelectedNavplan] = useState("External");

  
  const [newProjectIDExternal, setNewProjectIDExternal] = useState("");
  const [selectedProjectMilestoneExternal, setSelectedProjectMilestoneExternal] = useState("");
  const [newStartDateExternal, setNewStartDateExternal] = useState("");
  const [newEndDateExternal, setNewEndDateExternal] = useState("");
  const [newProjectIssueExternal, setNewProjectIssueExternal] = useState("");
  const [newProjectWarrantyIDExternal, setNewProjectWarrantyIDExternal] = useState("");

  const [newProjectIDInternal, setNewProjectIDInternal] = useState("");
  const [newStartDateInternal, setNewStartDateInternal] = useState("");
  const [newEndDateInternal, setNewEndDateInternal] = useState("");
  const [newProjectIssueInternal, setNewProjectIssueInternal] = useState("");

  const handleNavClickdash = (nav) => {
    setSelectedNavplan(nav);
  };

  const handleNavClick = (navItem) => {
    setSelectedNav2(navItem);
  };

  const handleNavClick2 = (navItem) => {
    setSelectedNav3(navItem);
  };

  const handleAddProjectClick = () => {
    setShowAddProjectForm(true);
  };

  const handleAddExternalProject = (e) => {
    e.preventDefault();
    const newProject = {
      ProjectTrackingID: dataExternal.length + 1,
      ProjectID: newProjectIDExternal,
      ProjectMilestone: selectedProjectMilestoneExternal,
      StartDate: newStartDateExternal,
      EstimatedEndDate: newEndDateExternal,
      ProjectWarrantyStatus: newProjectWarrantyIDExternal,
      ProjectIssue: newProjectIssueExternal,
    };
    setDataExternal([...dataExternal, newProject]);
    setShowAddProjectForm(false);
    setNewProjectIDExternal("");
    setSelectedProjectMilestoneExternal("");
    setNewStartDateExternal("");
    setNewEndDateExternal("");
    setNewProjectWarrantyIDExternal("");
    setNewProjectIssueExternal("");
  };

  const handleAddInternalProject = (e) => {
    e.preventDefault();
    const newProject = {
      ProjectTrackingID: dataInternal.length + 1,
      ProjectID: newProjectIDInternal,
      StartDate: newStartDateInternal,
      EstimatedEndDate: newEndDateInternal,
      ProjectIssue: newProjectIssueInternal,
    };
    setDataInternal([...dataInternal, newProject]);
    setShowAddProjectForm(false);
    setNewProjectIDInternal("");
    setNewStartDateInternal("");
    setNewEndDateInternal("");
    setNewProjectIssueInternal("");
  };

  const handleCancelAddProject = () => {
    setShowAddProjectForm(false);
    setNewProjectIDExternal("");
    setSelectedProjectMilestoneExternal("");
    setNewStartDateExternal("");
    setNewEndDateExternal("");
    setNewProjectWarrantyIDExternal("");
    setNewProjectIssueExternal("");
    setNewProjectIDInternal("");
    setNewStartDateInternal("");
    setNewEndDateInternal("");
    setNewProjectIssueInternal("");
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
                {data.map((item, index) => (
                  <tr key={index}>
                    <td className="due"><b>{item.Overdue}</b></td>
                    <td>{item.Task}</td>
                    <td>{item.Deadline}</td>
                    <td>{item.Employee}</td>
                  </tr>
                ))}
              </tbody>
            </table>
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
                  {dataExternal.map((item, index) => (
                    <tr key={index}>
                      <td>{item.ProjectTrackingID}</td>
                      <td><b>{item.ProjectID}</b></td>
                      <td>{item.ProjectMilestone}</td>
                      <td>{item.StartDate}</td>
                      <td>{item.EstimatedEndDate}</td>
                      <td>{item.ProjectWarrantyStatus}</td>
                      <td>{item.ProjectIssue}</td>
                    </tr>
                  ))}
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
                  {dataInternal.map((item, index) => (
                    <tr key={index}>
                      <td>{item.ProjectTrackingID}</td>
                      <td><b>{item.ProjectID}</b></td>
                      <td>{item.StartDate}</td>
                      <td>{item.EstimatedEndDate}</td>
                      <td>{item.ProjectIssue}</td>
                    </tr>
                  ))}
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
                          <input type="checkbox" id="docu1" name="docu1" value="documents1" />
                          <label htmlFor="docu1">Get Prescription Pads for Vicodin</label>
                          <br />
                          <input type="checkbox" id="docu2" name="docu2" value="documents2" />
                          <label htmlFor="docu2">Create a user flow of non-creational drugs</label>
                          <br />
                          <input type="checkbox" id="docu3" name="docu3" value="documents3" />
                          <label htmlFor="docu3">Buy Methylamine in Guadalajara</label>
                          <br />
                          <input type="checkbox" id="docu4" name="docu4" value="documents4" />
                          <label htmlFor="docu4">Start a coup</label>
                          <br />
                          <input type="checkbox" id="docu5" name="docu5" value="documents5" />
                          <label htmlFor="docu5">Prototype Meth Empire Blueprint</label>
                          <br />
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
              <form onSubmit={handleAddExternalProject}>
                <label className="projectiddash">
                  <b>Project ID*</b>
                </label>
                <br />
                <input className="projectiddash2"
                  type="text"
                  placeholder="Name"
                  value={newProjectIDExternal}
                  onChange={(e) => setNewProjectIDExternal(e.target.value)}
                  required
                />
                <br />

                <label className="projectmilestone"><b>Project Milestone</b></label>
                <br />
                <select
                  name="projectmilestone2"
                  className="projectmilestone2"
                  value={selectedProjectMilestoneExternal}
                  onChange={(e) => setSelectedProjectMilestoneExternal(e.target.value)}
                  required
                >
                  <option value="">Choose Project Milestone</option>
                  <option value="Project Initiation Completed">Project Initiation Completed</option>
                  <option value="Project Initiation Ongoing">Project Initiation Ongoing</option>
                  <option value="Project Initiation Rejected">Project Initiation Rejected</option>
                </select>
                <br />

                <label className="startdatedash">
                  <b>Start Date</b>
                </label>
                <br />
                <input
                  className="startdatedash2"
                  type="date"
                  placeholder="00/00/0000"
                  value={newStartDateExternal}
                  onChange={(e) => setNewStartDateExternal(e.target.value)}
                  required
                />
                <br />

                <label className="estenddatedash">
                  <b>Est. End Date</b>
                </label>
                <br />
                <input
                  className="estenddatedash2"
                  type="date"
                  placeholder="00/00/0000"
                  value={newEndDateExternal}
                  onChange={(e) => setNewEndDateExternal(e.target.value)}
                  required
                />
                <br />

                <label className="projectwarrantyiddash">
                  <b>Project Warranty ID</b>
                </label>
                <br />
                <input
                  className="projectwarrantyiddash2"
                  type="text"
                  placeholder="Insert Warranty ID"
                  value={newProjectWarrantyIDExternal}
                  onChange={(e) => setNewProjectWarrantyIDExternal(e.target.value)}
                  required
                />
                <br />

                <label className="projectissuedash">
                  <b>Project Issue</b>
                </label>
                <br />
                <input
                  className="projectissuedash2"
                  type="text"
                  placeholder="Add Project Issue:"
                  value={newProjectIssueExternal}
                  onChange={(e) => setNewProjectIssueExternal(e.target.value)}
                  required
                />
                <br />

                <button type="submit" className="Savedashboard"><b>Save</b></button>
                <button type="button" className="cancel" onClick={handleCancelAddProject}><b>Cancel</b></button>
              </form>
            </>
          )}

          {selectedNavplan === "Internal" && (
            <>
              <form onSubmit={handleAddInternalProject}>
                <label className="projectiddashint">
                  <b>Project ID*</b>
                </label>
                <br />
                <input className="projectiddashint2"
                  type="text"
                  placeholder="Name"
                  value={newProjectIDInternal}
                  onChange={(e) => setNewProjectIDInternal(e.target.value)}
                  required
                />
                <br />

                <label className="startdatedashint">
                  <b>Start Date</b>
                </label>
                <br />
                <input
                  className="startdatedashint2"
                  type="date"
                  placeholder="00/00/0000"
                  value={newStartDateInternal}
                  onChange={(e) => setNewStartDateInternal(e.target.value)}
                  required
                />
                <br />

                <label className="estenddatedashint">
                  <b>Est. End Date</b>
                </label>
                <br />
                <input
                  className="estenddatedashint2"
                  type="date"
                  placeholder="00/00/0000"
                  value={newEndDateInternal}
                  onChange={(e) => setNewEndDateInternal(e.target.value)}
                  required
                />
                <br />

                <label className="projectissuedash">
                  <b>Project Issue</b>
                </label>
                <br />
                <input
                  className="projectissuedash2"
                  type="text"
                  placeholder="Add Project Issue:"
                  value={newProjectIssueInternal}
                  onChange={(e) => setNewProjectIssueInternal(e.target.value)}
                  required
                />
                <br />

                <button type="submit" className="Savedashboard"><b>Save</b></button>
                <button type="button" className="cancel" onClick={handleCancelAddProject}><b>Cancel</b></button>
              </form>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default BodyContent;