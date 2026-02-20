function init() {
    return {
        executions: [],
        steps: null,
        selectedStep: null,
        selectedId:null,
        charts: [],
        showOnlyErrored: false,
        stepsDebug: null,
       
        async loadList() {
            console.log('Loading List');
            if(this.showOnlyErrored) {
                var result = await (await fetch('/api/crud/listAllExecutions?errored_only=true')).json();
            } else {
                var result = await (await fetch('/api/crud/listAllExecutions')).json();
            }
            console.log(result);
            this.executions= result;
            var chartsResult = await (await fetch('/api/crud/getPageConfig/executions')).json();
            this.charts = chartsResult.charts;
        }, 

        async loadSteps(executionId) {
            console.log('Loading Steps');
            this.selectedId = executionId;
            var result = await (await fetch(`/api/crud/listExecutionSteps/${executionId["$oid"]}`)).json();
            this.steps = result.workflow.wf;
            var debugResult = await (await fetch(`/api/crud/getExecutionDebug/${executionId["$oid"]}`)).json();
            if(debugResult.url) {
                this.stepsDebug = debugResult.url;
            }
            this.selectedStep = null;
        },

        async retryExecution(executionId) {
            console.log('Retrying Execution');
            var result = await (await fetch(`/api/exec/retryExecution/${executionId}`)).json();
            console.log(result);
            this.loadList();
        }
    }
}