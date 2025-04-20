import React, { useState } from "react";
import "../styles/Projectrequest.css";

const BodyContent = () => {
  const [newInternalprojectname, setNewInternalprojectname] = useState("");
  const [newInternalrequestdate, setNewInternalrequestdate] = useState("");
  const [newInternalstartingdate, setNewInternalstartingdate] = useState("");
  const [newInternalemployeeid, setNewInternalemployeeid] = useState("");
  const [newInternaldepartmentid, setNewInternaldepartmentid] = useState("");
  const [newInternalbudgetrequest, setNewInternalbudgetrequest] = useState("");
  const [newInternalbudgetdescription, setNewInternalbudgetdescription] = useState("");
  const [newInternalprojectdescription, setNewInternalprojectdescription] = useState("");
  const [showReportList, setShowReportList] = useState(false);
  const [currentForm, setCurrentForm] = useState(1);
  const [reportData, setReportData] = useState([]);
  const [selectedReports, setSelectedReports] = useState([]);

  const handleFirstSubmitprojrequest = (e) => {
    e.preventDefault();
    const newData = {
      Internalprojectname: newInternalprojectname,
      Internalrequestdate: newInternalrequestdate,
      Internalstartingdate: newInternalstartingdate,
      Internalemployeeid: newInternalemployeeid,
      Internaldepartmentid: newInternaldepartmentid,
      Internalbudgetrequest: newInternalbudgetrequest,
      Internalbudgetdescription: newInternalbudgetdescription,
    Internalprojectdescription: newInternalprojectdescription,
    };
    console.log("New Report Data:", newData);
    setReportData([...reportData, newData]);
    setShowReportList(true);
    setCurrentForm(null);
    setNewInternalprojectname("");
    setNewInternalrequestdate("");
    setNewInternalstartingdate("");
    setNewInternalemployeeid("");
    setNewInternaldepartmentid("");
    setNewInternalbudgetrequest("");
    setNewInternalbudgetdescription(""),
    setNewInternalprojectdescription("")
  };

  const handleBackClick = () => {
    setShowReportList(false);
    setCurrentForm(1);
  };

  const handleRemoveReports = () => {
    const newReportData = reportData.filter((_, index) => !selectedReports.includes(index));
    setReportData(newReportData);
    setSelectedReports([]);
  };

  const handleCheckboxChange = (index) => {
    if (selectedReports.includes(index)) {
      setSelectedReports(selectedReports.filter((i) => i !== index));
    } else {
      setSelectedReports([...selectedReports, index]);
    }
  };

  return (
    <div className="body-content-container5">
      {currentForm === 1 && (
        <form onSubmit={handleFirstSubmitprojrequest}>
          <h1 className="newreport">
            <b>Internal Project Request</b>
          </h1>
          <label className="projectnamereq">
            <b>Project Name</b>
          </label>
          <br />
          <input
            className="projectnamereq2"
            type="text"
            placeholder="Enter Project Name"
            value={newInternalprojectname}
            onChange={(e) => setNewInternalprojectname(e.target.value)}
            required
          />
          <br />

          <label className="requestdateprojreq">
            <b>Request Date</b>
          </label>
          <br />
          <input
            className="requestdateprojreq2"
            type="date"
            placeholder="00/00/0000"
            value={newInternalrequestdate}
            onChange={(e) => setNewInternalrequestdate(e.target.value)}
            required
          />
          <br />

          <label className="startingreqdate">
            <b>Starting Date</b>
          </label>
          <br />
          <input
            className="startingreqdate2"
            type="date"
            placeholder="00/00/0000"
            value={newInternalstartingdate}
            onChange={(e) => setNewInternalstartingdate(e.target.value)}
            required
          />
          <br />

          <label className="employeeidreq">
            <b>Employee ID</b>
          </label>
          <br />
          <input
            className="employeeidreq2"
            type="text"
            placeholder="Insert Employee ID"
            value={newInternalemployeeid}
            onChange={(e) => setNewInternalemployeeid(e.target.value)}
            required
          />
          <br />

          <label className="deptidreq">
            <b>Department ID</b>
          </label>
          <br />
          <input
            className="deptidreq2"
            type="text"
            placeholder="Insert Department ID"
            value={newInternaldepartmentid}
            onChange={(e) => setNewInternaldepartmentid(e.target.value)}
            required
          />
          <br />

          <label className="budgetreq3">
            <b>Budget Request</b>
          </label>
          <br />
          <input
            className="budgetreq4"
            type="number"
            placeholder="Add Budget"
            value={newInternalbudgetrequest}
            onChange={(e) => setNewInternalbudgetrequest(e.target.value)}
            required
          />
          <br />

          <label className="budgetdescription">
            <b>Budget Description</b>
          </label>
          <br />
          <input
            className="budgetdescription2"
            type="text"
            placeholder="Add Description"
            value={newInternalbudgetdescription}
            onChange={(e) => setNewInternalbudgetdescription(e.target.value)}
            required
          />
          <br />

          <label className="projectdescriptionint">
            <b>Project Description</b>
          </label>
          <br />
          <input
            className="projectdescriptionint2"
            type="text"
            placeholder="Add Description"
            value={newInternalprojectdescription}
            onChange={(e) => setNewInternalprojectdescription(e.target.value)}
            required
          />
          <br />
        <div className="intrequestsavebutton"> 
          <button type="submit" className="saverep">
            <b>Save</b>
          </button>
          <button className="editrep">
            <b>Edit</b>
          </button>
          </div>
          <button className="attachfile">
            <b>Attachfile</b>
          </button>
          <h1 className="attach2">
            <b>Attachments</b>
          </h1>
        </form>
      )}

      {showReportList && (
        <>
          <h1 className="internalrequestlist">
            <b>Internal Request Monitoring</b>
          </h1>
          <button onClick={handleBackClick} className="addreport">
            <b>Add Request</b>
          </button>
          <button onClick={handleRemoveReports} className="removereport">
            <b>Remove Request</b>
          </button>
          <div className="replisttable1">
            <table className="replist">
              <thead>
                <tr>
                  <th>
                    <input type="checkbox" disabled />
                  </th>
                  <th>
                    <b>Project Name</b>
                  </th>
                  <th>
                    <b>Request Date</b>
                  </th>
                  <th>
                    <b>Starting Date</b>
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
                {reportData.map((item, index) => (
                  <tr key={index}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedReports.includes(index)}
                        onChange={() => handleCheckboxChange(index)}
                      />
                    </td>
                    <td>
                      <b>{item.Internalprojectname}</b>
                    </td>
                    <td>{item.Internalrequestdate}</td>
                    <td>{item.Internalstartingdate}</td>
                    <td>{item.Internalemployeeid}</td>
                    <td>{item.Internaldepartmentid}</td>
                    <td>{item.Internalbudgetrequest}</td>
                    <td>{item.Internalbudgetdescription}</td>
                    <td>{item.Internalprojectdescription}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {!showReportList && currentForm !== 1 && (
        <div>
          <button onClick={() => setShowReportList(true)}>View Report List</button>
        </div>
      )}
    </div>
  );
};

export default BodyContent;