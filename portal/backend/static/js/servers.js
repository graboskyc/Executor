function init() {
    return {
        servers: [],
        currentServers: [],
        oldServers: [],
       
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
            // if the servrs have been seen in last 2 hours, it is current, otherwise it is old
            this.currentServers = this.servers.filter(s => { 
                const lastSeen = new Date(s.lastSeen.$date);
                const now = new Date();
                const diffMs = now - lastSeen;
                const diffHours = diffMs / (1000 * 60 * 60);
                return diffHours <= 2;
            });
            this.oldServers = this.servers.filter(s => { 
                const lastSeen = new Date(s.lastSeen.$date);
                const now = new Date();
                const diffMs = now - lastSeen;
                const diffHours = diffMs / (1000 * 60 * 60);
                return diffHours > 2;
            });
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