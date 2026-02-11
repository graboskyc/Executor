function init() {
    return {
        servers: [],
       
        minutesAgo(dateStr) {
            const date = new Date(dateStr);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            return diffMins + ' min ago';
        },

        async loadList() {
            console.log('Loading List');
            var result = await (await fetch('/api/exec/servers')).json();
            //console.log(result);
            this.servers= result;
        }, 

        async updateServer(server) {
            console.log('Updating server', server);
            await fetch('/api/exec/updateServer', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({name: server._id, nextPoll: parseInt(server.nextPoll)})
            });
            alert('Server updated successfully');
        }

    }
}