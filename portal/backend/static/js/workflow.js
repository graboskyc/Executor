function init() {
    return {
        workflow: {},
        allTemplates: [],
       
        async loadList() {
            console.log('Loading List');
            var id = this.getQueryVariable("_id");
            this.workflow= await (await fetch('/api/crud/getWorkflow/'+id)).json();
            this.allTemplates= await (await fetch('/api/crud/listAllTemplate')).json();
        }, 

        async saveWorkflow() {
            console.log('Saving');
            var id = this.getQueryVariable("_id");
            await fetch('/api/crud/saveWorkflow/'+id, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.workflow)
            });
        },

        async appendWf(t) {
            this.workflow.wf.push(t);
        },

        getQueryVariable(variable) {
            var query = window.location.search.substring(1);
            var vars = query.split("&");
            for (var i=0;i<vars.length;i++) {
              var pair = vars[i].split("=");
              if (pair[0] == variable) {
                return pair[1];
              }
            } 
        }


    }
}