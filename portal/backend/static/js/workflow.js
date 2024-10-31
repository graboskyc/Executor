function init() {
    return {
        workflow: {},
        allTemplates: [],
        openModal: false,
        selectedTemplate: {},
        oldSelectedTemplate:{},
       
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
            alert("Saved!");
        },

        async exeWorkflow() {
            await this.saveWorkflow();
            console.log('Executing');
            var id = this.getQueryVariable("_id");
            await fetch('/api/exec/enqueueWorkflow/'+id, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            alert("Enqueued!");
        },

        async appendWf(t) {
            this.workflow.wf.push(t);
        },

        async editTask(t) {
            this.selectedTemplate = t;
            this.oldSelectedTemplate = t; 
            this.openModal = true;
        },

        async saveTask() {
            this.workflow.wf.forEach(element => {
                if(element == this.oldSelectedTemplate) {
                    element = this.selectedTemplate;
                }
            });
            this.selectedTemplate = {};
            this.oldSelectedTemplate = {};
            this.openModal = false;
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