function init() {
    return {
        executions: [],
        steps: null,
        selectedStep: null,
        selectedId:null,
       
        async loadList() {
            console.log('Loading List');
            var result = await (await fetch('/api/crud/listAllExecutions')).json();
            console.log(result);
            this.executions= result;
        }, 

        async loadSteps(executionId) {
            console.log('Loading Steps');
            this.selectedId = executionId;
            var result = await (await fetch(`/api/crud/listExecutionSteps/${executionId["$oid"]}`)).json();
            this.steps = result.workflow.wf;
            this.selectedStep = null;
        },



    }
}