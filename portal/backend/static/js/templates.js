function init() {
    return {
        allTemplates: [],
        selectedTemplate: {},
        newArgument: {key:"",friendlyName:""},
        file: null,

        defaultList() {
            this.selectedTemplate= {title:"",engine:"python3",arguments:[], icon:"code", revision:1};
            this.file = null;
        },

        async loadList() {
            this.defaultList();
            console.log('Loading List');
            this.allTemplates= await (await getWithAuthAlert('/api/crud/listAllTemplate')).json();
        },

        async saveTemplate() {
            console.log(this.selectedTemplate);
            this.selectedTemplate.revision = this.selectedTemplate.revision + 1;
            var data = new FormData()
            if(this.file != null){
                data.append('file', this.file[0])
            }
            data.append('template', JSON.stringify(this.selectedTemplate))
            if("_id" in this.selectedTemplate) {
                console.log('Saving Template');
                var id = this.selectedTemplate._id.$oid;
                await fetch('/api/crud/saveTemplate/'+id, {
                    method: 'PUT',
                    body: data
                });
                alert('Template saved successfully!');
            } else {
                console.log('Creating Template');
                await fetch('/api/crud/newTemplate', {
                    method: 'POST',
                    body: data
                });
                this.defaultList();
                alert('Template created successfully!');
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

        async handleFileSelect(files) {
            if (!files || files.length === 0) return;
            this.file = files;
            
            try {
                const zip = await JSZip.loadAsync(files[0]);
                const manifestFile = zip.file('manifest.json');
                
                if (manifestFile) {
                    const manifestContent = await manifestFile.async('string');
                    const manifest = JSON.parse(manifestContent);
                    
                    // Fill form values from manifest
                    if (manifest.title) this.selectedTemplate.title = manifest.title;
                    if (manifest.engine) this.selectedTemplate.engine = manifest.engine;
                    if (manifest.icon) this.selectedTemplate.icon = manifest.icon;
                    if (manifest.link) this.selectedTemplate.link = manifest.link;
                    if (manifest.revision) this.selectedTemplate.revision = manifest.revision;
                    if (manifest.arguments && Array.isArray(manifest.arguments)) {
                        this.selectedTemplate.arguments = manifest.arguments;
                    }
                    
                    console.log('Manifest loaded:', manifest);
                }
            } catch (e) {
                console.error('Error reading zip or manifest:', e);
            }
        },


    }
}