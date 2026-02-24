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