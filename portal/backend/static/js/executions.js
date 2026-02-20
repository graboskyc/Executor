function init() {
    return {
        executions: [],
        steps: null,
        selectedStep: null,
        selectedId:null,
        charts: [],
        showOnlyErrored: false,
        stepsDebug: null,
        originalId: null,
       
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
            //console.log(executionId);
            this.selectedId = executionId;
            // Highlight the selected execution LI
            setTimeout(() => {
                // Remove highlight from all execution LIs
                document.querySelectorAll('li[id^="execution-"]').forEach(li => {
                    li.style.background = '';
                });
                document.querySelectorAll('li[id^="step-"]').forEach(li => {
                    li.style.background = '';
                });
                // Add highlight to the selected LI
                const selectedLi = document.getElementById('execution-' + (typeof executionId === 'object' && executionId.$oid ? executionId.$oid : executionId));
                if(selectedLi) {
                    selectedLi.style.background = '#a5d601'; 
                }
            }, 100);
            var result = await (await fetch(`/api/crud/listExecutionSteps/${executionId["$oid"]}`)).json();
            this.steps = result.workflow.wf;
            // if there isRetry:true, then show button to parent
            if (result.isRetry) {
                this.originalId = result.originalId;
            } else {
                this.originalId = null;
            }
            var debugResult = await (await fetch(`/api/crud/getExecutionDebug/${executionId["$oid"]}`)).json();
            if(debugResult.url) {
                this.stepsDebug = debugResult.url;
            }
            this.selectedStep = null;
        },

        async setSelectedStep(step) {
            this.selectedStep = step;
            // Highlight the selected step LI
            setTimeout(() => {
                // Remove highlight from all step LIs
                document.querySelectorAll('li[id^="step-"]').forEach(li => {
                    li.style.background = '';
                });
                // Add highlight to the selected LI
                if(step && step._id && step._id.$oid) {
                    const selectedLi = document.getElementById('step-' + step._id.$oid);
                    if(selectedLi) {
                        selectedLi.style.background = '#a5d601'; // light yellow
                    }
                }
            }, 100);
        },

        async retryExecution(executionId) {
            console.log('Retrying Execution');
            var result = await (await fetch(`/api/exec/retryExecution/${executionId}`)).json();
            console.log(result);
            this.loadList();
        }
    }
}