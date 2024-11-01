function init() {
    return {
        workflow: {},
        allTemplates: [],
        openModal: false,
        selectedTemplate: {},
        oldSelectedTemplate:{},
        showToolbox:true,
        latestTemplateVersion:{},
       
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
            this.latestTemplateVersion = await (await fetch('/api/crud/getTemplate/'+t._id.$oid)).json();
            this.openModal = true;
        },

        async saveTask() {
            var i = this.workflow.wf.findIndex(x => x._id == this.selectedTemplate._id);
            console.log(i);
            this.workflow.wf[i] = this.selectedTemplate;
            this.selectedTemplate = {};
            this.oldSelectedTemplate = {};
            this.openModal = false;
        },

        async deleteTask() {
            let result = confirm("Are you sure you want to delete this task?");
            if (!result) {
                return;
            }
            this.workflow.wf = this.workflow.wf.filter((c) => c != this.selectedTemplate);
            this.selectedTemplate = {};
            this.oldSelectedTemplate = {};
            this.openModal = false;
        },

        async updateTask() {
            let result = confirm("Are you sure you want to update this task to the latest version? This cannot be reverted.");
            if (!result) {
                return;
            }
            this.latestTemplateVersion = await (await fetch('/api/crud/getTemplate/'+this.selectedTemplate._id.$oid)).json();
            var i = this.workflow.wf.findIndex(x => x._id == this.selectedTemplate._id);
            console.log(i);
            this.workflow.wf[i] = this.latestTemplateVersion;
            await this.saveWorkflow();
            this.selectedTemplate = {};
            this.oldSelectedTemplate = {};
            this.latestTemplateVersion = {};
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