async function getWithAuthAlert(url) {
    var response = await fetch(url);
    if (response.status === 401 || response.status === 403) {
        alert("You are not logged in or in the correct group.");
    } else {
        return response;
    }
}

function init() {
    return {
        workflows: [],
       
        async loadList() {
            console.log('Loading List');
            this.workflows = await (await getWithAuthAlert('/api/crud/listAllWorkflows')).json();
        }, 

        async newWorkflow() {
            console.log('New Workflow');
            var retVal = await (await fetch('/api/crud/newWorkflow')).json();
            window.location = "/workflow.html?_id="+retVal._id.$oid;
        }, 


    }
}