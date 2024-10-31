function init() {
    return {
        allTemplates: [],
        selectedTemplate: {},
        newArgument: {key:"",friendlyName:""},
        file: null,

        defaultList() {
            this.selectedTemplate= {title:"",engine:"python3",arguments:[], icon:"code"};
        },

        async loadList() {
            this.defaultList();
            console.log('Loading List');
            this.allTemplates= await (await fetch('/api/crud/listAllTemplate')).json();
        },

        async saveTemplate() {
            console.log(this.selectedTemplate);
            var data = new FormData()
            data.append('file', this.file[0])
            data.append('template', JSON.stringify(this.selectedTemplate))
            if("_id" in this.selectedTemplate) {
                console.log('Saving Template');
                var id = this.selectedTemplate._id.$oid;
                await fetch('/api/crud/saveTemplate/'+id, {
                    method: 'PUT',
                    body: data
                });
            } else {
                console.log('Creating Template');
                await fetch('/api/crud/newTemplate', {
                    method: 'POST',
                    body: data
                });
                this.defaultList();
            }
            await this.loadList();
        },

        async pushNewArgument() {
            console.log('Pushing new arg');
            if(this.newArgument.key.length > 0 && this.newArgument.friendlyName.length > 0) {
                this.selectedTemplate.arguments.push(this.newArgument);
                this.newArgument = {"key":"", "friendlyName":""};
            } else {
                alert("You must provide a key and friendly name for this argument!");
            }
        },

        delay(ms) {
            return new Promise(resolve => setTimeout(resolve, ms))
        },          


    }
}