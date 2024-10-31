function init() {
    return {
        allTemplates: [],
        selectedTemplate: {title:"",engine:"python3",arguments:[], icon:"code"},
        newArgument: {key:"",friendlyName:""},
        

        async loadList() {
            console.log('Loading List');
            this.allTemplates= await (await fetch('/api/listAllTemplate')).json();
            console.log(this.foo);
        },

        async saveTemplate() {
            console.log('Saving Template');
            
            console.log(this.selectedTemplate);
            await fetch('/api/newTemplate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.selectedTemplate)
            });
            this.selectedTemplate= {title:"",engine:"python3",arguments:[], icon:"code"},
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